import os
import shutil
import time

def get_terminal_height():
    """Get terminal height for display purposes (minimum 24 lines)"""
    try:
        import struct
        import fcntl
        import termios
        call = fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0))
        _, _, height, _ = struct.unpack('HHHH', call)
        return max(24, height)
    except:
        return 24

def get_terminal_width():
    """Get terminal width for table formatting (minimum 80 columns)"""
    try:
        import struct
        import fcntl
        import termios
        call = fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0))
        _, width, _, _ = struct.unpack('HHHH', call)
        return max(80, width)
    except:
        return 80

def format_size(size_bytes):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def format_time(timestamp):
    """Format timestamp to readable date"""
    return time.strftime('%Y-%m-%d %H:%M', time.localtime(timestamp))

def get_file_info(directory_path):
    """Collect information about all files in directory and subdirectories"""
    file_info = []
    total_size = 0
    total_files = 0
    
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    stat = os.stat(file_path)
                    file_size = stat.st_size
                    file_type = os.path.splitext(file)[1].upper() or "FILE"
                    
                    file_info.append({
                        'name': file,
                        'size': file_size,
                        'type': file_type,
                        'created': stat.st_ctime,
                        'modified': stat.st_mtime,
                        'path': file_path
                    })
                    
                    total_size += file_size
                    total_files += 1
                except Exception as e:
                    print(f"Error reading {file_path}: {str(e)}")
    
    return file_info, total_files, total_size

def display_file_table(file_info, max_rows=100):
    """Display files in a table format with columns"""
    terminal_width = get_terminal_width()
    
    # Calculate column widths
    name_width = min(40, (terminal_width - 60) // 2)
    type_width = 6
    size_width = 10
    date_width = 16
    
    # Header
    header = (f"{'#':<4} "
              f"{'Filename':<{name_width}} "
              f"{'Type':<{type_width}} "
              f"{'Size':>{size_width}} "
              f"{'Created':<{date_width}} "
              f"{'Modified':<{date_width}}")
    
    print("\n" + "=" * len(header))
    print(header)
    print("=" * len(header))
    
    # Rows
    terminal_height = get_terminal_height()
    rows_displayed = 0
    
    for i, file in enumerate(file_info[:max_rows], 1):
        row = (f"{i:<4} "
               f"{file['name'][:name_width]:<{name_width}} "
               f"{file['type']:<{type_width}} "
               f"{format_size(file['size']):>{size_width}} "
               f"{format_time(file['created']):<{date_width}} "
               f"{format_time(file['modified']):<{date_width}}")
        print(row)
        rows_displayed += 1
        
        # Pause every screen height - 4 rows (for header and prompt)
        if rows_displayed % (terminal_height - 4) == 0 and rows_displayed < max_rows:
            input("\nPress Enter to continue...")
            print("\n" + "=" * len(header))
            print(header)
            print("=" * len(header))
    
    if len(file_info) > max_rows:
        print(f"\nShowing {max_rows} of {len(file_info)} files. More files exist in subdirectories.")

def delete_directory_contents(directory_path):
    """Delete all files and subdirectories with confirmation"""
    try:
        if not os.path.exists(directory_path):
            print(f"Directory does not exist: {directory_path}")
            return False
        
        if not os.path.isdir(directory_path):
            print(f"Path is not a directory: {directory_path}")
            return False
        
        # Get file information
        file_info, total_files, total_size = get_file_info(directory_path)
        
        if total_files == 0:
            print(f"No files to delete in {directory_path}")
            return True
        
        # Display summary
        print("\n" + "=" * 50)
        print(f"Directory: {directory_path}")
        print(f"Total files: {total_files}")
        print(f"Total size: {format_size(total_size)}")
        print("=" * 50)
        
        # Display sample files
        if total_files > 0:
            display_file_table(file_info, max_rows=100)
            print("\nNote: All files in subdirectories will also be deleted.")
        
        # Confirm deletion
        confirm = input(f"\nAre you sure you want to delete ALL {total_files} files ({format_size(total_size)})? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Deletion cancelled.")
            return False
        
        # Perform deletion
        deleted_count = 0
        deleted_size = 0
        for root, dirs, files in os.walk(directory_path, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    os.unlink(file_path)
                    deleted_count += 1
                    deleted_size += file_size
                except Exception as e:
                    print(f"Failed to delete {file_path}: {str(e)}")
            
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    shutil.rmtree(dir_path)
                    deleted_count += 1  # Counting directory as one item
                except Exception as e:
                    print(f"Failed to delete directory {dir_path}: {str(e)}")
        
        # Display results
        print("\n" + "=" * 50)
        print(f"Deleted {deleted_count} items ({format_size(deleted_size)})")
        remaining_files = total_files - deleted_count
        if remaining_files > 0:
            print(f"Warning: {remaining_files} items could not be deleted")
        print("=" * 50)
        
        return True
    
    except Exception as e:
        print(f"Error while cleaning directory {directory_path}: {str(e)}")
        return False

def main():
    # Default directories to clean
    default_dirs = [
        "/Users/madhukunwar/Downloads/googleClassroomXpoter/downloads",
        "/Users/madhukunwar/Downloads/googleClassroomXpoter/uploaded_files"
    ]
    
    print("\n" + "=" * 50)
    print("DIRECTORY CLEANUP TOOL".center(50))
    print("=" * 50)
    print("\nOptions:")
    print("1. Clean default directories")
    print("2. Enter custom directory path")
    print("3. Clean both default and custom directory")
    
    try:
        choice = input("\nEnter your choice (1/2/3): ").strip()
        
        if choice == "1":
            for directory in default_dirs:
                delete_directory_contents(directory)
        elif choice == "2":
            custom_path = input("\nEnter the full path of the directory to clean: ").strip()
            delete_directory_contents(custom_path)
        elif choice == "3":
            for directory in default_dirs:
                delete_directory_contents(directory)
            custom_path = input("\nEnter the full path of the directory to clean: ").strip()
            delete_directory_contents(custom_path)
        else:
            print("Invalid choice. Please run the script again.")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")

if __name__ == "__main__":
    main()