import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
from tqdm import tqdm

# Create the directory if it doesn't exist
save_directory = "CardImages"
os.makedirs(save_directory, exist_ok=True)

# Assuming you already have the links from a text file
with open("all.links.txt", "r") as links:
    for line in links:
        page_to_scrape = requests.get(line.strip())  # Strip removes any newline characters
        soup = BeautifulSoup(page_to_scrape.text, 'html.parser')
        
        # Find all items with the class 'card-image-link'
        content = soup.findAll(attrs={'class': 'card-image-link'})
        
        # Display the progress bar for image downloads on this page
        for idx, a in tqdm(enumerate(content), total=len(content), desc="Downloading Images"):
            img_tag = a.find('img')
            
            if img_tag:  # Check if the img_tag was found
                img_url = img_tag['src']
                img_data = requests.get(img_url).content  # Download the image data
                
                # Extract the original file name from the URL
                base_filename = os.path.basename(urlsplit(img_url).path)
                filename, ext = os.path.splitext(base_filename)
                
                # Create the new filename with the index number
                new_filename = f"{idx + 1}_{filename}{ext}"
                full_path = os.path.join(save_directory, new_filename)
                
                # Save the image
                with open(full_path, 'wb') as handler:
                    handler.write(img_data)
                
