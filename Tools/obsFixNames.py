import os
import re

def undo_rename(directory):
    # Define the pattern to match files with a 6-character prefix followed by an underscore
    pattern = re.compile(r'^\d{5}_(.*)$')
    
    # List all files in the directory
    files = os.listdir(directory)
    
    for filename in files:
        match = pattern.match(filename)
        if match:
            # Extract the original filename (excluding the first 6 characters)
            new_filename = match.group(1)
            
            # Construct the full path for renaming
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, new_filename)
            
            # Rename the file
            os.rename(old_path, new_path)
            print(f"Renamed '{filename}' to '{new_filename}'")

# Replace 'your_directory' with the path to your directory


undo_rename('CardImages - Copy - Copy')
