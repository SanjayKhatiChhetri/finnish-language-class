from bs4 import BeautifulSoup, Tag
from .models import StreamItem, StreamItemType, Attachment, AttachmentType, WeeklyData
from .config import Config
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from collections import defaultdict
from typing import List, Dict, Optional, Tuple
import re
import logging
import json
from urllib.parse import urlparse, parse_qs

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClassroomParser:
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'lxml')
        self._validate_html_structure()
        
    def _validate_html_structure(self) -> None:
        """Perform basic HTML structure validation"""
        required_classes = ['qhnNic', 'LBlAUc', 'Aopndd', 'TIunU']
        containers = self.soup.select('div[data-stream-item-id]')
        
        if not containers:
            logger.warning("No stream item containers found - HTML structure may have changed")
            
        # Check for expected class combinations
        valid_containers = 0
        for container in containers:
            if all(cls in container.get('class', []) for cls in required_classes):
                valid_containers += 1
                
        if valid_containers == 0 and containers:
            logger.warning(f"Found {len(containers)} containers but none match expected class structure")
        
        logger.info(f"HTML validation: {valid_containers}/{len(containers)} containers validated")
        
    def parse_stream_items(self) -> List[StreamItem]:
        """Parse all stream items from the HTML content with enhanced error handling"""
        items = []
        
        # Primary selector based on actual HTML structure
        primary_selector = 'div[data-stream-item-id].qhnNic.LBlAUc.Aopndd.TIunU'
        containers = self.soup.select(primary_selector)
        
        # Fallback selector if primary fails
        if not containers:
            logger.warning("Primary selector failed, trying fallback")
            containers = self.soup.select('div[data-stream-item-id]')
        
        logger.info(f"Found {len(containers)} stream item containers")
        
        for i, container in enumerate(containers):
            try:
                item = self._parse_single_item(container)
                if item:
                    items.append(item)
                    logger.debug(f"Successfully parsed item {i+1}: {item.id}")
                else:
                    logger.warning(f"Failed to parse item {i+1}")
            except Exception as e:
                logger.error(f"Error parsing item #{i+1}: {str(e)}", exc_info=True)
                continue
                
        logger.info(f"Successfully parsed {len(items)} items")
        return items

    def _parse_single_item(self, container: Tag) -> Optional[StreamItem]:
        """Parse a single stream item container with comprehensive error handling"""
        try:
            # Extract basic metadata
            item_id = container.get('data-stream-item-id', '')
            if not item_id:
                logger.warning("Skipping item without ID")
                return None
                
            author = self._extract_author(container)
            date_str = self._extract_date(container)
            content = self._extract_content(container)
            attachments = self._extract_attachments(container)
            
            # Determine item type
            item_type = self._determine_item_type(container)
            
            # Check if deleted
            deleted = bool(container.select('.deleted-text'))
            
            return StreamItem(
                id=item_id,
                type=item_type,
                author=author,
                date=date_str,
                deleted=deleted,
                content=content,
                attachments=attachments
            )
            
        except Exception as e:
            logger.error(f"Failed to parse container: {str(e)}")
            return None

    def _extract_author(self, container: Tag) -> str:
        """Extract author name with multiple fallback strategies"""
        # Strategy 1: Direct author span (most reliable)
        author_span = container.select_one('span.YVvGBb.asQXV')
        if author_span:
            author_text = author_span.get_text(strip=True)
            # Clean up action text patterns
            patterns_to_remove = [
                r'\s+posted\s+a\s+new\s+assignment:.*$',
                r'\s+posted\s+a\s+new\s+announcement:.*$',
                r'\s+posted.*$'
            ]
            for pattern in patterns_to_remove:
                author_text = re.sub(pattern, '', author_text, flags=re.IGNORECASE)
            
            if author_text.strip():
                return author_text.strip()
        
        # Strategy 2: Try multiple author selectors
        author_selectors = [
            'div.GQW44b span.YVvGBb',
            'div.lziZub span.YVvGBb',
            'div[role="listitem"] span:first-child'
        ]
        
        for selector in author_selectors:
            element = container.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                # Filter out obviously non-author text
                if text and not any(word in text.lower() for word in ['assignment', 'announcement', 'created', 'posted']):
                    return text
        
        # Strategy 3: Look for profile image alt text or nearby text
        img = container.select_one('img.tnyRnb')
        if img and img.get('alt'):
            return img.get('alt')
        
        logger.warning("Could not extract author from container")
        return "Unknown Author"
    
    def _extract_date(self, container: Tag) -> str:
        """Extract date with enhanced parsing and multiple selector strategies"""
        # Strategy 1: Look for aria-hidden date elements (most reliable)
        date_selectors = [
            'span[aria-hidden="true"]',
            'span.PazDv',
            'span.IMvYId span.PazDv',
            'div.IMvYId span'
        ]
        
        for selector in date_selectors:
            elements = container.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and self._looks_like_date(text):
                    return self._clean_date_text(text)
        
        # Strategy 2: Look in header areas
        header_area = container.select_one('div.lziZub, div.GQW44b')
        if header_area:
            date_texts = header_area.find_all(text=True)
            for text in date_texts:
                cleaned = text.strip()
                if cleaned and self._looks_like_date(cleaned):
                    return self._clean_date_text(cleaned)
        
        logger.warning("Could not extract date from container")
        return ""

    def _looks_like_date(self, text: str) -> bool:
        """Check if text looks like a date"""
        # Remove common prefixes
        clean_text = re.sub(r'^(Created|Posted|Due|Assignment:|Announcement:)\s*', '', text, flags=re.IGNORECASE)
        
        # Date patterns
        date_patterns = [
            r'\d{1,2}\s+\w{3,9}\s+\d{4}',  # 27 Feb 2023
            r'\w{3,9}\s+\d{1,2},?\s+\d{4}',  # Feb 27, 2023
            r'\d{1,2}[./]\d{1,2}[./]\d{4}',  # 27/02/2023 or 27.02.2023
            r'\d{4}-\d{1,2}-\d{1,2}',  # 2023-02-27
        ]
        
        return any(re.search(pattern, clean_text) for pattern in date_patterns)

    def _clean_date_text(self, date_str: str) -> str:
        """Clean and normalize date text"""
        # Remove prefixes
        prefixes = ["Assignment:", "Announcement:", "Created", "Posted", "Due"]
        for prefix in prefixes:
            if prefix in date_str:
                date_str = date_str.replace(prefix, "").replace('"', '').strip()
        
        # Remove bracketed content like (Edited)
        date_str = re.sub(r'\s*\(.*?\)$', '', date_str)
        
        # Handle "Week of" format
        week_match = re.search(r'Week of\s+(.+)', date_str, re.IGNORECASE)
        if week_match:
            return week_match.group(1).strip()
        
        return date_str.strip()

    def _extract_content(self, container: Tag) -> str:
        """Extract and clean content with enhanced assignment detection"""
        # Try assignment-specific content extraction first
        if self._is_assignment_item(container):
            return self._extract_assignment_content(container)
        
        # Existing content extraction strategies
        content_selectors = [
            'div.pco8Kc.obylVb.j70YMc > span',
            'div.pco8Kc.obylVb.j70YMc',
            'div.n8F6Jd div.pco8Kc span',
            'div[role="listitem"] > div > div > div',
        ]
        
        for selector in content_selectors:
            content_element = container.select_one(selector)
            if content_element:
                return self._clean_content(content_element)
        
        # Last resort strategies
        return self._extract_content_fallback(container)

    def _is_assignment_item(self, container: Tag) -> bool:
        """Check if item is an assignment with specific UI markers"""
        return bool(
            container.select('svg.NMm5M.hhikbc') or  # Assignment icon
            container.select('div[aria-label*="Assignment"]') or
            'Assignment:' in container.get_text()
        )

    def _extract_assignment_content(self, container: Tag) -> str:
        """Specialized content extraction for assignment items"""
        # Strategy 1: Extract from assignment title
        title_element = container.select_one('div.lziZub h2 span.PazDv, div.GQW44b h2 span.PazDv')
        if title_element:
            return self._clean_content(title_element)
        
        # Strategy 2: Extract from aria-label
        aria_label = container.select_one('div[aria-label]')
        if aria_label and 'Assignment:' in aria_label.get('aria-label', ''):
            return aria_label['aria-label'].replace('Assignment:', '').strip()
        
        # Strategy 3: Extract from author text
        author_text = container.select_one('span.YVvGBb.asQXV')
        if author_text and 'assignment:' in author_text.get_text().lower():
            text = author_text.get_text(strip=True)
            return re.sub(r'.*assignment:\s*', '', text, flags=re.IGNORECASE)
        
        return "Assignment"

    def _extract_content_fallback(self, container: Tag) -> str:
        """Fallback content extraction strategies"""
        # Look for any substantial text content
        text_elements = container.find_all(text=True, recursive=True)
        substantial_text = []
        for text in text_elements:
            cleaned = text.strip()
            if len(cleaned) > 10 and not self._is_metadata_text(cleaned):
                substantial_text.append(cleaned)
        
        if substantial_text:
            return ' '.join(substantial_text[:3])
        
        return ""

    def _is_metadata_text(self, text: str) -> bool:
        """Check if text is likely metadata rather than content"""
        metadata_indicators = [
            'created', 'posted', 'assignment', 'announcement', 'pdf', 'video',
            'google docs', 'attachment', 'view', 'edit', 'download'
        ]
        return any(indicator in text.lower() for indicator in metadata_indicators)

    def _determine_item_type(self, container: Tag) -> StreamItemType:
        """Determine if item is announcement or assignment with enhanced detection"""
        # Method 1: Check for explicit data attributes
        if container.select('div[data-assignment-id]') or container.get('data-assignment-id'):
            return StreamItemType.ASSIGNMENT
        if container.select('div[data-announcement-id]') or container.get('data-announcement-id'):
            return StreamItemType.ANNOUNCEMENT
            
        # Method 2: Check for assignment-specific UI elements
        assignment_indicators = [
            'svg.NMm5M.hhikbc',  # Assignment clipboard icon
            'div[role="button"][aria-label*="assignment"]',
            'div[aria-label*="Assignment:"]',
        ]
        
        for indicator in assignment_indicators:
            if container.select(indicator):
                return StreamItemType.ASSIGNMENT
        
        # Method 3: Check text content for type indicators
        all_text = container.get_text().lower()
        if 'assignment:' in all_text or 'posted a new assignment' in all_text:
            return StreamItemType.ASSIGNMENT
        if 'announcement:' in all_text or 'posted a new announcement' in all_text:
            return StreamItemType.ANNOUNCEMENT
        
        # Method 4: Check for assignment-specific classes
        if container.select('.xWw7yd.h7Ww0.DkDwHe'):  # Assignment-specific styling
            return StreamItemType.ASSIGNMENT
            
        # Default to announcement
        return StreamItemType.ANNOUNCEMENT

    def _extract_attachments(self, container: Tag) -> List[Attachment]:
        """Parse all attachments with enhanced detection and validation"""
        attachments = []
        
        # Find all attachment containers
        attachment_selectors = [
            'div.luto0c',  # Primary attachment container
            'div[data-attachment-id]',  # Fallback by attribute
        ]
        
        attachment_divs = []
        for selector in attachment_selectors:
            divs = container.select(selector)
            if divs:
                attachment_divs = divs
                break
        
        logger.debug(f"Found {len(attachment_divs)} potential attachments")
        
        for div in attachment_divs:
            try:
                attachment = self._parse_single_attachment(div)
                if attachment:
                    attachments.append(attachment)
            except Exception as e:
                logger.error(f"Error parsing attachment: {str(e)}")
                continue
                
        return attachments

    def _parse_single_attachment(self, div: Tag) -> Optional[Attachment]:
        """Parse a single attachment element with comprehensive validation"""
        # Find the main link
        link = div.find('a')
        if not link or not link.get('href'):
            logger.debug("Attachment div has no valid link")
            return None
            
        url = link['href']
        title = self._get_attachment_title(link, div)
        
        # Determine attachment type
        attachment_type = self._determine_attachment_type(div, url, title)
        
        # Validate and clean URL
        url = self._clean_attachment_url(url)
        
        # Additional validation
        if not url or url == '#':
            logger.debug("Invalid URL after cleaning")
            return None
            
        return Attachment(
            type=attachment_type,
            title=title,
            url=url
        )

    def _get_attachment_title(self, link: Tag, container: Tag) -> str:
        """Get attachment title with multiple fallback strategies"""
        # Strategy 1: Direct link text
        link_text = link.get_text(strip=True)
        if link_text and not link_text.lower().startswith('attachment'):
            return link_text
            
        # Strategy 2: aria-label
        aria_label = link.get('aria-label', '')
        if aria_label:
            # Clean up aria-label (remove "Attachment: Type: " prefix)
            clean_label = re.sub(r'^Attachment:\s*\w+:\s*', '', aria_label)
            if clean_label:
                return clean_label
                
        # Strategy 3: Look for title elements in container
        title_selectors = [
            '.lIHx8b',  # Common title class
            '.A6dC2c',  # Alternative title class
            'div[title]'  # Elements with title attribute
        ]
        
        for selector in title_selectors:
            element = container.select_one(selector)
            if element:
                title = element.get_text(strip=True) or element.get('title', '')
                if title:
                    return title
        
        # Strategy 4: Image alt text
        img = container.find('img')
        if img and img.get('alt'):
            return img['alt']
            
        # Strategy 5: Extract from URL
        try:
            from urllib.parse import urlparse
            parsed = urlparse(link['href'])
            if 'drive.google.com' in parsed.netloc:
                # Try to extract filename from Google Drive URL
                path_parts = parsed.path.split('/')
                if 'd' in path_parts:
                    idx = path_parts.index('d')
                    if idx + 1 < len(path_parts):
                        file_id = path_parts[idx + 1]
                        return f"Google Drive File ({file_id[:8]}...)"
        except Exception:
            pass
            
        return "Untitled Attachment"

    def _determine_attachment_type(self, div: Tag, url: str, title: str) -> AttachmentType:
        """Determine attachment type using multiple detection strategies"""
        # Strategy 1: Check icon images
        icon_img = div.select_one('div.rzTfPe img, img[role="presentation"]')
        if icon_img:
            icon_src = icon_img.get('src', '').lower()
            if 'pdf' in icon_src:
                return AttachmentType.PDF
            elif 'document' in icon_src:
                return AttachmentType.DOCS
            elif 'video' in icon_src:
                return AttachmentType.VIDEO
            elif 'image' in icon_src or 'picture' in icon_src:
                return AttachmentType.IMAGE
            elif 'audio' in icon_src:
                return AttachmentType.VIDEO  # Treat audio as video for simplicity
        
        # Strategy 2: Check type indicators in container
        type_indicator = div.select_one('.kRYv9b')
        if type_indicator:
            type_text = type_indicator.get_text(strip=True).lower()
            type_mapping = {
                'pdf': AttachmentType.PDF,
                'google docs': AttachmentType.DOCS,
                'video': AttachmentType.VIDEO,
                'image': AttachmentType.IMAGE,
                'audio': AttachmentType.VIDEO,
            }
            for key, attachment_type in type_mapping.items():
                if key in type_text:
                    return attachment_type
        
        # Strategy 3: URL pattern analysis
        url_lower = url.lower()
        
        # File extension patterns
        if any(ext in url_lower for ext in ['.pdf']):
            return AttachmentType.PDF
        elif any(ext in url_lower for ext in ['.doc', '.docx', '.rtf', '.odt']):
            return AttachmentType.DOCS
        elif any(ext in url_lower for ext in ['.mp4', '.avi', '.mov', '.wmv', '.mp3', '.wav']):
            return AttachmentType.VIDEO
        elif any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.bmp']):
            return AttachmentType.IMAGE
            
        # Domain patterns
        if any(domain in url_lower for domain in ['youtube.com', 'youtu.be', 'vimeo.com']):
            return AttachmentType.VIDEO
        elif 'docs.google.com' in url_lower:
            return AttachmentType.DOCS
        elif 'drive.google.com' in url_lower:
            # Try to determine from Google Drive mime type
            mime_type = div.select_one('[data-mime-type]')
            if mime_type:
                mime = mime_type.get('data-mime-type', '').lower()
                if 'pdf' in mime:
                    return AttachmentType.PDF
                elif 'video' in mime:
                    return AttachmentType.VIDEO
                elif 'image' in mime:
                    return AttachmentType.IMAGE
                elif any(doc_type in mime for doc_type in ['document', 'kix', 'msword']):
                    return AttachmentType.DOCS
            return AttachmentType.DOCS  # Default for Drive links
            
        # Strategy 4: Title-based detection
        title_lower = title.lower()
        if any(ext in title_lower for ext in ['.pdf', 'pdf']):
            return AttachmentType.PDF
        elif any(word in title_lower for word in ['video', 'recording', 'mp4']):
            return AttachmentType.VIDEO
        elif any(word in title_lower for word in ['image', 'photo', 'png', 'jpg']):
            return AttachmentType.IMAGE
        elif any(word in title_lower for word in ['doc', 'document', 'slide']):
            return AttachmentType.DOCS
            
        return AttachmentType.LINK

    def _clean_attachment_url(self, url: str) -> str:
        """Clean and normalize attachment URLs with enhanced Google Drive support"""
        if not url:
            return ""
            
        # Remove tracking parameters
        clean_url = re.sub(r'[&?]utm_[^&]*', '', url)
        clean_url = re.sub(r'[&?]fbclid=[^&]*', '', clean_url)
        
        # Decode common URL encodings
        clean_url = clean_url.replace('%20', ' ').replace('%2F', '/')
        
        # Normalize Google Drive URLs
        if 'drive.google.com' in clean_url:
            # Extract file ID from various Google Drive URL formats
            file_id_patterns = [
                r'/file/d/([a-zA-Z0-9_-]+)',
                r'id=([a-zA-Z0-9_-]+)',
                r'/d/([a-zA-Z0-9_-]+)'
            ]
            
            for pattern in file_id_patterns:
                match = re.search(pattern, clean_url)
                if match:
                    file_id = match.group(1)
                    return f"https://drive.google.com/file/d/{file_id}/view"
        
        # Normalize Google Docs URLs
        elif 'docs.google.com' in clean_url:
            doc_id_match = re.search(r'/document/d/([a-zA-Z0-9_-]+)', clean_url)
            if doc_id_match:
                doc_id = doc_id_match.group(1)
                return f"https://docs.google.com/document/d/{doc_id}/edit"
        
        # Normalize YouTube URLs
        elif any(domain in clean_url for domain in ['youtube.com', 'youtu.be']):
            video_id_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]+)', clean_url)
            if video_id_match:
                video_id = video_id_match.group(1)
                return f"https://www.youtube.com/watch?v={video_id}"
                
        return clean_url

    def _clean_content(self, content_element: Tag) -> str:
        """Convert HTML content to clean text with enhanced formatting"""
        if not content_element:
            return ""
            
        if Config.PRESERVE_HTML:
            return str(content_element)
            
        # Handle line breaks and paragraphs
        for br in content_element.find_all('br'):
            br.replace_with('\n')
            
        for p in content_element.find_all('p'):
            p.append('\n\n')
            
        # Handle bold text markers
        for b in content_element.find_all(['b', 'strong']):
            text = b.get_text()
            b.replace_with(f"**{text}**")
            
        # Handle italic text markers
        for i in content_element.find_all(['i', 'em']):
            text = i.get_text()
            i.replace_with(f"*{text}*")
            
        # Extract text with preserved whitespace
        text = content_element.get_text(separator='\n', strip=True)
        
        # Clean and normalize whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)  # Reduce excessive newlines
        text = re.sub(r'[ \t]{2,}', ' ', text)  # Collapse multiple spaces
        text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)  # Trim lines
        
        return text.strip()

    def group_by_weeks(self, items: List[StreamItem]) -> Dict[str, WeeklyData]:
        """Group items by week with enhanced date parsing and validation"""
        week_groups = defaultdict(list)
        valid_items = []
        date_format_errors = 0
        
        for item in items:
            if not item.date:
                logger.debug(f"Item {item.id} has no date, skipping")
                continue
                
            try:
                parsed_date = self._parse_date_enhanced(item.date)
                if parsed_date:
                    week_start = self._get_week_start(parsed_date)
                    week_key = week_start.strftime(Config.WEEK_KEY_FORMAT)
                    week_groups[week_key].append(item)
                    valid_items.append(item)
                else:
                    date_format_errors += 1
                    logger.warning(f"Could not parse date '{item.date}' for item {item.id}")
            except Exception as e:
                date_format_errors += 1
                logger.warning(f"Date parsing error for '{item.date}': {str(e)}")
                continue
        
        logger.info(f"Grouped {len(valid_items)} items into {len(week_groups)} weeks "
                    f"({date_format_errors} date errors)")
        
        # Create weekly data objects with enhanced naming
        weekly_data = {}
        sorted_weeks = sorted(week_groups.keys())
        
        for i, week_key in enumerate(sorted_weeks):
            # Sort items within week by date (newest first)
            week_items = sorted(
                week_groups[week_key], 
                key=lambda x: self._parse_date_enhanced(x.date) or datetime.min,
                reverse=True
            )
            
            # Generate a more descriptive week name
            week_start = datetime.strptime(week_key, Config.WEEK_KEY_FORMAT)
            week_end = week_start + timedelta(days=6)
            display_name = f"Week {i+1} ({week_start.strftime('%b %d')} - {week_end.strftime('%b %d')})"
            
            weekly_data[week_key] = WeeklyData(
                display_name=display_name,
                items=week_items
            )
        
        return weekly_data
        
    def _parse_date_enhanced(self, date_str: str) -> Optional[datetime]:
        """Enhanced date parsing with multiple format support and validation"""
        if not date_str or not date_str.strip():
            return None
            
        original_date = date_str
        
        # Clean the date string
        date_str = self._clean_date_text(date_str)
        
        # Handle special formats
        # "Week of" format
        week_match = re.search(r'Week of\s+(.+)', date_str, re.IGNORECASE)
        if week_match:
            date_str = week_match.group(1).strip()
        
        # "Due:" prefix
        if date_str.lower().startswith('due:'):
            date_str = date_str[4:].strip()
            
        # Try configured formats first
        for fmt in Config.DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Try dateutil parser with enhanced month name support
        try:
            # Handle Finnish month names
            finnish_months = {
                'tammi': 'Jan', 'helmi': 'Feb', 'maalis': 'Mar', 
                'huhti': 'Apr', 'touko': 'May', 'kesä': 'Jun',
                'heinä': 'Jul', 'elo': 'Aug', 'syys': 'Sep',
                'loka': 'Oct', 'marras': 'Nov', 'joulu': 'Dec'
            }
            
            normalized_date = date_str.lower()
            for fin, eng in finnish_months.items():
                if fin in normalized_date:
                    normalized_date = normalized_date.replace(fin, eng)
                    break
            
            # Try parsing with fuzzy matching
            return date_parser.parse(normalized_date, fuzzy=True)
            
        except Exception as e:
            logger.debug(f"dateutil failed for '{original_date}': {str(e)}")
            
        # Last resort: try to extract year, month, day with regex
        date_match = re.search(r'(\d{1,2})\s+(\w{3,})\s+(\d{4})', date_str)
        if date_match:
            day, month_str, year = date_match.groups()
            try:
                month_num = datetime.strptime(month_str[:3], '%b').month
                return datetime(int(year), month_num, int(day))
            except ValueError:
                pass
        
        logger.debug(f"All date parsing methods failed for: '{original_date}'")
        return None

    def _get_week_start(self, date: datetime) -> datetime:
        """Calculate week start date based on config with validation"""
        try:
            # Adjust week start day (0 = Monday, 6 = Sunday)
            days_diff = (date.weekday() - Config.WEEK_START_DAY) % 7
            week_start = date - timedelta(days=days_diff)
            return week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        except Exception as e:
            logger.error(f"Error calculating week start for {date}: {str(e)}")
            return date.replace(hour=0, minute=0, second=0, microsecond=0)

    def _validate_output_schema(self, weekly_data: Dict[str, WeeklyData]) -> bool:
        """Validate the output data structure"""
        try:
            for week_key, data in weekly_data.items():
                # Validate week key format
                datetime.strptime(week_key, Config.WEEK_KEY_FORMAT)
                
                # Validate data structure
                if not isinstance(data.display_name, str):
                    logger.error(f"Invalid display_name type for week {week_key}")
                    return False
                    
                if not isinstance(data.items, list):
                    logger.error(f"Invalid items type for week {week_key}")
                    return False
                    
                # Validate each item
                for item in data.items:
                    if not all(hasattr(item, attr) for attr in ['id', 'type', 'author', 'date', 'content', 'attachments']):
                        logger.error(f"Invalid item structure in week {week_key}")
                        return False
                        
            logger.info("Output schema validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Schema validation failed: {str(e)}")
            return False

    def generate_typescript(self, weekly_data: Dict[str, WeeklyData]) -> str:
        """Generate TypeScript code with snake_case naming and enhanced structure"""
        
        # Validate data before generation
        if not self._validate_output_schema(weekly_data):
            logger.warning("Schema validation failed, proceeding with generation anyway")
        
        ts_lines = [
            "// Auto-generated by Enhanced Classroom Parser",
            f"// Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"// Total weeks: {len(weekly_data)}",
            f"// Total items: {sum(len(data.items) for data in weekly_data.values())}",
            "",
            "export enum StreamItemType {",
            f"  {StreamItemType.ANNOUNCEMENT.name} = '{StreamItemType.ANNOUNCEMENT.value}',",
            f"  {StreamItemType.ASSIGNMENT.name} = '{StreamItemType.ASSIGNMENT.value}',",
            "}",
            "",
            "export enum AttachmentType {",
            *[f"  {at.name} = '{at.value}'," for at in AttachmentType],
            "}",
            "",
            "export interface Attachment {",
            "  type: AttachmentType;",
            "  title: string;",
            "  url: string;",
            "}",
            "",
            "export interface StreamItem {",
            "  id: string;",
            "  type: StreamItemType;",
            "  author: string;",
            "  date: string;",
            "  deleted: boolean;",
            "  content: string;",
            "  attachments: Attachment[];",
            "}",
            "",
            "export interface WeeklyData {",
            "  display_name: string;",
            "  items: StreamItem[];",
            "}",
            "",
            "// Statistics",
            f"export const parser_stats = {{",
            f"  total_weeks: {len(weekly_data)},",
            f"  total_items: {sum(len(data.items) for data in weekly_data.values())},",
            f"  total_attachments: {sum(len(att) for data in weekly_data.values() for item in data.items for att in [item.attachments])},",
            f"  generated_at: '{datetime.now().isoformat()}',",
            f"}};",
            "",
            "export const classroom_data: Record<string, WeeklyData> = {"
        ]
        
        # Generate data for each week
        for week_key, data in weekly_data.items():
            ts_lines.append(f"  '{week_key}': {{")
            ts_lines.append(f"    display_name: '{self._escape_typescript_string(data.display_name)}',")
            ts_lines.append("    items: [")
            
            for item in data.items:
                # Escape special characters in strings for TypeScript
                author = self._escape_typescript_string(item.author)
                content = self._escape_typescript_string(item.content)
                date = self._escape_typescript_string(item.date)
                
                # Format attachments with proper escaping
                attachments = []
                for att in item.attachments:
                    title = self._escape_typescript_string(att.title)
                    url = self._escape_typescript_string(att.url)
                    attachments.append(
                        f"{{ type: AttachmentType.{att.type.name}, "
                        f"title: `{title}`, "
                        f"url: `{url}` }}"
                    )
                
                attachments_str = ", ".join(attachments)
                
                ts_lines.extend([
                    "      {",
                    f"        id: '{item.id}',",
                    f"        type: StreamItemType.{item.type.name},",
                    f"        author: `{author}`,",
                    f"        date: '{date}',",
                    f"        deleted: {str(item.deleted).lower()},",
                    f"        content: `{content}`,",
                    f"        attachments: [{attachments_str}]",
                    "      },"
                ])
            
            ts_lines.append("    ]")
            ts_lines.append("  },")
        
        ts_lines.extend([
            "};",
            "",
            "// Helper functions for data access",
            "export function get_week_data(week_key: string): WeeklyData | undefined {",
            "  return classroom_data[week_key];",
            "}",
            "",
            "export function get_all_items(): StreamItem[] {",
            "  return Object.values(classroom_data).flatMap(week => week.items);",
            "}",
            "",
            "export function get_items_by_type(type: StreamItemType): StreamItem[] {",
            "  return get_all_items().filter(item => item.type === type);",
            "}",
            "",
            "export function get_items_by_author(author: string): StreamItem[] {",
            "  return get_all_items().filter(item => item.author === author);",
            "}",
            "",
            "export function search_items(query: string): StreamItem[] {",
            "  const lowercaseQuery = query.toLowerCase();",
            "  return get_all_items().filter(item => ",
            "    item.content.toLowerCase().includes(lowercaseQuery) ||",
            "    item.author.toLowerCase().includes(lowercaseQuery) ||",
            "    item.attachments.some(att => att.title.toLowerCase().includes(lowercaseQuery))",
            "  );",
            "}",
            "",
            "// Export for debugging",
            "export const debug_info = {",
            "  parser_version: '2.0.0-enhanced',",
            "  features: ['enhanced_date_parsing', 'google_drive_support', 'schema_validation', 'snake_case_naming'],",
            "  week_keys: Object.keys(classroom_data).sort(),",
            "};",
        ])
        
        return "\n".join(ts_lines)

    def _escape_typescript_string(self, text: str) -> str:
        """Escape special characters for TypeScript template literals"""
        if not text:
            return ""
            
        # Escape backticks and template literal expressions
        escaped = text.replace('`', '\\`').replace('${', '\\${')
        
        # Escape other problematic characters
        escaped = escaped.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r')
        
        return escaped

    def get_parsing_statistics(self) -> Dict[str, any]:
        """Get statistics about the parsing process"""
        containers = self.soup.select('div[data-stream-item-id]')
        
        stats = {
            'total_containers_found': len(containers),
            'html_structure_valid': len(containers) > 0,
            'timestamp': datetime.now().isoformat(),
            'parser_version': '2.0.0-enhanced'
        }
        
        return stats

    def validate_and_repair_html(self) -> Tuple[bool, List[str]]:
        """Validate HTML structure and attempt basic repairs"""
        issues = []
        repaired = False
        
        # Check for required elements
        stream_items = self.soup.select('div[data-stream-item-id]')
        if not stream_items:
            issues.append("No stream items found")
            
        # Check for malformed structure
        for i, item in enumerate(stream_items):
            if not item.get('data-stream-item-id'):
                issues.append(f"Item {i} missing stream-item-id")
                
        # Attempt basic repairs
        if issues:
            logger.warning(f"Found {len(issues)} HTML structure issues")
            
        return len(issues) == 0, issues