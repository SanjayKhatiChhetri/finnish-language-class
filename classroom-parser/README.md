# Google Classroom HTML Parser

This tool parses exported Google Classroom HTML files and converts them into structured TypeScript data.

## Features

- Parses announcements and assignments
- Extracts attachments (PDF, Video, Docs, Image, Link)
- Groups items by week
- Generates TypeScript interfaces and helper functions
- Handles Finnish date formats and Google Drive URLs

## Installation

1. Clone repository:
```bash
git clone https://github.com/SanjayKhatiChhetri/finnish-language-class/tree/tools/classroom-parser.git
cd classroom-parser
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Ensure you have Python 3.8 or higher installed.
   
## Usage

### Single File Processing
```bash
python -m src.main --input classroom.html --output data.ts
```

### Batch Processing
```bash
python -m src.main --input ./html_files --output ./ts_output
```

### Configuration
You can customize the behavior of the parser by modifying the `src/config.py` file. Key settings include:
```python
class Config:
    WEEK_START_DAY = 0  # Monday (0=Mon, 6=Sun)
    PRESERVE_HTML = False  # Set True to keep HTML formatting
    VALIDATE_URLS = True  # Validate attachment URLs
    # Add date formats as needed
```
## Output Structure
``` typescript
export enum StreamItemType { ... }
export enum AttachmentType { ... }
export interface Attachment { ... }
export interface StreamItem { ... }
export interface WeeklyData { ... }
export const classroom_data: Record<string, WeeklyData> = { ... }
```

## Troubleshooting
- Update CSS selectors in `parser.py` if Google Classroom UI changes
- Add new date formats to `Config.DATE_FORMATS` as needed
- Enable debug logging in `parser.py` for detailed processing info

### The parser includes robust features like:
- Enhanced date parsing with Finnish month support
- Google Drive URL normalization
- HTML structure validation
- Comprehensive error handling
- Schema validation before output
- Statistics generation


### To use the parser:
1. Export Google Classroom as HTML
2. Run the parser on the HTML files
3. Import the generated TS files into your application
4. Use the helper functions to access the data