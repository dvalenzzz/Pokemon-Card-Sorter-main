from bs4 import BeautifulSoup
import requests
import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

# Function to scrape data from a single card link
def scrape_card_data(link):
    page_to_scrape = requests.get(link)
    soup = BeautifulSoup(page_to_scrape.text, 'html.parser')
    content = soup.findAll(attrs={'class': 'card-image-link'})
    card_data = []
    for i, a in enumerate(content):
        card_page = requests.get(a.attrs["href"])
        card_soup = BeautifulSoup(card_page.text, 'html.parser')
        name = card_soup.findAll('span', attrs={'class': 'name'})
        type = card_soup.findAll('span', attrs={"class": "type"})
        set = card_soup.findAll('span', attrs={"title": "Set"})
        set_num = card_soup.findAll('span', attrs={"class": "number"})
        cardnumber = str(i)

        if type[0].text == 'Pokémon':
            color = card_soup.findAll('span', attrs={"class": "color"})[0].text
            subtype = '0'
        elif type[0].text == 'Trainer':
            subtype = card_soup.findAll('span', attrs={"class": "sub-type"})[0].text
            color = '0'
        else:
            color = '0'
            subtype = '0'

        card_data.append([name[0].text, type[0].text, set[0].text, set_num[0].text, color, subtype, cardnumber])

    return card_data

# Function to process each link and collect data
def process_link(link):
    start_time = time.time()  # Start timer for this task
    card_data = scrape_card_data(link.strip())
    end_time = time.time()  # End timer for this task
    print(f"Processed {link.strip()} in {end_time - start_time:.2f} seconds")
    return card_data

# Main code block
if __name__ == '__main__':
    file_exists = os.path.isfile('scraped_cards_pt4.csv')

    with open("links.txt", "r") as links_file:
        links = links_file.readlines()

    all_data = []
    with ThreadPoolExecutor(max_workers=24) as executor:
        futures = [executor.submit(process_link, link) for link in links]

        for future in tqdm(as_completed(futures), total=len(links), desc="Processing Links"):
            all_data.extend(future.result())

    # Write to CSV file
    with open('scraped_cards_pt4.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Name', 'Type', 'Set', 'Set No.', 'Color', 'Sub-Type', 'index'])
        writer.writerows(all_data)
