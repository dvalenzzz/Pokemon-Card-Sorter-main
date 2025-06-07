from bs4 import BeautifulSoup
import requests

#IMPORT CSV LIBRARY
import csv

# Import xpath
from lxml import etree

#OPEN A NEW CSV FILE. IT CAN BE CALLED ANYTHING
file = open('scraped_cards.csv', 'w')
#CREATE A VARIABLE FOR WRITING TO THE CSV
writer = csv.writer(file)

#CREATE THE HEADER ROW OF THE CSV
writer.writerow(['Name', 'Type'])

#REQUEST WEBPAGE AND STORE IT AS A VARIABLE
page_to_scrape = requests.get("https://pkmncards.com/card/pecharunt-scarlet-violet-promos-svp-129/")
'''
doc = libxml2.parseFile(page_to_scrape)
ctxt = doc.xpathNewContext()
res = ctxt.xpathEval("//*")
if len(res) != 2:
   # print "xpath query: wrong node set size"
    sys.exit(1)
if res[0].name != "doc" or res[1].name != "foo":
   # print "xpath query: wrong node set value"
    sys.exit(1)
doc.freeDoc()
ctxt.xpathFreeContext()
'''

#USE BEAUTIFULSOUP TO PARSE THE HTML AND STORE IT AS A VARIABLE
soup = BeautifulSoup(page_to_scrape.text, 'html.parser')
#FIND ALL THE ITEMS IN THE PAGE WITH A CLASS ATTRIBUTE OF 'TEXT'
#AND STORE THE LIST AS A VARIABLE
name = soup.findAll('span', attrs={'class':'name'})

#FIND ALL THE ITEMS IN THE PAGE WITH A CLASS ATTRIBUTE OF 'AUTHOR'
#AND STORE THE LIST AS A VARIABLE
type = soup.findAll('span', attrs={"class":"type"})

#LOOP THROUGH BOTH LISTS USING THE 'ZIP' FUNCTION
#AND PRINT AND FORMAT THE RESULTS
for name, type in zip(name, type):
    print(name.text + "-" + type.text)
    #WRITE EACH ITEM AS A NEW ROW IN THE CSV
    writer.writerow([name.text, type.text])
#CLOSE THE CSV FILE
file.close()