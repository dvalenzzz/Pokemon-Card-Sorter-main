from scipy.spatial import distance
import numpy as np
import imagehash

# Convert imagehash objects to numpy arrays
def hash_to_array(hash_obj):
    # imagehash produces an object of size 8x8 for pHash
    return np.array(hash_obj.hash, dtype=int).flatten()

ph1 = imagehash.hex_to_hash('800b75b96ac75735')
ph2 = imagehash.hex_to_hash('802a5dc54bd33b9d')
ph3 = imagehash.hex_to_hash('802b4be77a9535b1')
ph4 = imagehash.hex_to_hash('802f6d9553d97a49')
dodgy = hash_to_array(ph1)
print(dodgy)
# Convert to numerical coordinates
coords = [hash_to_array(ph1),
          hash_to_array(ph2),
          hash_to_array(ph3),
          hash_to_array(ph4)]

# Calculate the pairwise Euclidean distances
d = distance.cdist(coords, coords, 'euclidean')

print(d)
