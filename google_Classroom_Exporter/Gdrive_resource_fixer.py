import re
import os
import time
import csv
import argparse
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import mimetypes
from difflib import SequenceMatcher
from urllib.parse import urlparse, parse_qs
import io
from collections import defaultdict

# Configuration
HTML_FILE = 'source_index.html'
DOWNLOADS_FOLDER = 'downloads'
UPLOAD_FOLDER = 'uploaded_files'
CLASSROOM_FOLDER_NAME = 'classroom_Resource'
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
]
CHECKPOINT_INTERVAL = 10
MAX_RETRIES = 3
RETRY_DELAY = 5

# Google Workspace MIME types for conversion
GOOGLE_MIME_TYPES = {
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'application/vnd.google-apps.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'application/vnd.google-apps.spreadsheet',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'application/vnd.google-apps.presentation',
    'text/csv': 'application/vnd.google-apps.spreadsheet'
}

# Export MIME types for downloading Google Workspace files
EXPORT_MIME_TYPES = {
    'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.google-apps.drawing': 'image/png'
}

# File extensions for export types
EXPORT_EXTENSIONS = {
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
    'image/png': '.png',
    'application/pdf': '.pdf'
}

# File type mappings from HTML indicators
HTML_TYPE_TO_EXTENSIONS = {
    'google docs': ['.docx', '.doc', '.txt'],
    'google doc': ['.docx', '.doc', '.txt'],
    'pdf': ['.pdf'],
    'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv'],
    'google sheets': ['.xlsx', '.xls', '.csv'],
    'google sheet': ['.xlsx', '.xls', '.csv'],
    'google slides': ['.pptx', '.ppt'],
    'google slide': ['.pptx', '.ppt'],
    'document': ['.docx', '.doc', '.txt'],
    'spreadsheet': ['.xlsx', '.xls', '.csv'],
    'presentation': ['.pptx', '.ppt']
}

def normalize_filename(filename):
    """Normalize filename for better matching"""
    # Remove file extension and common variations
    name = os.path.splitext(filename)[0]
    # Remove special characters and normalize spaces
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', ' ', name).strip().lower()
    return name

def similarity_score(str1, str2):
    """Calculate similarity score between two strings"""
    return SequenceMatcher(None, str1, str2).ratio()

def extract_file_id(url):
    """Extract file ID from Google Drive URL"""
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]+)',
        r'/document/d/([a-zA-Z0-9_-]+)',
        r'/open\?id=([a-zA-Z0-9_-]+)',
        r'/spreadsheets/d/([a-zA-Z0-9_-]+)',
        r'/presentation/d/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def extract_file_type_from_html(link_element):
    """Extract file type indicator from HTML element context"""
    element_str = str(link_element)
    
    # Look for type indicators in the element and nearby elements
    type_indicators = []
    
    # Check for explicit type labels
    type_patterns = [
        r'Google Docs?',
        r'Google Sheets?',
        r'Google Slides?',
        r'PDF',
        r'Video',
        r'Document',
        r'Spreadsheet',
        r'Presentation'
    ]
    
    for pattern in type_patterns:
        if re.search(pattern, element_str, re.IGNORECASE):
            type_indicators.append(pattern.lower().replace('s', ''))  # Normalize
    
    # Check for MIME type in data attributes
    mime_match = re.search(r'data-mime-type="([^"]+)"', element_str)
    if mime_match:
        mime_type = mime_match.group(1)
        if 'document' in mime_type or 'kix' in mime_type:
            type_indicators.append('google docs')
        elif 'pdf' in mime_type:
            type_indicators.append('pdf')
        elif 'video' in mime_type:
            type_indicators.append('video')
        elif 'spreadsheet' in mime_type:
            type_indicators.append('google sheets')
        elif 'presentation' in mime_type:
            type_indicators.append('google slides')
    
    # Check for file extension in display name
    text_content = link_element.get_text(strip=True)
    ext_match = re.search(r'\.([a-zA-Z0-9]+)$', text_content)
    if ext_match:
        ext = ext_match.group(1).lower()
        if ext == 'pdf':
            type_indicators.append('pdf')
        elif ext in ['mp4', 'avi', 'mov']:
            type_indicators.append('video')
        elif ext in ['docx', 'doc']:
            type_indicators.append('google docs')
        elif ext in ['xlsx', 'xls']:
            type_indicators.append('google sheets')
        elif ext in ['pptx', 'ppt']:
            type_indicators.append('google slides')
    
    return list(set(type_indicators))  # Remove duplicates

def clean_display_name(name):
    """Clean display name by removing common suffixes and artifacts"""
    # Remove common Google service type suffixes
    suffixes_to_remove = [
        'Google Docs',
        'Google Doc', 
        'Google Sheets',
        'Google Sheet',
        'Google Slides', 
        'Google Slide',
        'PDF',
        'Video',
        'Document',
        'Spreadsheet',
        'Presentation'
    ]
    
    cleaned_name = name
    for suffix in suffixes_to_remove:
        # Remove suffix if it appears at the end
        if cleaned_name.endswith(suffix):
            cleaned_name = cleaned_name[:-len(suffix)].strip()
    
    # Remove duplicate file extensions in display name
    cleaned_name = re.sub(r'\.(pdf|docx?|xlsx?|pptx?|mp4|avi|mov)\.?\1$', r'.\1', cleaned_name, flags=re.IGNORECASE)
    
    # Remove trailing dots and spaces
    cleaned_name = cleaned_name.rstrip('. ')
    
    return cleaned_name

def select_best_name(names):
    """Select the best name from a list of candidates"""
    if not names:
        return ""
    
    # Clean all names first
    cleaned_names = [clean_display_name(name) for name in names]
    
    # Score each name based on quality criteria
    scored_names = []
    for name in cleaned_names:
        score = 0
        
        # Prefer longer names (more descriptive)
        score += len(name)
        
        # Bonus for not having common suffixes
        if not any(suffix.lower() in name.lower() for suffix in ['google docs', 'pdf', 'video', 'document']):
            score += 20
        
        # Penalty for generic names
        if name.lower() in ['untitled', 'document', 'file', 'sheet']:
            score -= 50
        
        # Bonus for having meaningful content
        if len(name.split()) > 1:  # Multi-word names are usually better
            score += 10
        
        scored_names.append((score, name))
    
    # Return the highest scored name
    scored_names.sort(reverse=True)
    best_name = scored_names[0][1]
    
    # Fallback to original if cleaning made it empty
    if not best_name.strip():
        best_name = names[0]
    
    return best_name

def group_files_by_content(drive_links):
    """
    Group files by content using normalized names and file types.
    This handles cases where same content has different file IDs.
    """
    content_groups = defaultdict(list)
    
    for link_info in drive_links:
        # Create a content signature
        normalized_name = normalize_filename(link_info['name'])
        file_types = sorted(link_info.get('file_types', []))
        content_signature = f"{normalized_name}|{','.join(file_types)}"
        
        content_groups[content_signature].append(link_info)
    
    return content_groups

def consolidate_duplicate_files(drive_links):
    """
    Consolidate duplicate files by content and select best canonical names
    
    Returns:
        - consolidated_files: List of unique file objects with best names
        - url_consolidation_map: Dict mapping all original URLs to canonical URLs
        - duplicate_report: Dict with statistics about duplicates found
    """
    print(f"\n🔍 CONSOLIDATING DUPLICATE FILES BY CONTENT")
    print(f"{'─' * 80}")
    
    # Group files by content (not just file_id)
    content_groups = group_files_by_content(drive_links)
    
    consolidated_files = []
    url_consolidation_map = {}
    duplicate_stats = {
        'total_original_links': len(drive_links),
        'unique_content_groups': len(content_groups),
        'duplicate_groups': 0,
        'total_duplicates_removed': 0
    }
    
    print(f"📊 Found {len(drive_links)} total links representing {len(content_groups)} unique content pieces")
    
    # Process each content group
    for content_signature, group in content_groups.items():
        if len(group) > 1:
            duplicate_stats['duplicate_groups'] += 1
            duplicate_stats['total_duplicates_removed'] += len(group) - 1
            
            print(f"🔄 Content '{content_signature.split('|')[0]}': Found {len(group)} duplicates")
            for i, link in enumerate(group):
                print(f"   {i+1}. '{link['name']}' -> {link['url']} (ID: {link['id']})")
        
        # Extract all names and file types from the group
        all_names = [link['name'] for link in group]
        all_file_types = []
        for link in group:
            all_file_types.extend(link.get('file_types', []))
        all_file_types = list(set(all_file_types))
        
        # Select the best canonical name
        canonical_name = select_best_name(all_names)
        
        # Choose the "best" file ID (prefer ones that aren't generic)
        best_link = group[0]
        for link in group:
            # Prefer links with more specific file types
            if len(link.get('file_types', [])) > len(best_link.get('file_types', [])):
                best_link = link
        
        # Create consolidated file entry
        canonical_link = best_link.copy()
        canonical_link['name'] = canonical_name
        canonical_link['original_names'] = all_names
        canonical_link['original_urls'] = [link['url'] for link in group]
        canonical_link['all_file_ids'] = [link['id'] for link in group]
        canonical_link['file_types'] = all_file_types
        canonical_link['duplicate_count'] = len(group)
        
        consolidated_files.append(canonical_link)
        
        if len(group) > 1:
            print(f"   ✅ Selected canonical name: '{canonical_name}' (using ID: {best_link['id']})")
        
        # Map all original URLs to the canonical URL (will be updated after upload)
        canonical_url = best_link['url']
        for link in group:
            url_consolidation_map[link['url']] = canonical_url
    
    # Print consolidation summary
    print(f"\n📋 CONSOLIDATION SUMMARY:")
    print(f"   📊 Original links: {duplicate_stats['total_original_links']}")
    print(f"   🎯 Unique content pieces: {duplicate_stats['unique_content_groups']}")
    print(f"   🔄 Duplicate content groups: {duplicate_stats['duplicate_groups']}")
    print(f"   ❌ Duplicates removed: {duplicate_stats['total_duplicates_removed']}")
    print(f"   📉 Reduction: {duplicate_stats['total_duplicates_removed']/duplicate_stats['total_original_links']*100:.1f}%")
    
    if duplicate_stats['duplicate_groups'] > 0:
        print(f"\n🎉 Successfully consolidated {duplicate_stats['duplicate_groups']} duplicate content groups!")
        print(f"   This will reduce processing time and prevent duplicate uploads.")
    
    return consolidated_files, url_consolidation_map, duplicate_stats

def extract_drive_links_from_html(html_file_path):
    """Extract Google Drive links from HTML file with enhanced type detection"""
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    drive_links = []
    
    # Find all links that contain Google Drive URLs
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if 'drive.google.com' in href or 'docs.google.com' in href:
            file_id = extract_file_id(href)
            if file_id:
                filename = a_tag.get_text(strip=True) or f"file_{file_id}"
                
                # Extract file type information from HTML context
                file_types = extract_file_type_from_html(a_tag)
                
                # Look at parent elements for additional context
                parent = a_tag.parent
                while parent and len(file_types) == 0:
                    file_types = extract_file_type_from_html(parent)
                    parent = parent.parent
                    # Don't go too far up the tree
                    if parent and parent.name in ['body', 'html']:
                        break
                
                drive_links.append({
                    'id': file_id,
                    'url': href,
                    'name': filename,
                    'file_types': file_types,
                    'element': str(a_tag)
                })
    
    print(f"📄 Extracted {len(drive_links)} Google Drive links from HTML")
    return drive_links, html_content

def get_drive_service(credentials_file='credentials.json', token_file='token.json'):
    """Authenticate and return Google Drive service with improved error handling"""
    creds = None
    
    # Check for existing token
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception as e:
            print(f"⚠️  Error loading existing token: {e}")
            print("🔄 Will create new authentication...")
            # Delete corrupted token file
            os.remove(token_file)
            creds = None
    
    # Handle token refresh or create new authentication
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("🔄 Refreshing expired token...")
                creds.refresh(Request())
            except Exception as e:
                print(f"❌ Token refresh failed: {e}")
                print("🆕 Creating new authentication...")
                # Delete failed token and create new one
                if os.path.exists(token_file):
                    os.remove(token_file)
                creds = None
        
        if not creds:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(f"❌ Credentials file not found: {credentials_file}")
            
            print("🔐 Starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        print("✅ Authentication successful!")
    
    return build('drive', 'v3', credentials=creds)

def download_file_from_drive(service, file_id, output_path, original_name):
    """Download file from Google Drive with proper handling for different file types"""
    try:
        print(f"📥 Downloading: {original_name}")
        
        # Get file metadata first
        file_metadata = service.files().get(fileId=file_id, fields='name,mimeType,size').execute()
        mime_type = file_metadata['mimeType']
        file_name = file_metadata['name']
        
        print(f"📋 File type: {mime_type}")
        
        # Handle Google Workspace files (need export)
        if mime_type in EXPORT_MIME_TYPES:
            export_mime = EXPORT_MIME_TYPES[mime_type]
            extension = EXPORT_EXTENSIONS.get(export_mime, '.txt')
            
            # Ensure output path has correct extension
            base_name = os.path.splitext(output_path)[0]
            output_path = base_name + extension
            
            print(f"🔄 Exporting Google Workspace file as {export_mime}")
            request = service.files().export_media(fileId=file_id, mimeType=export_mime)
        else:
            # Regular files - direct download
            print(f"📁 Downloading regular file")
            request = service.files().get_media(fileId=file_id)
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Download the file
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        
        while done is False:
            status, done = downloader.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"   📊 Progress: {progress}%")
        
        # Write to file
        with open(output_path, 'wb') as f:
            f.write(fh.getvalue())
        
        file_size = os.path.getsize(output_path)
        print(f"✅ Download complete: {output_path} ({file_size:,} bytes)")
        return True
        
    except Exception as e:
        print(f"❌ Download failed for {file_id}: {str(e)}")
        return False

def find_best_matching_file(downloads_folder, target_name, file_id, file_types=None):
    """Find the best matching local file using improved algorithm with type matching"""
    if not os.path.exists(downloads_folder):
        return None, 0
    
    local_files = os.listdir(downloads_folder)
    target_normalized = normalize_filename(target_name)
    
    best_match = None
    best_score = 0
    matches = []
    
    print(f"🔍 Looking for file matching: '{target_name}'")
    if file_types:
        print(f"📋 Expected file types: {', '.join(file_types)}")
    print(f"📂 Searching in: {downloads_folder}")
    
    for local_file in local_files:
        local_normalized = normalize_filename(local_file)
        
        # Calculate similarity score
        score = similarity_score(target_normalized, local_normalized)
        
        # Bonus for exact match
        if target_normalized == local_normalized:
            score = 1.0
        
        # Bonus for containing file_id
        if file_id and file_id.lower() in local_file.lower():
            score += 0.2
        
        # Bonus for exact name match (case insensitive)
        if target_name.lower() == os.path.splitext(local_file)[0].lower():
            score = 1.0
        
        # File type matching bonus
        if file_types:
            file_ext = os.path.splitext(local_file)[1].lower()
            type_match = False
            
            for file_type in file_types:
                expected_exts = HTML_TYPE_TO_EXTENSIONS.get(file_type.lower(), [])
                if file_ext in expected_exts:
                    score += 0.3  # Significant bonus for type match
                    type_match = True
                    break
            
            # Penalty for type mismatch
            if not type_match and len(file_types) > 0:
                score -= 0.2
        
        matches.append({
            'file': local_file,
            'score': score,
            'path': os.path.join(downloads_folder, local_file),
            'extension': os.path.splitext(local_file)[1].lower()
        })
    
    # Sort by score
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    # Show top matches for debugging
    print(f"🎯 Top 5 matches:")
    for i, match in enumerate(matches[:5]):
        type_info = ""
        if file_types:
            ext = match['extension']
            matching_types = []
            for file_type in file_types:
                expected_exts = HTML_TYPE_TO_EXTENSIONS.get(file_type.lower(), [])
                if ext in expected_exts:
                    matching_types.append(file_type)
            if matching_types:
                type_info = f" [type: {', '.join(matching_types)}]"
        
        print(f"   {i+1}. {match['file']} (score: {match['score']:.3f}){type_info}")
    
    if matches and matches[0]['score'] > 0.3:  # Lowered threshold for better matching
        best_match = matches[0]['path']
        best_score = matches[0]['score']
        print(f"✅ Selected: {os.path.basename(best_match)} (score: {best_score:.3f})")
    else:
        best_score_display = matches[0]['score'] if matches else 0
        print(f"❌ No suitable match found (best score: {best_score_display:.3f})")
    
    return best_match, best_score

def download_missing_files(service, missing_files, downloads_folder):
    """Download files that have no local matches"""
    print(f"\n🔄 DOWNLOADING MISSING FILES")
    print(f"{'─' * 80}")
    
    downloaded_count = 0
    failed_downloads = []
    
    for i, missing_file in enumerate(missing_files, 1):
        print(f"\n📥 [{i}/{len(missing_files)}] Processing: {missing_file['drive_name']}")
        
        # Create safe filename
        safe_name = re.sub(r'[^\w\s-]', '', missing_file['drive_name'])
        safe_name = re.sub(r'\s+', '_', safe_name.strip())
        
        # We'll determine the extension after getting file info
        temp_output_path = os.path.join(downloads_folder, f"{safe_name}.tmp")
        
        try:
            # Download the file
            if download_file_from_drive(service, missing_file['file_id'], temp_output_path, missing_file['drive_name']):
                # Rename from .tmp to actual extension after download
                final_files = [f for f in os.listdir(downloads_folder) if f.startswith(safe_name) and not f.endswith('.tmp')]
                if final_files:
                    # Remove .tmp file if it exists
                    if os.path.exists(temp_output_path):
                        os.remove(temp_output_path)
                    downloaded_count += 1
                    print(f"✅ Successfully downloaded and saved")
                else:
                    downloaded_count += 1
                    print(f"✅ Successfully downloaded")
            else:
                failed_downloads.append(missing_file)
                
        except Exception as e:
            print(f"❌ Failed to download {missing_file['drive_name']}: {str(e)}")
            failed_downloads.append(missing_file)
            continue
    
    print(f"\n📊 Download Summary:")
    print(f"   ✅ Successfully downloaded: {downloaded_count}")
    print(f"   ❌ Failed downloads: {len(failed_downloads)}")
    
    if failed_downloads:
        print(f"\n❌ Failed downloads:")
        for failed in failed_downloads[:5]:
            print(f"   - {failed['drive_name']} (ID: {failed['file_id']})")
        if len(failed_downloads) > 5:
            print(f"   ... and {len(failed_downloads) - 5} more")
    
    return downloaded_count, failed_downloads

def find_or_create_folder(service, folder_name, parent_id='root'):
    """Find or create a folder in Google Drive"""
    # Search for existing folder
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields='files(id, name)').execute()
    folders = results.get('files', [])
    
    if folders:
        print(f"📁 Found existing folder: {folder_name} (ID: {folders[0]['id']})")
        return folders[0]['id']
    
    # Create new folder
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    print(f"📁 Created new folder: {folder_name} (ID: {folder['id']})")
    return folder['id']

def get_file_info(service, file_id):
    """Get file information from Google Drive"""
    try:
        file_info = service.files().get(
            fileId=file_id,
            fields='id,name,mimeType,parents,trashed,webViewLink'
        ).execute()
        return file_info
    except Exception as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg or '404' in error_msg:
            print(f"⚠️  File not found (404): {file_id} - skipping")
            return 'NOT_FOUND'
        else:
            print(f"❌ Error getting file info for {file_id}: {str(e)}")
            return None

def upload_file_to_drive(service, file_path, folder_id, original_name=None):
    """Upload a file to Google Drive in the specified folder"""
    try:
        filename = os.path.basename(file_path)
        display_name = original_name or os.path.splitext(filename)[0]
        
        print(f"📤 Uploading: {filename} -> {display_name}")
        
        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # Check if we should convert to Google Workspace format
        convert_mime = GOOGLE_MIME_TYPES.get(mime_type)
        
        file_metadata = {
            'name': display_name,
            'parents': [folder_id]
        }
        
        # If converting to Google Workspace format, set the target MIME type
        if convert_mime:
            file_metadata['mimeType'] = convert_mime
            print(f"🔄 Converting {mime_type} to {convert_mime}")
        
        media = MediaFileUpload(file_path, mimetype=mime_type)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink,name'
        ).execute()
        
        # Set permissions to "anyone can view"
        permission = {
            'role': 'reader',
            'type': 'anyone'
        }
        service.permissions().create(
            fileId=file['id'],
            body=permission
        ).execute()
        
        print(f"✅ Upload successful!")
        print(f"   📋 Name: {file['name']}")
        print(f"   🆔 ID: {file['id']}")
        print(f"   🔗 Link: {file['webViewLink']}")
        
        return {
            'id': file['id'],
            'url': file['webViewLink'],
            'name': file['name']
        }
        
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        return None

def create_updated_html(original_html_content, url_mapping, output_path):
    """Create updated HTML file with new URLs, handling consolidated duplicates"""
    soup = BeautifulSoup(original_html_content, 'html.parser')
    
    updated_count = 0
    
    # Create a comprehensive mapping that includes all original URLs
    comprehensive_mapping = {}
    for original_url, new_url in url_mapping.items():
        comprehensive_mapping[original_url] = new_url
    
    # Update all links
    for a_tag in soup.find_all('a', href=True):
        original_url = a_tag['href']
        if original_url in comprehensive_mapping:
            a_tag['href'] = comprehensive_mapping[original_url]
            updated_count += 1
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write updated HTML
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    
    print(f"📄 Updated HTML created: {output_path}")
    print(f"🔗 Updated {updated_count} links (including consolidated duplicates)")
    return output_path

def save_consolidation_report(duplicate_stats, consolidated_files, output_folder):
    """Save detailed consolidation report"""
    report_file = os.path.join(output_folder, 'consolidation_report.csv')
    
    with open(report_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'content_signature', 'canonical_name', 'selected_file_id', 'duplicate_count', 
            'all_file_ids', 'original_names', 'original_urls', 'file_types'
        ])
        writer.writeheader()
        
        for file_info in consolidated_files:
            if file_info['duplicate_count'] > 1:  # Only include files that had duplicates
                writer.writerow({
                    'content_signature': f"{normalize_filename(file_info['name'])}|{','.join(sorted(file_info.get('file_types', [])))}",
                    'canonical_name': file_info['name'],
                    'selected_file_id': file_info['id'],
                    'duplicate_count': file_info['duplicate_count'],
                    'all_file_ids': ' | '.join(file_info.get('all_file_ids', [])),
                    'original_names': ' | '.join(file_info.get('original_names', [])),
                    'original_urls': ' | '.join(file_info.get('original_urls', [])),
                    'file_types': ' | '.join(file_info.get('file_types', []))
                })
    
    print(f"📋 Consolidation report saved: {report_file}")

def load_progress():
    """Load progress from checkpoint files"""
    progress = {
        'completed': set(),
        'failed': set()
    }
    
    mapping_file = os.path.join(UPLOAD_FOLDER, 'file_mapping.csv')
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            progress['completed'] = {row['original_url'] for row in reader}
    
    error_file = os.path.join(UPLOAD_FOLDER, 'error_log.csv')
    if os.path.exists(error_file):
        with open(error_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            progress['failed'] = {row['url'] for row in reader}
    
    return progress

def save_checkpoint(mapping_data, error_data):
    """Save progress to checkpoint files"""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    mapping_file = os.path.join(UPLOAD_FOLDER, 'file_mapping.csv')
    with open(mapping_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'original_url', 'new_url', 'name', 'id', 'original_id', 'local_file', 
            'match_score', 'consolidated_from', 'file_types'
        ])
        writer.writeheader()
        writer.writerows(mapping_data)
    
    error_file = os.path.join(UPLOAD_FOLDER, 'error_log.csv')
    with open(error_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['url', 'error', 'timestamp', 'file_id', 'original_name'])
        writer.writeheader()
        writer.writerows(error_data)

def print_progress_header():
    """Print progress tracking header"""
    print(f"\n{'='*80}")
    print(f"{'GOOGLE DRIVE RESOURCE REPLACEMENT WITH SMART CONSOLIDATION':^80}")
    print(f"{'='*80}")

def print_file_progress(current, total, filename):
    """Print current file progress"""
    percentage = (current * 100) // total
    bar_length = 40
    filled_length = (percentage * bar_length) // 100
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    print(f"\n┌{'─' * 78}┐")
    print(f"│ Progress: [{bar}] {percentage:3d}% ({current}/{total}) │")
    print(f"│ Current: {filename[:65]:<65} │")
    print(f"└{'─' * 78}┘")

def verify_file_association(consolidated_files, downloads_folder):
    """Verify and display file associations before processing with type matching"""
    print(f"\n🔍 VERIFYING FILE ASSOCIATIONS WITH TYPE MATCHING")
    print(f"{'─' * 80}")
    
    associations = []
    missing_files = []
    skipped_files = []
    
    for link_info in consolidated_files:
        # Skip files with generic names or obvious 404 indicators
        if link_info['name'].lower() in ['drive file', 'untitled', 'file', '']:
            print(f"⚠️  Skipping generic filename: '{link_info['name']}'")
            skipped_files.append(link_info)
            continue
            
        local_file, score = find_best_matching_file(
            downloads_folder, 
            link_info['name'], 
            link_info['id'],
            link_info.get('file_types', [])
        )
        
        if local_file and score > 0.3:  # Lowered threshold
            associations.append({
                'drive_name': link_info['name'],
                'local_file': os.path.basename(local_file),
                'score': score,
                'url': link_info['url'],
                'duplicate_count': link_info.get('duplicate_count', 1),
                'file_types': link_info.get('file_types', [])
            })
        else:
            missing_files.append({
                'drive_name': link_info['name'],
                'file_id': link_info['id'],
                'url': link_info['url'],
                'duplicate_count': link_info.get('duplicate_count', 1),
                'file_types': link_info.get('file_types', [])
            })
    
    if associations:
        print(f"✅ Found {len(associations)} file associations:")
        total_links_covered = sum(assoc['duplicate_count'] for assoc in associations)
        print(f"   📊 Covering {total_links_covered} original HTML links")
        
        for i, assoc in enumerate(associations[:10], 1):  # Show first 10
            dup_info = f" (covers {assoc['duplicate_count']} links)" if assoc['duplicate_count'] > 1 else ""
            type_info = f" [{', '.join(assoc['file_types'])}]" if assoc['file_types'] else ""
            print(f"   {i:2d}. '{assoc['drive_name']}'{type_info} -> '{assoc['local_file']}' (score: {assoc['score']:.3f}){dup_info}")
        if len(associations) > 10:
            print(f"   ... and {len(associations) - 10} more associations")
    
    if missing_files:
        total_missing_links = sum(missing['duplicate_count'] for missing in missing_files)
        print(f"\n❌ Missing local files for {len(missing_files)} unique files:")
        print(f"   📊 Affecting {total_missing_links} original HTML links")
        
        for i, missing in enumerate(missing_files[:5], 1):  # Show first 5
            dup_info = f" (affects {missing['duplicate_count']} links)" if missing['duplicate_count'] > 1 else ""
            type_info = f" [{', '.join(missing['file_types'])}]" if missing['file_types'] else ""
            print(f"   {i}. '{missing['drive_name']}'{type_info} (ID: {missing['file_id']}){dup_info}")
        if len(missing_files) > 5:
            print(f"   ... and {len(missing_files) - 5} more missing files")
    
    if skipped_files:
        print(f"\n⚠️  Skipped {len(skipped_files)} files with generic/invalid names")
    
    return len(associations), len(missing_files), missing_files

def main():
    parser = argparse.ArgumentParser(description='Update Google Drive resources from local files with smart content-based consolidation')
    parser.add_argument('--resume', action='store_true', help='Resume interrupted transfer')
    parser.add_argument('--retry-failed', action='store_true', help='Retry only failed transfers')
    parser.add_argument('--html-file', default=HTML_FILE, help='HTML file to process')
    parser.add_argument('--downloads-folder', default=DOWNLOADS_FOLDER, help='Local downloads folder')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without changes')
    parser.add_argument('--download-missing', action='store_true', help='Download missing files from Google Drive')
    parser.add_argument('--reset-auth', action='store_true', help='Reset authentication (delete token.json)')
    parser.add_argument('--no-consolidation', action='store_true', help='Disable duplicate consolidation')
    parser.add_argument('--show-types', action='store_true', help='Show detected file types for debugging')
    args = parser.parse_args()
    
    print_progress_header()
    
    # Handle authentication reset
    if args.reset_auth:
        token_file = 'token.json'
        if os.path.exists(token_file):
            os.remove(token_file)
            print(f"✅ Removed {token_file} - will re-authenticate on next run")
        else:
            print(f"ℹ️  No {token_file} found to remove")
        return
    
    # Check if HTML file exists
    if not os.path.exists(args.html_file):
        print(f"❌ Error: HTML file {args.html_file} not found")
        return
    
    # Create downloads folder if it doesn't exist
    os.makedirs(args.downloads_folder, exist_ok=True)
    
    # Setup upload directory
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Load progress if resuming
    progress = load_progress() if args.resume or args.retry_failed else {'completed': set(), 'failed': set()}
    
    # Extract links from HTML with enhanced type detection
    print(f"📄 Parsing HTML file: {args.html_file}")
    all_drive_links, html_content = extract_drive_links_from_html(args.html_file)
    print(f"🔗 Found {len(all_drive_links)} total Google Drive links in HTML")
    
    # Show file type detection if requested
    if args.show_types:
        print(f"\n🔍 DETECTED FILE TYPES:")
        print(f"{'─' * 80}")
        for i, link in enumerate(all_drive_links[:10], 1):  # Show first 10
            types_str = ', '.join(link['file_types']) if link['file_types'] else 'No types detected'
            print(f"   {i:2d}. '{link['name']}' -> [{types_str}]")
        if len(all_drive_links) > 10:
            print(f"   ... and {len(all_drive_links) - 10} more files")
    
    # Phase 1: Consolidate duplicates by content (unless disabled)
    if not args.no_consolidation:
        consolidated_files, url_consolidation_map, duplicate_stats = consolidate_duplicate_files(all_drive_links)
    else:
        print(f"⚠️  Duplicate consolidation disabled - processing all files individually")
        consolidated_files = all_drive_links
        url_consolidation_map = {link['url']: link['url'] for link in all_drive_links}
        duplicate_stats = {
            'total_original_links': len(all_drive_links),
            'unique_content_groups': len(all_drive_links),
            'duplicate_groups': 0,
            'total_duplicates_removed': 0
        }
    
    # Filter out files with generic names or 404 errors before processing
    valid_consolidated_files = []
    for link in consolidated_files:
        # Skip obviously invalid files
        if link['name'].lower() in ['drive file', 'untitled', 'file', '']:
            print(f"⚠️  Skipping file with generic name: '{link['name']}'")
            continue
        valid_consolidated_files.append(link)
    
    consolidated_files = valid_consolidated_files
    
    # Filter files based on resume mode
    if args.retry_failed:
        drive_links = [link for link in consolidated_files if link['url'] in progress['failed']]
        print(f"🔄 Retry mode: Processing {len(drive_links)} failed files")
    elif args.resume:
        drive_links = [link for link in consolidated_files if link['url'] not in progress['completed']]
        print(f"▶️  Resume mode: Processing {len(drive_links)} remaining files")
    else:
        drive_links = consolidated_files
        print(f"🆕 Fresh start: Processing {len(drive_links)} content-consolidated unique files")
    
    if not drive_links:
        print("✅ No files to process")
        return
    
    # Save consolidation report
    if not args.no_consolidation and duplicate_stats['duplicate_groups'] > 0:
        save_consolidation_report(duplicate_stats, consolidated_files, UPLOAD_FOLDER)
    
    # Verify file associations with enhanced type matching
    matched_count, missing_count, missing_files = verify_file_association(drive_links, args.downloads_folder)
    
    # Handle missing files
    if missing_count > 0 and args.download_missing:
        print(f"\n🔐 Authenticating with Google Drive for downloads...")
        try:
            service = get_drive_service()
            
            # Download missing files
            downloaded_count, failed_downloads = download_missing_files(service, missing_files, args.downloads_folder)
            
            if downloaded_count > 0:
                print(f"\n✅ Downloaded {downloaded_count} missing files!")
                print(f"🔄 Re-verifying file associations...")
                
                # Re-verify associations after downloading
                matched_count, missing_count, missing_files = verify_file_association(drive_links, args.downloads_folder)
                print(f"📊 Updated stats: {matched_count} matches, {missing_count} still missing")
        
        except Exception as e:
            print(f"❌ Authentication failed: {str(e)}")
            print(f"💡 Try running with --reset-auth to reset authentication")
            return
    
    elif missing_count > 0 and not args.download_missing:
        print(f"\n⚠️  Warning: {missing_count} files have no local matches")
        print(f"💡 Use --download-missing flag to automatically download them from Google Drive")
        if not args.dry_run:
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("Aborted by user")
                return
    
    if args.dry_run:
        print(f"\n🏃 DRY RUN: Would process {matched_count} unique content pieces")
        print(f"   📊 This represents {sum(f.get('duplicate_count', 1) for f in drive_links)} original HTML links")
        return
    
    # Initialize Google Drive service
    print(f"\n🔐 Authenticating with Google Drive...")
    try:
        service = get_drive_service()
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        print(f"💡 Try running with --reset-auth to reset authentication")
        return
    
    # Find or create classroom_Resource folder
    print(f"📁 Setting up {CLASSROOM_FOLDER_NAME} folder...")
    classroom_folder_id = find_or_create_folder(service, CLASSROOM_FOLDER_NAME)
    
    # Initialize tracking
    mapping_data = []
    error_data = []
    final_url_mapping = {}
    
    # Load existing mappings if resuming
    if args.resume and os.path.exists(os.path.join(UPLOAD_FOLDER, 'file_mapping.csv')):
        with open(os.path.join(UPLOAD_FOLDER, 'file_mapping.csv'), 'r', encoding='utf-8') as f:
            existing_mappings = list(csv.DictReader(f))
            mapping_data.extend(existing_mappings)
            final_url_mapping.update({m['original_url']: m['new_url'] for m in existing_mappings})
    
    # Process files
    start_time = time.time()
    processed_count = 0
    successful_uploads = 0
    
    print(f"\n🚀 STARTING FILE PROCESSING WITH SMART MATCHING")
    print(f"{'─' * 80}")
    
    for i, link_info in enumerate(drive_links, 1):
        print_file_progress(i, len(drive_links), link_info['name'])
        
        # Show duplicate and type info if applicable
        if link_info.get('duplicate_count', 1) > 1:
            print(f"🔄 This content consolidates {link_info['duplicate_count']} duplicate links")
        if link_info.get('file_types'):
            print(f"📋 Expected types: {', '.join(link_info['file_types'])}")
        
        # Skip if already processed and resuming
        if args.resume and link_info['url'] in progress['completed']:
            print(f"⏭️  Already processed: {link_info['name']}")
            continue
        
        # Skip if not in retry list when retrying failed
        if args.retry_failed and link_info['url'] not in progress['failed']:
            continue
        
        processed_count += 1
        retry_count = 0
        upload_success = False
        
        while retry_count < MAX_RETRIES and not upload_success:
            try:
                # Verify the original file exists in Google Drive
                print(f"🔍 Verifying original file: {link_info['name']} ({link_info['id']})")
                file_info = get_file_info(service, link_info['id'])
                
                if file_info == 'NOT_FOUND':
                    error_data.append({
                        'url': link_info['url'],
                        'error': 'File not found (404)',
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'file_id': link_info['id'],
                        'original_name': link_info['name']
                    })
                    print(f"❌ Original file not found in Google Drive - skipping")
                    break
                
                if not file_info:
                    raise Exception("Failed to get file information")
                
                print(f"✅ Original file verified: {file_info['name']}")
                
                # Find matching local file with type information
                local_file_path, match_score = find_best_matching_file(
                    args.downloads_folder, 
                    link_info['name'], 
                    link_info['id'],
                    link_info.get('file_types', [])
                )
                
                if not local_file_path or match_score < 0.3:  # Lowered threshold
                    error_data.append({
                        'url': link_info['url'],
                        'error': f'No suitable local match found (best score: {match_score:.3f})',
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'file_id': link_info['id'],
                        'original_name': link_info['name']
                    })
                    print(f"❌ No suitable local file found - skipping")
                    break
                
                print(f"📁 Using local file: {os.path.basename(local_file_path)} (score: {match_score:.3f})")
                
                # Upload new version to classroom_Resource folder
                upload_result = upload_file_to_drive(
                    service, 
                    local_file_path, 
                    classroom_folder_id, 
                    link_info['name']
                )
                
                if upload_result:
                    # Get all original URLs that this content represents
                    original_urls = link_info.get('original_urls', [link_info['url']])
                    
                    # Record successful mapping for the primary URL
                    consolidated_from = ""
                    if len(original_urls) > 1:
                        consolidated_from = " | ".join(original_urls)
                    
                    mapping_data.append({
                        'original_url': link_info['url'],
                        'new_url': upload_result['url'],
                        'name': upload_result['name'],
                        'id': upload_result['id'],
                        'original_id': link_info['id'],
                        'local_file': os.path.basename(local_file_path),
                        'match_score': f"{match_score:.3f}",
                        'consolidated_from': consolidated_from,
                        'file_types': ', '.join(link_info.get('file_types', []))
                    })
                    
                    # Map ALL original URLs to the new URL (including content duplicates)
                    for original_url in original_urls:
                        final_url_mapping[original_url] = upload_result['url']
                    
                    successful_uploads += 1
                    upload_success = True
                    
                    if len(original_urls) > 1:
                        print(f"✅ Successfully processed: {link_info['name']} (consolidated {len(original_urls)} content duplicates)")
                    else:
                        print(f"✅ Successfully processed: {link_info['name']}")
                    
                else:
                    raise Exception("Upload failed")
                
            except Exception as e:
                retry_count += 1
                error_msg = str(e)
                print(f"❌ Error processing {link_info['name']} (attempt {retry_count}/{MAX_RETRIES}): {error_msg}")
                
                if retry_count < MAX_RETRIES:
                    print(f"⏳ Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    # Record final failure
                    error_data.append({
                        'url': link_info['url'],
                        'error': f'Failed after {MAX_RETRIES} attempts: {error_msg}',
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'file_id': link_info['id'],
                        'original_name': link_info['name']
                    })
                    print(f"❌ Final failure after {MAX_RETRIES} attempts")
        
        # Save progress periodically
        if processed_count % CHECKPOINT_INTERVAL == 0:
            print(f"💾 Saving checkpoint at file {processed_count}...")
            save_checkpoint(mapping_data, error_data)
    
    # Final save
    print(f"\n💾 Saving final results...")
    save_checkpoint(mapping_data, error_data)
    
    # Create updated HTML file
    if final_url_mapping:
        output_html_path = os.path.join(UPLOAD_FOLDER, 'updated_index.html')
        create_updated_html(html_content, final_url_mapping, output_html_path)
    
    # Print final summary
    elapsed_time = time.time() - start_time
    print(f"\n{'='*80}")
    print(f"{'PROCESSING COMPLETE':^80}")
    print(f"{'='*80}")
    
    print(f"📊 Final Statistics:")
    print(f"   📁 Original HTML links: {duplicate_stats['total_original_links']}")
    print(f"   🎯 Unique content pieces processed: {processed_count}")
    print(f"   ✅ Successful uploads: {successful_uploads}")
    print(f"   ❌ Failed uploads: {len(error_data)}")
    print(f"   🔗 Total URLs updated in HTML: {len(final_url_mapping)}")
    print(f"   ⏱️  Total time: {elapsed_time:.1f} seconds")
    
    if not args.no_consolidation:
        print(f"\n📋 Smart Consolidation Summary:")
        print(f"   🔄 Content groups consolidated: {duplicate_stats['duplicate_groups']}")
        print(f"   ❌ Duplicates eliminated: {duplicate_stats['total_duplicates_removed']}")
        print(f"   📉 Processing reduction: {duplicate_stats['total_duplicates_removed']/duplicate_stats['total_original_links']*100:.1f}%")
    
    if successful_uploads > 0:
        avg_time = elapsed_time / successful_uploads
        print(f"   📈 Average time per unique content: {avg_time:.1f} seconds")
    
    print(f"\n📂 Output Files:")
    print(f"   📋 File mapping: {os.path.join(UPLOAD_FOLDER, 'file_mapping.csv')}")
    print(f"   📋 Error log: {os.path.join(UPLOAD_FOLDER, 'error_log.csv')}")
    
    if not args.no_consolidation and duplicate_stats['duplicate_groups'] > 0:
        print(f"   📋 Consolidation report: {os.path.join(UPLOAD_FOLDER, 'consolidation_report.csv')}")
    
    if final_url_mapping:
        print(f"   📄 Updated HTML: {os.path.join(UPLOAD_FOLDER, 'updated_index.html')}")
    
    if error_data:
        print(f"\n⚠️  Errors encountered:")
        error_types = {}
        for error in error_data:
            error_type = error['error'].split(':')[0]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        for error_type, count in error_types.items():
            print(f"   - {error_type}: {count} files")
        
        print(f"\n💡 Tips for resolving errors:")
        print(f"   • Check that files exist in both Google Drive and local folder")
        print(f"   • Ensure file names are similar enough for matching")
        print(f"   • Use --download-missing to get files from Google Drive")
        print(f"   • Use --retry-failed to retry failed uploads")
        print(f"   • Use --show-types to debug file type detection")
    
    if successful_uploads > 0:
        efficiency_note = ""
        if not args.no_consolidation and duplicate_stats['duplicate_groups'] > 0:
            efficiency_note = f" (saved {duplicate_stats['total_duplicates_removed']} redundant uploads through smart consolidation)"
        
        print(f"\n🎉 Success! {successful_uploads} unique content pieces uploaded to '{CLASSROOM_FOLDER_NAME}' folder{efficiency_note}")
        print(f"   📄 {len(final_url_mapping)} HTML links updated with public viewing permissions")
        print(f"   🧠 Smart type matching and content consolidation applied")

if __name__ == '__main__':
    main()