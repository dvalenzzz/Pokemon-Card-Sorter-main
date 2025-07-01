import csv

# File path to the CSV file
csv_file_path = 'scraped_cards_cleaned.csv'

# List to hold the header and data tuples
header = ()
data_tuples = []

# Open the CSV file and read its contents
with open(csv_file_path, newline='') as csvfile:
    reader = csv.reader(csvfile)
    
    # Extract the header row
    header = tuple(next(reader))
    
    # Iterate through each remaining row in the CSV
    for row in reader:
        # Convert the row to a tuple and add to the list
        data_tuples.append(tuple(row))

# Combine the header and the data tuples
final_tuple = (header, *data_tuples)

# Output the result
print(final_tuple)
