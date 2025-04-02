import re
import os
import time
import csv
import email
import io
import argparse
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.generator import BytesGenerator
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
import shutil

# Configuration
MHTML_FILE = 'GoogleDriveLinksTest.mhtml'
DOWNLOAD_FOLDER = 'downloads'
UPLOAD_FOLDER = 'uploaded_files'
SCOPES = ['https://www.googleapis.com/auth/drive']
CHECKPOINT_INTERVAL = 50
MAX_RETRIES = 3
RETRY_DELAY = 10

# Google Workspace MIME types
GOOGLE_MIME_TYPES = {
    'document': 'application/vnd.google-apps.document',
    'spreadsheet': 'application/vnd.google-apps.spreadsheet',
    'presentation': 'application/vnd.google-apps.presentation'
}

EXPORT_FORMATS = {
    'application/vnd.google-apps.document': {
        'export_mime': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'extension': '.docx'
    },
    'application/vnd.google-apps.spreadsheet': {
        'export_mime': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'extension': '.xlsx'
    },
    'application/vnd.google-apps.presentation': {
        'export_mime': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'extension': '.pptx'
    }
}

def parse_mhtml_file(mhtml_path):
    """Parse MHTML file and extract HTML content"""
    with open(mhtml_path, 'rb') as f:
        msg = email.message_from_binary_file(f)
    
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            return part.get_payload(decode=True).decode('utf-8')
    return None

def extract_file_id(url):
    """Extract file ID from Google Drive URL"""
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]+)',
        r'/document/d/([a-zA-Z0-9_-]+)',
        r'/open\?id=([a-zA-Z0-9_-]+)',
        r'/spreadsheets/d/([a-zA-Z0-9_-]+)',
        r'/presentation/d/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def extract_targeted_links(html_content):
    """Extract Google Drive links from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    target_links = []
    
    # Multiple selector patterns to find links
    selectors = [
        {'class': re.compile(r'VkhHKd e7EEH nQaZq')},
        {'class': re.compile(r'drive-viewer-link')},
        {'href': re.compile(r'drive\.google\.com')},
        {'role': 'link', 'href': True}
    ]
    
    for selector in selectors:
        elements = soup.find_all(**selector)
        for element in elements:
            if element.name == 'a' and 'href' in element.attrs:
                href = element['href']
                file_id = extract_file_id(href)
                if file_id:
                    filename = element.get_text(strip=True) or f"file_{file_id}"
                    target_links.append({
                        'id': file_id,
                        'url': href,
                        'name': filename,
                        'element': str(element)
                    })
        if target_links:
            break
    
    return target_links

def get_drive_service(credentials_file='credentials.json', token_file='token.json'):
    """Authenticate and return Google Drive service"""
    creds = None
    
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file,
                SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )
            creds = flow.run_local_server(port=0)
        
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def download_file(service, file_info, download_folder):
    """Download a file from Google Drive"""
    try:
        file_id = file_info['id']
        filename = file_info['name']
        
        # Get file metadata
        file_metadata = service.files().get(
            fileId=file_id,
            fields='name,mimeType,exportLinks'
        ).execute()
        
        mime_type = file_metadata.get('mimeType', '')
        filename = file_metadata.get('name', filename)
        
        print(f"\nProcessing: {filename} ({mime_type})")
        
        os.makedirs(download_folder, exist_ok=True)
        
        # Handle Google Workspace files
        if mime_type in EXPORT_FORMATS:
            export_info = EXPORT_FORMATS[mime_type]
            request = service.files().export_media(
                fileId=file_id,
                mimeType=export_info['export_mime']
            )
            filename = f"{os.path.splitext(filename)[0]}{export_info['extension']}"
        else:
            request = service.files().get_media(fileId=file_id)
        
        filepath = os.path.join(download_folder, filename)
        counter = 1
        while os.path.exists(filepath):
            name, ext = os.path.splitext(filename)
            filepath = os.path.join(download_folder, f"{name}_{counter}{ext}")
            counter += 1
        
        with io.FileIO(filepath, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download progress: {int(status.progress() * 100)}%", end='\r')
        
        print(f"\nDownloaded: {os.path.basename(filepath)}")
        return {
            'status': 'success',
            'path': filepath,
            'name': os.path.basename(filepath),
            'original_mime': mime_type,
            'original_url': file_info['url']
        }
        
    except Exception as e:
        print(f"\nError downloading file {file_id}: {str(e)}")
        return {'status': 'error', 'error': str(e)}

def upload_file(service, file_info):
    """Upload a file to Google Drive"""
    try:
        file_path = file_info['path']
        file_name = os.path.basename(file_path)
        
        # Handle Google Workspace file conversion
        if file_info.get('original_mime') in GOOGLE_MIME_TYPES.values():
            file_metadata = {
                'name': os.path.splitext(file_name)[0],
                'mimeType': file_info['original_mime']
            }
            media = None
        else:
            file_metadata = {'name': file_name}
            media = MediaFileUpload(file_path)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()
        
        print(f"Uploaded: {file_metadata['name']} (ID: {file['id']})")
        return {
            'id': file['id'],
            'url': file['webViewLink'],
            'name': file_metadata['name'],
            'original_url': file_info['original_url']
        }
        
    except Exception as e:
        print(f"Error uploading file {file_name}: {str(e)}")
        return None

def create_new_mhtml(original_path, updated_html):
    """Create new MHTML file with updated HTML content"""
    with open(original_path, 'rb') as f:
        original_msg = email.message_from_binary_file(f)
    
    # Create a new multipart message
    new_msg = MIMEMultipart('related')
    
    # Copy headers (excluding Content-Type and Content-Transfer-Encoding)
    for header, value in original_msg.items():
        if header.lower() not in ['content-type', 'content-transfer-encoding']:
            new_msg[header] = value
    
    # Create HTML part
    html_part = MIMEText(updated_html, 'html', 'utf-8')
    html_part.add_header('Content-Transfer-Encoding', 'quoted-printable')
    
    # Add HTML part first
    new_msg.attach(html_part)
    
    # Add other parts (images, attachments) unchanged
    for part in original_msg.walk():
        if part.get_content_type() != 'text/html':
            # Create a new part with the same content
            new_part = email.message.Message()
            new_part.set_type(part.get_content_type())
            for header, value in part.items():
                new_part[header] = value
            new_part.set_payload(part.get_payload(decode=True))
            new_msg.attach(new_part)
    
    # Save new file
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    new_path = os.path.join(UPLOAD_FOLDER, 'updated_' + os.path.basename(original_path))
    with open(new_path, 'wb') as f:
        gen = email.generator.BytesGenerator(f)
        gen.flatten(new_msg)
    
    return new_path


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
    mapping_file = os.path.join(UPLOAD_FOLDER, 'file_mapping.csv')
    with open(mapping_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['original_url', 'new_url', 'name', 'id'])
        writer.writeheader()
        writer.writerows(mapping_data)
    
    error_file = os.path.join(UPLOAD_FOLDER, 'error_log.csv')
    with open(error_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['url', 'error', 'timestamp'])
        writer.writeheader()
        writer.writerows(error_data)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', action='store_true', help='Resume interrupted transfer')
    parser.add_argument('--retry-failed', action='store_true', help='Retry only failed transfers')
    args = parser.parse_args()
    
    # Setup directories
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Load progress if resuming
    progress = load_progress() if args.resume or args.retry_failed else {'completed': set(), 'failed': set()}
    
    # Parse MHTML
    html_content = parse_mhtml_file(MHTML_FILE)
    if not html_content:
        print("Error: Could not extract HTML from MHTML file")
        return
    
    all_file_infos = extract_targeted_links(html_content)
    
    # Filter files based on resume mode
    if args.retry_failed:
        file_infos = [fi for fi in all_file_infos if fi['url'] in progress['failed']]
    elif args.resume:
        file_infos = [fi for fi in all_file_infos if fi['url'] not in progress['completed']]
    else:
        file_infos = all_file_infos
    
    print(f"Files to process: {len(file_infos)} (out of {len(all_file_infos)} total)")
    
    # Initialize services
    source_service = get_drive_service('source_credentials.json', 'source_token.json')
    dest_service = get_drive_service('dest_credentials.json', 'dest_token.json')
    
    # Initialize tracking
    mapping_data = []
    error_data = []
    
    # Load existing mappings if resuming
    if args.resume and os.path.exists(os.path.join(UPLOAD_FOLDER, 'file_mapping.csv')):
        with open(os.path.join(UPLOAD_FOLDER, 'file_mapping.csv'), 'r', encoding='utf-8') as f:
            mapping_data.extend(list(csv.DictReader(f)))
    
    # Process files
    processed_count = 0
    for i, file_info in enumerate(file_infos, 1):
        print(f"\nProcessing file {i}/{len(file_infos)}: {file_info['name']}")
        
        try:
            # Download with retry
            for attempt in range(MAX_RETRIES):
                try:
                    download_result = download_file(source_service, file_info, DOWNLOAD_FOLDER)
                    if download_result['status'] == 'success':
                        break
                    time.sleep(RETRY_DELAY)
                except Exception as e:
                    if attempt == MAX_RETRIES - 1:
                        raise
                    time.sleep(RETRY_DELAY)
            
            if download_result['status'] != 'success':
                raise Exception(f"Download failed: {download_result.get('error', 'Unknown error')}")
            
            # Upload with retry
            for attempt in range(MAX_RETRIES):
                try:
                    upload_result = upload_file(dest_service, download_result)
                    if upload_result:
                        break
                    time.sleep(RETRY_DELAY)
                except Exception as e:
                    if attempt == MAX_RETRIES - 1:
                        raise
                    time.sleep(RETRY_DELAY)
            
            if not upload_result:
                raise Exception("Upload failed")
            
            # Record success
            mapping_data.append({
                'original_url': file_info['url'],
                'new_url': upload_result['url'],
                'name': upload_result['name'],
                'id': upload_result['id']
            })
            
            # Update progress
            processed_count += 1
            if file_info['url'] in progress['failed']:
                progress['failed'].remove(file_info['url'])
            
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            error_data.append({
                'url': file_info['url'],
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })
            progress['failed'].add(file_info['url'])
            continue
        
        # Save checkpoint periodically
        if i % CHECKPOINT_INTERVAL == 0 or i == len(file_infos):
            save_checkpoint(mapping_data, error_data)
            print(f"\nCheckpoint saved. Processed: {processed_count}, Failed: {len(error_data)}")
    
    # Final processing
    print(f"\nProcessing complete. Total: {len(file_infos)}, Success: {processed_count}, Failed: {len(error_data)}")
    
    if processed_count > 0:
        print("\nUpdating MHTML with new links...")
        soup = BeautifulSoup(html_content, 'html.parser')
        url_mapping = {m['original_url']: m['new_url'] for m in mapping_data}
        
        for a in soup.find_all('a', href=True):
            if a['href'] in url_mapping:
                a['href'] = url_mapping[a['href']]
        
        new_mhtml_path = create_new_mhtml(MHTML_FILE, str(soup))
        print(f"Updated MHTML created: {new_mhtml_path}")
    
    save_checkpoint(mapping_data, error_data)
    
    if error_data:
        print("\nFailed files (see error_log.csv for details):")
        for error in error_data[-10:]:
            print(f"- {error['url']}: {error['error']}")

if __name__ == '__main__':
    main()