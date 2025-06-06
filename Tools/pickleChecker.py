import pickle

# Step 1: Load the pickle file
pickle_file_path = 'data.pickle'  # Path to your pickle file
with open('fullSet.pickle', 'rb') as file:
    fullSet = pickle.load(file)


# Step 2: Modify the attribute (if needed)
# Check the current setname attribute
print(type(fullSet))