import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Create the directory if it doesn't exist
save_directory = "CardImages"
os.makedirs(save_directory, exist_ok=True)

# Function to download a single image
def download_image(img_url, save_directory, idx):
    img_data = requests.get(img_url).content  # Download the image data
    
    # Extract the original file name from the URL
    base_filename = os.path.basename(urlsplit(img_url).path)
    filename, ext = os.path.splitext(base_filename)
    
    # Create the new filename with the index number at the start
    new_filename = f"{idx + 1}_{filename}{ext}"
    full_path = os.path.join(save_directory, new_filename)
    
    # Save the image
    with open(full_path, 'wb') as handler:
        handler.write(img_data)
    
    return new_filename

# Assuming you already have the links from the renamed text file
with open("urls.txt", "r") as links:
    all_lines = links.readlines()
    total_pages = len(all_lines)
    
    # Initialize the global index for card images
    global_idx = 0
    
    # Overall progress bar for all pages
    for page_idx, line in enumerate(tqdm(all_lines, desc="Overall Progress", total=total_pages), start=95):
        page_to_scrape = requests.get(line.strip())  # Strip removes any newline characters
        soup = BeautifulSoup(page_to_scrape.text, 'html.parser')
        
        # Find all items with the class 'card-image-link'
        content = soup.findAll(attrs={'class': 'card-image-link'})
        
        # Initialize a thread pool for the current page
        with ThreadPoolExecutor(max_workers=24) as executor:  # Adjust max_workers to control concurrency
            # Submit download tasks to the thread pool, using the global index for filenames
            futures = [
                executor.submit(download_image, a.find('img')['src'], save_directory, global_idx + idx)
                for idx, a in enumerate(content)
            ]
            
            # Progress bar for the current page, showing page number and percentage of total progress
            page_progress = tqdm(as_completed(futures), total=len(futures), 
                                 desc=f"Page {page_idx}/{total_pages} ({(page_idx/total_pages)*100:.1f}%)")
            
            # Wait for all tasks on the current page to complete
            for future in page_progress:
                filename = future.result()
                print(f"Saved {filename}")
        
        # Update the global index after each page
        global_idx += len(content)
