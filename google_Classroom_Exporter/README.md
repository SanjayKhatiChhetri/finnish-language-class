# Google Classroom Resource Downloader

display: block !important;
overflow: auto !important;
max-height: 100% !important;

A tool to download files from Google Classroom (via MHTML export) and transfer them to another Google Drive account.

## Features

- Parses Google Classroom MHTML exports to extract file links.
- Downloads files from a source Google Drive account.
- Uploads files to a destination Google Drive account.
- Updates the MHTML file with new links.
- Resume capability for interrupted transfers.
- Error logging and retry mechanism.

## Requirements

1. **Python**: Python 3.7 or higher.
2. **Google API Credentials**: Two sets of credentials for source and destination accounts.
3. **Required Python Packages**: Install dependencies using:
   ```sh
   pip install -r requirements.txt
   ```

## Setup

### Step 1: Install Dependencies

Run the following command to install the required Python packages:

```sh
pip install -r requirements.txt
```

### Step 2: Create Google API Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Enable the **Google Drive API**:
   - Navigate to **APIs & Services > Library**.
   - Search for "Google Drive API" and enable it.
4. Create **OAuth 2.0 Credentials**:
   - Navigate to **APIs & Services > Credentials**.
   - Click **Create Credentials** and select **OAuth 2.0 Client IDs**.
   - Configure the consent screen:
     - Select **External** for user type.
     - Fill in the required fields (e.g., app name, email).
     - Save and continue.
   - Set the application type to **Desktop App**.
   - Download the credentials JSON file and save it as:
     - `source_credentials.json` (for the account with original files).
     - `dest_credentials.json` (for the account receiving files).

### Step 3: Prepare Your MHTML File

1. Export your Google Classroom as an MHTML file:
   - Open Google Classroom in Chrome or Edge.
   - Use the **Save As** option to save the page as an MHTML file.
2. Place the MHTML file in the project directory.

## Usage

### Basic Command

Run the script using:

```sh
python google_classrom_downloader.py
```

### Options

- `--resume`: Resume an interrupted transfer.
- `--retry-failed`: Retry only files that failed previously.

### Workflow

1. The script will parse your MHTML file for Google Drive links.
2. It will download files from the source account.
3. The files will be uploaded to the destination account.
4. A new MHTML file will be created with updated links.

> **Note**: The first run will require you to authenticate both accounts in your browser.

### Output Files

- **downloads/**: Temporary folder for downloaded files.
- **uploaded_files/**:
  - `updated_[original].mhtml`: New MHTML file with updated links.
  - `file_mapping.csv`: Mapping of old URLs to new URLs.
  - `error_log.csv`: Any errors encountered during the process.

## Notes

- The script handles Google Docs/Sheets/Slides by converting them to Office formats.
- Files are renamed if duplicates exist (appends `_1`, `_2`, etc.).
- Large transfers may take significant time (progress is shown).
- If interrupted, use `--resume` to continue where you left off.

## Troubleshooting

- **Authentication Errors**: Delete `source_token.json` or `dest_token.json` and try again.
- **API Quota Errors**: Wait and retry later.
- **File Not Found**: Ensure the source account has access to all files.
- Check `error_log.csv` for specific failure details.

## License

This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

## Acknowledgments

- Google APIs for Drive integration.
- BeautifulSoup for HTML parsing.

## Project Folder Structure

```
.
├── .gitignore
├── converted.html
├── dest_credentials.json
├── dest_token.json
├── google_classrom_downloader.py
├── README.md
├── requirements.txt
├── source_credentials.json
├── source_token.json
├── cred/
│   ├── dest_credentials.json
│   ├── dest_token.json
│   ├── source_credentials.json
│   └── source_token.json
├── downloaded/
│   ├── -minen-muoto, lumikot.docx
│   ├── 01 Minä - Google Docs.pdf
│   ├── 01A. Minä - Google Docs.pdf
│   ├── 01A. Minä.pdf
│   ├── 01B. Minä - Google Docs.pdf
│   ├── 02A. Perhe - Google Docs_1.pdf
│   └── ...
├── downloads/
├── resources/
├── source file/
├── test_file/
│   ├── converted.html
│   └── mhtmlToMhtml.py
├── uploaded_files/
├── utils/
│   ├── directory_cleaner.py
│   └── extract_css.py
```

rewrite script in python script so that 
- source and destination google drive is same now.
- it can take the source_index_html_file(with corrupt docs link) and extract file name and docs links  and other needed identifiers and  move docs to trash update necessary file_name, corrupt_old_link, corrupt_old_id, corrupt_delete_status in docx_mapping.csv file.
- In downloads folder there is docx file with same name, upload the file to gdrive and update the links in html file, provide with updated html file  and update uploaded_new_id, uploaded_new_link, new_upload_status in docx_mapping.csv file.


- 
============================================================
Processing file 857/1184: massa/masta/maan, lumikot
File ID: 16237hUfBR4Sz0x6v8yt-G0HtZkT9pleJ3SoAgK3BCxE
Original URL: https://docs.google.com/document/d/16237hUfBR4Sz0x6v8yt-G0HtZkT9pleJ3SoAgK3BCxE/edit?usp=classroom_web&authuser=0
Original file name: massa/masta/maan, lumikot
✗ Error processing file: No matching local file found for 'massa/masta/maan, lumikot'

TRY AGAIN WHEN ERROR PROCESSING FILES: NO MATCHING LOCAL FILE FOUND FOR


# Google Drive Resource Fixer

A powerful Python tool that automatically updates Google Drive links in HTML files by uploading local files to a centralized Google Drive folder, with intelligent duplicate detection and content consolidation.

## 🌟 Features

- **Smart Content Consolidation**: Automatically detects and consolidates duplicate content across different Google Drive links
- **Intelligent File Matching**: Uses advanced similarity algorithms with file type detection to match local files to Drive resources
- **Batch Processing**: Handles hundreds of files efficiently with progress tracking and checkpoint recovery
- **Resume Capability**: Can resume interrupted transfers and retry failed uploads
- **File Type Detection**: Recognizes Google Docs, Sheets, Slides, PDFs, videos, and other formats from HTML context
- **Automatic Downloads**: Can download missing files directly from Google Drive
- **Progress Tracking**: Real-time progress bars and detailed reporting
- **Error Handling**: Comprehensive error logging with retry mechanisms

## 📋 Requirements

### Python Packages
```bash
pip install -r requirements.txt
```

Required packages:
- `google-api-python-client`
- `google-auth-httplib2` 
- `google-auth-oauthlib`
- `beautifulsoup4`
- `requests`

### Google Drive API Setup

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Google Drive API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Drive API" and enable it

3. **Create Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application"
   - Download the credentials file as `credentials.json`

4. **Place Credentials**:
   - Put `credentials.json` in the same directory as the script

## 📁 Directory Structure

```
project/
├── Gdrive_resource_fixer.py    # Main script
├── credentials.json            # Google API credentials
├── source_index.html          # HTML file with Google Drive links
├── downloads/                 # Local files folder
│   ├── document1.pdf
│   ├── spreadsheet1.xlsx
│   └── ...
├── uploaded_files/            # Output folder (auto-created)
│   ├── file_mapping.csv
│   ├── error_log.csv
│   ├── consolidation_report.csv
│   └── updated_index.html
└── requirements.txt
```

## 🚀 Usage

### Basic Usage

```bash
python Gdrive_resource_fixer.py
```

This will:
1. Parse `source_index.html` for Google Drive links
2. Match them with files in `downloads/` folder
3. Upload matched files to `classroom_Resource` folder in Google Drive
4. Create updated HTML with new links

### Command Line Options

```bash
# Resume interrupted processing
python Gdrive_resource_fixer.py --resume

# Download missing files from Google Drive first
python Gdrive_resource_fixer.py --download-missing

# Retry only failed uploads
python Gdrive_resource_fixer.py --retry-failed

# Preview what would be done (no changes)
python Gdrive_resource_fixer.py --dry-run

# Use custom file paths
python Gdrive_resource_fixer.py --html-file custom.html --downloads-folder ./files

# Disable duplicate consolidation
python Gdrive_resource_fixer.py --no-consolidation

# Show detected file types for debugging
python Gdrive_resource_fixer.py --show-types

# Reset authentication
python Gdrive_resource_fixer.py --reset-auth
```

### Advanced Examples

```bash
# Complete workflow with missing file downloads
python Gdrive_resource_fixer.py --download-missing --show-types

# Resume with retry for robustness
python Gdrive_resource_fixer.py --resume --retry-failed

# Process custom HTML with specific folder
python Gdrive_resource_fixer.py --html-file classroom.html --downloads-folder ./course_materials
```

## 🔧 How It Works

### 1. HTML Parsing
- Extracts all Google Drive links from HTML
- Detects file types from HTML context (Google Docs, PDFs, videos, etc.)
- Extracts file IDs and display names

### 2. Smart Consolidation
- Groups files by normalized content signatures
- Detects duplicates across different file IDs
- Selects best canonical names from duplicate groups
- Reduces redundant processing by up to 70%

### 3. Intelligent File Matching
- Normalizes filenames for better comparison
- Uses similarity scoring algorithms
- Matches file types from HTML context
- Handles Google Workspace format conversions

### 4. Upload & Update Process
- Creates/finds `classroom_Resource` folder in Google Drive
- Uploads files with public viewing permissions
- Converts Office docs to Google Workspace formats when appropriate
- Updates HTML with new public links

## 📊 Output Files

The script generates several useful output files in the `uploaded_files/` directory:

### `file_mapping.csv`
Complete mapping of original URLs to new URLs with metadata:
```csv
original_url,new_url,name,id,original_id,local_file,match_score,consolidated_from,file_types
```

### `error_log.csv` 
Detailed error information for failed uploads:
```csv
url,error,timestamp,file_id,original_name
```

### `consolidation_report.csv`
Report of duplicate content groups found and consolidated:
```csv
content_signature,canonical_name,selected_file_id,duplicate_count,all_file_ids,original_names,original_urls,file_types
```

### `updated_index.html`
Updated HTML file with all Google Drive links replaced with new public links

## 🛠️ Configuration

### File Type Detection
The script automatically detects file types from HTML context. You can customize type mappings in:

```python
HTML_TYPE_TO_EXTENSIONS = {
    'google docs': ['.docx', '.doc', '.txt'],
    'pdf': ['.pdf'],
    'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv'],
    # ... customize as needed
}
```

### Matching Sensitivity
Adjust matching thresholds:
```python
# Minimum similarity score for file matching (default: 0.3)
if local_file and score > 0.3:  # Lower = more permissive
```

### Processing Settings
```python
CHECKPOINT_INTERVAL = 10  # Save progress every N files
MAX_RETRIES = 3          # Retry failed uploads
RETRY_DELAY = 5          # Seconds between retries
```

## 🎯 Use Cases

### Educational Content Migration
- Migrate classroom resources from individual Google Drive accounts
- Consolidate duplicate assignments across multiple courses
- Create centralized resource repositories

### Corporate Document Management
- Standardize shared document libraries
- Remove duplicate training materials
- Create department-wide resource centers

### Website Content Updates
- Update HTML pages with broken Google Drive links
- Migrate from private to public sharing
- Batch process multiple course websites

## 🔍 Troubleshooting

### Authentication Issues
```bash
# Reset authentication
python Gdrive_resource_fixer.py --reset-auth

# Check credentials.json exists and is valid
ls -la credentials.json
```

### File Matching Problems
```bash
# Debug file type detection
python Gdrive_resource_fixer.py --show-types --dry-run

# Check similarity scores
# Look for match_score in output - scores below 0.3 indicate poor matches
```

### Missing Local Files
```bash
# Download missing files automatically
python Gdrive_resource_fixer.py --download-missing

# Check downloads folder structure
ls -la downloads/
```

### Processing Errors
```bash
# Retry failed uploads
python Gdrive_resource_fixer.py --retry-failed

# Resume interrupted processing
python Gdrive_resource_fixer.py --resume
```

## ⚠️ Important Notes

### Permissions
- Uploaded files get "anyone can view" permissions automatically
- Original Google Drive files remain unchanged
- New files are created in the `classroom_Resource` folder

### File Conversion
- Office documents (`.docx`, `.xlsx`, `.pptx`) are converted to Google Workspace formats
- PDFs and media files are uploaded as-is
- Original file extensions are preserved in filenames

### Rate Limits
- Google Drive API has rate limits - the script includes automatic retry logic
- Large batches may take time - use `--resume` for interrupted processing

### Duplicate Handling
- Content-based deduplication is enabled by default
- Use `--no-consolidation` to process all files individually
- Check `consolidation_report.csv` for duplicate analysis

## 📈 Performance Tips

### For Large Batches (100+ files):
1. Use `--dry-run` first to verify matching
2. Process in chunks using `--resume`
3. Monitor `error_log.csv` for issues
4. Use `--download-missing` to get files from Drive first

### For Better Matching:
1. Ensure local filenames are similar to Google Drive names
2. Use descriptive filenames (avoid generic names like "Document", "File")
3. Keep file extensions in local files when possible
4. Use `--show-types` to debug type detection

## 📝 Example Workflow

```bash
# Step 1: Check what would be processed
python Gdrive_resource_fixer.py --dry-run --show-types

# Step 2: Download any missing files
python Gdrive_resource_fixer.py --download-missing

# Step 3: Process all files with consolidation
python Gdrive_resource_fixer.py

# Step 4: If interrupted, resume processing
python Gdrive_resource_fixer.py --resume

# Step 5: Retry any failed uploads
python Gdrive_resource_fixer.py --retry-failed
```

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the tool.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Need Help?** 
- Check the error logs in `uploaded_files/error_log.csv`
- Use `--dry-run` to preview operations
- Enable `--show-types` for debugging file detection
- Try `--reset-auth` for authentication issues