import mysql.connector
import cardSet
import imagehash
import numpy as np
import pickle
import tqdm
import timeit
username = "root"  # Your mysql username
password = "password"  # Your mysql password
databasename = "pokemondatabaselimit"  # name of database we want to create


# Creates a database of pokemon 
def createDatabase():
    # Connects to the localhost
    db = mysql.connector.connect(
        host="localhost",
        user=username,
        passwd=password
    )

    # Creates a cursor so that we can create and databases
    mycursor = db.cursor()

    # Check if database has already been created; if not, create it
    mycursor.execute(
        "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{}'".format(databasename))
    if mycursor.fetchone() is None:
        mycursor.execute(f"CREATE DATABASE {databasename}")
    else:
        mycursor.execute(f"DROP DATABASE {databasename}")  # Incase user forgot to change first to False after having
        # already created database
        mycursor.execute(f"CREATE DATABASE {databasename}")

    # Add tables and values to database
    initializeDatabase()


# Initializes database with inital values for cards and pokemon
def initializeDatabase():
    # Connects to the database that already existed or was created in createDatabase()
    db = mysql.connector.connect(
        host="localhost",
        user=username,
        passwd=password,
        database=databasename
    )

    # Creates a cursor so that we can edit the database
    mycursor = db.cursor()

    ## Creates a Pokedex object that holds information on the first 151 (Kanto) Pokemon and some of their mega evolutions
    ## Information includes pokedex number, pokemon names, type, stage, and height
    # poke = pokedex.Pokedex()

#     Creates a CardSet object that has information on the cards in Evolutions
#     Information includes card numbers, pokemon names, card names, card rarity, and card type
    fullSet = cardSet.CardSet('scraped_cards_complete.csv')

    # Creates a EvolutionsSet object that stores the hashes for the images of the Pokemon cards
    # Has hashes for the following orientations of the card: normal, mirrored, upside-down, upside down mirrored
#####   fullCards = evolutionsSet.EvolutionsSet()

    # with open('fullCards.pickle', 'wb') as file:
    #     pickle.dump(fullCards, file)
    
    with open('fullSet.pickle', 'wb') as file:
        pickle.dump(fullSet, file)

    with open('fullCards.pickle', 'rb') as file:
        fullCards = pickle.load(file)

    # with open('fullSet.pickle', 'rb') as file:
    #     fullSet = pickle.load(file)
    # print(fullSet.set)
    # # Creates a new table Pokemon that will hold the values in the poke Pokedex object
    # mycursor.execute("CREATE TABLE Pokemon (dexNumber SMALLINT, pokemon VARCHAR(20) PRIMARY KEY, \
    #         poketype VARCHAR(10), height DOUBLE UNSIGNED, stage VARCHAR(5))")

    # # Populates the Pokemon table
    # for x in range(poke.numpoke):
    #     mycursor.execute("INSERT INTO Pokemon (dexNumber, pokemon, poketype, stage, height) VALUES(%s, %s, %s, %s, %s)",
    #                      (poke.dexnumber[x], poke.pokemon[x], poke.type[x], poke.stage[x], poke.height[x]))

    # Creates a new table EvolutionsSet that will hold the values in the fullSet CardSet object
    mycursor.execute("CREATE TABLE EvolutionsSet (cardnumber INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT, \
            cardname VARCHAR(55), color VARCHAR(6), setname VARCHAR(50), setNo INT(3), cardtype VARCHAR(17), subType VARCHAR(15))")
    
    # Populates the EvolutionsSet table
    for x in tqdm.tqdm(range(fullSet.numCards)):
        mycursor.execute("INSERT INTO EvolutionsSet (cardname, cardtype, setname, setNo, color, subType) VALUES(%s, %s, %s, %s, %s, %s)",
                         (fullSet.cardnamelist[x], fullSet.cardtype[x], fullSet.setname[x], fullSet.setno[x], fullSet.color[x], fullSet.subtype[x]))

    # Creates a new table EvolutionsCards that will hold the values in the fullCards EvolutionsSet object
    mycursor.execute("CREATE TABLE EvolutionsCards (cardnumber INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT, \
            FOREIGN KEY(cardnumber) REFERENCES EvolutionsSet(cardnumber), \
            avghashes VARCHAR(20), avghashesmir VARCHAR(20), avghashesud VARCHAR(20), avghashesudmir VARCHAR(20), \
            whashes VARCHAR(20), whashesmir VARCHAR(20), whashesud VARCHAR(20), whashesudmir VARCHAR(20), \
            phashes VARCHAR(20), phashesmir VARCHAR(20), phashesud VARCHAR(20), phashesudmir VARCHAR(20), \
            dhashes VARCHAR(20), dhashesmir VARCHAR(20), dhashesud VARCHAR(20), dhashesudmir VARCHAR(20))")

    # Populates the EvolutionsCards table
    for x in range(fullCards.setSize):
        mycursor.execute(
            "INSERT INTO EvolutionsCards (avghashes, avghashesmir, avghashesud, avghashesudmir, \
            whashes, whashesmir, whashesud, whashesudmir, \
            phashes, phashesmir, phashesud, phashesudmir, \
            dhashes, dhashesmir, dhashesud, dhashesudmir) \
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (fullCards.hashes[x][0], fullCards.hashesmir[x][0], fullCards.hashesud[x][0], fullCards.hashesudmir[x][0],
             fullCards.hashes[x][1], fullCards.hashesmir[x][1], fullCards.hashesud[x][1], fullCards.hashesudmir[x][1],
             fullCards.hashes[x][2], fullCards.hashesmir[x][2], fullCards.hashesud[x][2], fullCards.hashesudmir[x][2],
             fullCards.hashes[x][3], fullCards.hashesmir[x][3], fullCards.hashesud[x][3], fullCards.hashesudmir[x][3]))

    # Commits changes to the database
    db.commit()


# Returns a dictionary of values of the matching Pokemon card if the hash distance is within the cutoff range
# If no matching card is found, it returns None
def compareCardsBozo(hashes):
    cutoff = 18  # Arbitrarily set cutoff value; was found through testing
    # Connects to the pokemon card database
    db = mysql.connector.connect(
        host="localhost",
        user=username,
        passwd=password,
        database=databasename
    )

    mycursor = db.cursor(buffered=True)  # Create cursor with buffered=True so that mycursor.rowcount doesn't return 0

    mycursor.execute("SELECT * FROM EvolutionsCards")  # Gets values from EvolutionsCards (hashes)

    # Create arrays of size=4 that store hash differences for each orientation; every hashing method gets its own array
    avghashesDists = np.zeros(4)
    whashesDists = np.zeros(4)
    phashesDists = np.zeros(4)
    dhashesDists = np.zeros(4)

    maxHashDists = []  # An array that will store the maximum of the minimum hash difference for each card

    for _ in range(mycursor.rowcount):  # Loop through each row in EvolutionsCards table
        # Get the values stored in each row
        # Note: the hashes are stored as Strings in the database because MySQL doesn't support storing hashes
        cardnum, \
            avghash1, avghash2, avghash3, avghash4, \
            whash1, whash2, whash3, whash4,\
            phash1, phash2, phash3, phash4, \
            dhash1, dhash2, dhash3, dhash4 = mycursor.fetchone()

        # Convert each hash from a String to a hash and find the distance from the scanned image
        avghashesDists[0] = hashes[0] - imagehash.hex_to_hash(avghash1)
        avghashesDists[1] = hashes[0] - imagehash.hex_to_hash(avghash2)
        avghashesDists[2] = hashes[0] - imagehash.hex_to_hash(avghash3)
        avghashesDists[3] = hashes[0] - imagehash.hex_to_hash(avghash4)

        whashesDists[0] = hashes[1] - imagehash.hex_to_hash(whash1)
        whashesDists[1] = hashes[1] - imagehash.hex_to_hash(whash2)
        whashesDists[2] = hashes[1] - imagehash.hex_to_hash(whash3)
        whashesDists[3] = hashes[1] - imagehash.hex_to_hash(whash4)

        phashesDists[0] = hashes[2] - imagehash.hex_to_hash(phash1)
        phashesDists[1] = hashes[2] - imagehash.hex_to_hash(phash2)
        phashesDists[2] = hashes[2] - imagehash.hex_to_hash(phash3)
        phashesDists[3] = hashes[2] - imagehash.hex_to_hash(phash4)

        dhashesDists[0] = hashes[3] - imagehash.hex_to_hash(dhash1)
        dhashesDists[1] = hashes[3] - imagehash.hex_to_hash(dhash2)
        dhashesDists[2] = hashes[3] - imagehash.hex_to_hash(dhash3)
        dhashesDists[3] = hashes[3] - imagehash.hex_to_hash(dhash4)

        # Find the minimum of each hashing method
        # This should make us look at the correct card orientation
        hashDistances = [min(avghashesDists), min(whashesDists), min(phashesDists), min(dhashesDists)]
        maxHashDists.append(max(hashDistances))  # Find the max of the mins of each hashing method to reduce error

    print(min(maxHashDists))
    if min(maxHashDists) < cutoff:  # If the smallest hash distance is less than the cutoff, we have found our card
        minCardNum = maxHashDists.index(min(maxHashDists)) + 1  # Find the card number of the card

        # Get values from minCardNum row of EvolutionsSet table
        mycursor.execute(f"SELECT * FROM EvolutionsSet WHERE cardnumber={minCardNum}")
        vals = mycursor.fetchone()
        _, cardname, cardtype, setname, setno, color, subtype = vals

        # # Get values from poke row of Pokemon table
        # mycursor.execute("SELECT * FROM Pokemon WHERE pokemon=%s", (poke,))
        # vals2 = mycursor.fetchone()
        # dexnumber, _, poketype, height, stage = vals2

        # Return dictionary with traits about cards
        return {'Card Number': minCardNum,
                'Card Name': cardname,
                'Set': setname,
                'Card Type': cardtype,
                'Set Number': setno,
                'Pokemon Type': color,
                'Subtype': subtype}
    return None
def convertStr2Hash(hashes):
    # Connects to the pokemon card database
    db = mysql.connector.connect(
        host="localhost",
        user=username,
        passwd=password,
        database=databasename
    )

    mycursor = db.cursor(buffered=True)  # Create cursor with buffered=True so that mycursor.rowcount doesn't return 0

    mycursor.execute("SELECT * FROM EvolutionsCards")  # Gets values from EvolutionsCards (hashes)
    phash1 = imagehash.hex_to_hash(phash1)
    phash2 = imagehash.hex_to_hash(phash2)
    phash3 = imagehash.hex_to_hash(phash3)
    phash4 = imagehash.hex_to_hash(phash4)
    dhash1 = imagehash.hex_to_hash(dhash1)
    dhash2 = imagehash.hex_to_hash(dhash2)
    dhash3 = imagehash.hex_to_hash(dhash3)
    dhash4 = imagehash.hex_to_hash(dhash4)



def compareCards(hashes):
    cutoff = 18  # Arbitrarily set cutoff value; was found through testing
    # Connects to the pokemon card database
    db = mysql.connector.connect(
        host="localhost",
        user=username,
        passwd=password,
        database=databasename
    )

    mycursor = db.cursor(buffered=True)  # Create cursor with buffered=True so that mycursor.rowcount doesn't return 0

    mycursor.execute("SELECT * FROM parsfahash")  # Gets values from EvolutionsCards (hashes)

    # Create arrays of size=4 that store hash differences for each orientation; every hashing method gets its own array
    phashesDists = np.zeros(4)
    dhashesDists = np.zeros(4)

    maxHashDists = []  # An array that will store the maximum of the minimum hash difference for each card
    
    for _ in range(mycursor.rowcount):  # Loop through each row in EvolutionsCards table
        # Get the values stored in each row
        # Note: the hashes are stored as Strings in the database because MySQL doesn't support storing hashes
        cardnum, \
            _, _, _, _,\
            _,_,_,_,\
            phash1, phash2, phash3, phash4, \
            dhash1, dhash2, dhash3, dhash4 = mycursor.fetchone()

        # # Convert each hash from a String to a hash and find the distance from the scanned image
        # section_start = timeit.default_timer()
        # pp = imagehash.hex_to_hash(phash1)
        # section_end = timeit.default_timer()
        # print(f"Time to read hex2hash: {section_end - section_start:.4f} seconds")
        # section_start = timeit.default_timer()
        # pp2 = hashes[0] - pp
        # section_end = timeit.default_timer()
        # print(f"Time to subtract: {section_end - section_start:.4f} seconds")

        phashesDists[0] = hashes[0] - imagehash.hex_to_hash(phash1)
        phashesDists[1] = hashes[0] - imagehash.hex_to_hash(phash2)
        phashesDists[2] = hashes[0] - imagehash.hex_to_hash(phash3)
        phashesDists[3] = hashes[0] - imagehash.hex_to_hash(phash4)

        dhashesDists[0] = hashes[1] - imagehash.hex_to_hash(dhash1)
        dhashesDists[1] = hashes[1] - imagehash.hex_to_hash(dhash2)
        dhashesDists[2] = hashes[1] - imagehash.hex_to_hash(dhash3)
        dhashesDists[3] = hashes[1] - imagehash.hex_to_hash(dhash4)

        section_start = timeit.default_timer()
        # Find the minimum of each hashing method
        # This should make us look at the correct card orientation
        hashDistances = [ min(phashesDists), min(dhashesDists)]
        maxHashDists.append(max(hashDistances))  # Find the max of the mins of each hashing method to reduce error
        section_end = timeit.default_timer()
        # print(f"Time to read phashdist 0: {section_end - section_start:.4f} seconds")

    # print(min(maxHashDists))
    if min(maxHashDists) < cutoff:  # If the smallest hash distance is less than the cutoff, we have found our card
        minCardNum = maxHashDists.index(min(maxHashDists)) +1 # Find the card number of the card

        # Get values from minCardNum row of EvolutionsSet table
        mycursor.execute(f"SELECT * FROM parsfainfo WHERE cardnumber={minCardNum+1}")
        vals = mycursor.fetchone()
        _, cardname, color, setname, setno, cardtype, subtype = vals

        # # Get values from poke row of Pokemon table
        # mycursor.execute("SELECT * FROM Pokemon WHERE pokemon=%s", (poke,))
        # vals2 = mycursor.fetchone()
        # dexnumber, _, poketype, height, stage = vals2

        # Return dictionary with traits about cards
        return {'Card Number': minCardNum,
                'Card Name': cardname,
                'Set': setname,
                'Card Type': cardtype,
                'Set Number': setno,
                'Pokemon Type': color,
                'Subtype': subtype}
    return None

def compareCardsDoesNotBreak(hashes):
    cutoff = 18  # Arbitrarily set cutoff value; was found through testing
    # Connects to the pokemon card database
    db = mysql.connector.connect(
        host="localhost",
        user=username,
        passwd=password,
        database=databasename
    )

    mycursor = db.cursor(buffered=True)  # Create cursor with buffered=True so that mycursor.rowcount doesn't return 0

    mycursor.execute("SELECT * FROM EvolutionsCards")  # Gets values from EvolutionsCards (hashes)

    # Create arrays of size=4 that store hash differences for each orientation; every hashing method gets its own array
    phashesDists = np.zeros(4)
    dhashesDists = np.zeros(4)

    maxHashDists = []  # An array that will store the maximum of the minimum hash difference for each card

    for _ in range(mycursor.rowcount):  # Loop through each row in EvolutionsCards table
        # Get the values stored in each row
        # Note: the hashes are stored as Strings in the database because MySQL doesn't support storing hashes
        cardnum, \
            _, _, _, _,\
            _,_,_,_,\
            phash1, phash2, phash3, phash4, \
            dhash1, dhash2, dhash3, dhash4 = mycursor.fetchone()
    
        # Convert each hash from a String to a hash and find the distance from the scanned image
        section_start = timeit.default_timer()

        phashesDists[0] = hashes[0] - imagehash.hex_to_hash(phash1)

        section_end = timeit.default_timer()
        print(f"Time to read phashdist 0: {section_end - section_start:.8f} seconds")
        phashesDists[0] = hashes[0] - imagehash.hex_to_hash(phash1)
        phashesDists[1] = hashes[0] - imagehash.hex_to_hash(phash2)
        phashesDists[2] = hashes[0] - imagehash.hex_to_hash(phash3)
        phashesDists[3] = hashes[0] - imagehash.hex_to_hash(phash4)

        dhashesDists[0] = hashes[1] - imagehash.hex_to_hash(dhash1)
        dhashesDists[1] = hashes[1] - imagehash.hex_to_hash(dhash2)
        dhashesDists[2] = hashes[1] - imagehash.hex_to_hash(dhash3)
        dhashesDists[3] = hashes[1] - imagehash.hex_to_hash(dhash4)

        # Find the minimum of each hashing method
        # This should make us look at the correct card orientation
        hashDistances = [ min(phashesDists), min(dhashesDists)]
        maxHashDists.append(max(hashDistances))  # Find the max of the mins of each hashing method to reduce error

    print(min(maxHashDists))
    if min(maxHashDists) < cutoff:  # If the smallest hash distance is less than the cutoff, we have found our card
        minCardNum = maxHashDists.index(min(maxHashDists)) + 1  # Find the card number of the card

        # Get values from minCardNum row of EvolutionsSet table
        mycursor.execute(f"SELECT * FROM EvolutionsSet WHERE cardnumber={minCardNum}")
        vals = mycursor.fetchone()
        _, cardname, cardtype, setname, setno, color, subtype = vals

        # # Get values from poke row of Pokemon table
        # mycursor.execute("SELECT * FROM Pokemon WHERE pokemon=%s", (poke,))
        # vals2 = mycursor.fetchone()
        # dexnumber, _, poketype, height, stage = vals2

        # Return dictionary with traits about cards
        return {'Card Number': minCardNum,
                'Card Name': cardname,
                'Set': setname,
                'Card Type': cardtype,
                'Set Number': setno,
                'Pokemon Type': color,
                'Subtype': subtype}
    return None