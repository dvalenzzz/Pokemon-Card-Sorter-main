import csv

class CardSet:
    def __init__(self, csv_file_path):
        self.cardnamelist = []
        self.cardtype = []
        self.setname = []
        self.setno = []
        self.color = []
        self.subtype = []

        # Read data from the CSV file and populate the lists
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.cardnamelist.append(row['Name'])
                self.cardtype.append(row['Type'])
                self.setname.append(row['Set'])
                self.setno.append(row['SetNo'])
                self.color.append(row['Color'])
                self.subtype.append(row['SubType'])




        self.numCards = len(self.cardnamelist)  # Number of cards in the set

# Usage
csv_file_path = 'scraped_cards_complete.csv'
cardset = CardSet(csv_file_path)

# Access the lists
# print(card_set.cardnamelist)
# print(card_set.cardtype)
# print(card_set.set)
# print(card_set.setno)
