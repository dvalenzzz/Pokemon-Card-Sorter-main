import numpy as np
import imagehash
from PIL import Image, ImageOps
import os
import re


def filelookup(directory, i):
    """
    Searches for a file in the given directory that matches the regex pattern 
    for the first five characters, then opens and returns the content of the file.
    
    Parameters:
    directory (str): The directory where the file is located.
    pattern (str): The regex pattern to match the first five characters of the file name.

    Returns:
    str: Content of the matched file, or a message if no file is found.
    """
    # Compile the regex pattern
    pattern = re.compile(r'^' + str(i).rjust(5, '0') + r'.*')


    # Find the file that matches the pattern
    file_to_open = None
    for filename in os.listdir(directory):
        if pattern.match(filename):
            file_to_open = filename

            break

    if file_to_open:
        file_to_open = directory + filename
        return file_to_open
    else:
    
        return f"No file found starting with the pattern '{pattern}'"
# Gets the average hash, whash, phash, & dhash for each card in the set in each orientation for a total of 16 hashes
# Four different hash methods are used to reduce potential for error in using only one hashing method
class EvolutionsSet:
    def __init__(self):
        self.setSize = 18512  # Number of cards total

        self.hashes = self.getHashes('hash')  # Gets hashes of normally oriented cards
        self.hashesmir = self.getHashes('hashmir')  # Gets hashes of mirrored cards
        self.hashesud = self.getHashes('hashud')  # Gets hashes of upside down cards
        self.hashesudmir = self.getHashes('hashudmir')  # Gets hashes of mirrored upside down cards
    import os





    # Gets hashes of all cards in Evolutions set
    def getHashes(self, type):
        # Create an array with self.setSize rows and 4 columns. Each column represents a different hashing method
        arr = np.empty((self.setSize, 4), dtype=object)
        # Loop through each card image
        for i in range(1, self.setSize + 1):
            filename = filelookup('CardImages/', i)
            print(filename)
            img = Image.open(filename)
            match type:
                # For each case, find the average hash, whash, phash, & dhash of the image & convert it to a string
                case 'hash':  # Normally oriented card
                    arr[i - 1][0] = str(imagehash.average_hash(img))
                    arr[i - 1][1] = str(imagehash.whash(img))
                    arr[i - 1][2] = str(imagehash.phash(img))
                    arr[i - 1][3] = str(imagehash.dhash(img))
                case 'hashmir':  # Mirrored card
                    imgmir = ImageOps.mirror(img)
                    arr[i - 1][0] = str(imagehash.average_hash(imgmir))
                    arr[i - 1][1] = str(imagehash.whash(imgmir))
                    arr[i - 1][2] = str(imagehash.phash(imgmir))
                    arr[i - 1][3] = str(imagehash.dhash(imgmir))
                case 'hashud':  # Upside down card
                    imgflip = ImageOps.flip(img)
                    arr[i - 1][0] = str(imagehash.average_hash(imgflip))
                    arr[i - 1][1] = str(imagehash.whash(imgflip))
                    arr[i - 1][2] = str(imagehash.phash(imgflip))
                    arr[i - 1][3] = str(imagehash.dhash(imgflip))
                case 'hashudmir':  # Upside down & mirrored card
                    imgmirflip = ImageOps.flip(ImageOps.mirror(img))
                    arr[i - 1][0] = str(imagehash.average_hash(imgmirflip))
                    arr[i - 1][1] = str(imagehash.whash(imgmirflip))
                    arr[i - 1][2] = str(imagehash.phash(imgmirflip))
                    arr[i - 1][3] = str(imagehash.dhash(imgmirflip))
        return arr  # Return self.setSize x 4 array of image hashes for selected orientation
