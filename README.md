# Google Classroom Resource Downloader

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
