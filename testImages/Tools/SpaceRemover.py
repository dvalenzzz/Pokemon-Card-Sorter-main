import csv

# File paths
input_file_path = 'scraped_cards.csv'
output_file_path = 'scraped_cards_cleaned.csv'

# Read the CSV and remove blank lines
with open(input_file_path, 'r', newline='') as infile, open(output_file_path, 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        # Only write rows that are not completely empty
        if any(field.strip() for field in row):
            writer.writerow(row)

print(f"Blank spaces removed. Cleaned file saved as {output_file_path}.")
