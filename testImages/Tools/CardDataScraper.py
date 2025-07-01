from bs4 import BeautifulSoup
import requests
import tqdm
#IMPORT CSV LIBRARY
import csv
import os
file_exists = os.path.isfile('scraped_cardspt6.csv')
#OPEN A NEW CSV FILE. IT CAN BE CALLED ANYTHING PLEASE note that : ' apostrophe e are all problem characters and might give you errors please ensure they work before use if not must edit csv``


# file = open('scraped_cards.csv', 'w', newline='') #for when making a new one
with open('scraped_cardspt6.csv', 'a', newline='', encoding='utf-8') as file:
          
    #CREATE A VARIABLE FOR WRITING TO THE CSV
    writer = csv.writer(file)

    if not file_exists:
        writer.writerow(['Name', 'Type','Set','Set No.', 'Color', 'Sub-Type'])
    #CREATE THE HEADER ROW OF THE CSV

    #REQUEST WEBPAGE AND STORE IT AS A VARIABLE
    #page_to_scrape = requests.get("https://pkmncards.com/card/pecharunt-scarlet-violet-promos-svp-129/")
    links = f = open("links.txt", "r")
    x = 0 

    for line in links:
        page_to_scrape = requests.get(line.replace('\n',''))
        #USE BEAUTIFULSOUP TO PARSE THE HTML AND STORE IT AS A VARIABLE
        soup = BeautifulSoup(page_to_scrape.text, 'html.parser')
        #FIND ALL THE ITEMS IN THE PAGE WITH A CLASS ATTRIBUTE OF 'entry-content'
        #AND STORE THE LIST AS A VARIABLE
        content = soup.findAll(attrs={'class':'card-image-link'})

        #LOOP THROUGH BOTH LISTS USING THE 'ZIP' FUNCTION
        #AND PRINT AND FORMAT THE RESULTS
        for a in tqdm.tqdm(content):
            card_page = requests.get(a.attrs["href"])
            card_soup = BeautifulSoup(card_page.text, 'html.parser')
            #for c in card_page
            name = card_soup.findAll('span', attrs={'class':'name'})
            type = card_soup.findAll('span', attrs={"class":"type"})
            set = card_soup.findAll('span',attrs={"title":"Set"})
            set_num = card_soup.findAll('span',attrs={"class":"number"})
            date = card_soup('span',attrs={"class":"date"})
            ## price = soup.findAll('span',attrs={"class":"set"})

            if type[0].text == 'Pokémon':
                color = card_soup.findAll('span', attrs={"class":"color"})[0].text
                subtype = 0
            if type[0].text == 'Trainer':
                subtype = card_soup.findAll('span', attrs={"class":"sub-type"})[0].text
                color = 0
        
            #WRITE EACH ITEM AS A NEW ROW IN THE CSV

            #r card in the link in a.attrs["href"]
            writer.writerow([name[0].text, type[0].text, set[0].text, set_num[0].text, color, subtype])

            # if x % 1000 == 0 and x > 0:
            #     file.flush()
            #     # print("row " + str(x) + "" + [name[0].text, type[0].text, set[0].text, set_num[0].text, color, subtype])
            #     print( "URL:"+a.attrs["href"])
            #     break
            x += 1


            

    #CLOSE THE CSV FILE
    file.close()