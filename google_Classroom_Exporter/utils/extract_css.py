import os
import email
import re
from bs4 import BeautifulSoup
from email.header import decode_header

def extract_css_from_mhtml(mhtml_path, output_folder='extracted_css'):
    """
    Extract CSS content from an MHTML file and save to separate files.
    
    Args:
        mhtml_path (str): Path to the MHTML file
        output_folder (str): Folder to save extracted CSS files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Read the MHTML file
    with open(mhtml_path, 'rb') as f:
        msg = email.message_from_binary_file(f)
    
    css_count = 0
    
    # Process each part of the MHTML
    for part in msg.walk():
        content_type = part.get_content_type()
        
        # Handle CSS content
        if content_type == 'text/css':
            css_count += 1
            payload = part.get_payload(decode=True)
            
            # Try to decode the payload
            try:
                css_content = payload.decode('utf-8')
            except UnicodeDecodeError:
                css_content = payload.decode('latin-1')
            
            # Get filename from Content-Location or generate one
            content_location = part.get('Content-Location', '')
            if content_location:
                filename = os.path.basename(content_location.split('?')[0])
            else:
                filename = f'stylesheet_{css_count}.css'
            
            # Ensure filename ends with .css
            if not filename.lower().endswith('.css'):
                filename += '.css'
            
            # Clean filename
            filename = re.sub(r'[^\w\-_. ]', '_', filename)
            
            # Save CSS file
            output_path = os.path.join(output_folder, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
            print(f"Extracted CSS: {filename}")
        
        # Also extract inline CSS from HTML
        elif content_type == 'text/html':
            payload = part.get_payload(decode=True)
            
            try:
                html_content = payload.decode('utf-8')
            except UnicodeDecodeError:
                html_content = payload.decode('latin-1')
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract <style> tags
            for i, style in enumerate(soup.find_all('style'), 1):
                if style.string:
                    filename = f'inline_styles_{i}.css'
                    output_path = os.path.join(output_folder, filename)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(style.string)
                    print(f"Extracted inline CSS: {filename}")
    
    print(f"\nExtraction complete. CSS files saved to: {os.path.abspath(output_folder)}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract CSS from MHTML file')
    parser.add_argument('mhtml_file', help='Path to the MHTML file')
    parser.add_argument('-o', '--output', help='Output folder for CSS files', default='extracted_css')
    args = parser.parse_args()
    
    extract_css_from_mhtml(args.mhtml_file, args.output)