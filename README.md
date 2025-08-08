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
