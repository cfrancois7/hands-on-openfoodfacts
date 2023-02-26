# %% [markdown]
# # Pre-requisite libraries

# %% [markdown]
# # Extract info

# %% [markdown]
# **WARNING: The following code supposes that your install one OpenFoodFact MongoDB instance locally.**

# %%
from pymongo import MongoClient
from module.image import parse, get_image, save_image
from tqdm import tqdm
import json

# %%
client = MongoClient('localhost', 27017, connectTimeoutMS=5000, serverSelectionTimeoutMS=5000)
db = client['off']
collection = db['products']
prefix = 'https://images.openfoodfacts.org/images/products/'

# %%
projection = {
    'id':1,
    'code':1,
    'images':1,
    'abbreviated_product_name':1,
    'product_name':1,
    }
query = {
    'countries':{'$nin':['France', 'en:fr']},
    'images':{"$exists":True, '$ne':[]}
    }
cursor = collection.find(query, projection=projection, limit=10000)

# %%
from pymongo.errors import ServerSelectionTimeoutError
from pathlib import Path
import json

f = Path('data/image_data.json')

try:
    ids = [i for i in cursor]
except ServerSelectionTimeoutError:
    # Does it exists the file locally?
    if f.is_file():
        with open(f, 'r') as file:
            ids = json.load(file)
            
with open(f, 'w') as file:
    json.dump(ids, file)

# %%
# build dict with code as key and product_name and/or
# abbreviated_product_name when they exist
image_url_dict = {i['code']:parse(i, prefix=prefix) for i in ids}
id_name_dict = {
    i['code']:{
    'product_name':i.get('product_name', 'NA'),
    'abbreviated_product_name':i.get('abbreviated_product_name', 'NA')
    } for i in ids
}
# save the dict into .json file.
with open('label_of_products.json', 'w') as file:
     file.write(json.dumps(id_name_dict))

# %% [markdown]
# # Download images one by one (long, maybe could be optimized)

# %%
from pathlib import Path
DOWNLOADED_IMAGE_LIST = Path('data/images_downloaded.txt')

if DOWNLOADED_IMAGE_LIST.exists():
    with open(str(DOWNLOADED_IMAGE_LIST), 'r') as f:
        downloaded = f.readlines()
    # set is faster than list for existence
    downloaded = set([i.strip() for i in downloaded])
else:
    downloaded = set()

for code, urls in tqdm(image_url_dict.items()):
    if code in downloaded:
        pass
    else:
        for image_url in urls:
            image = get_image(image_url)
            save_image('data/images', code, image_url, image)
            DOWNLOADED_IMAGE_LIST.touch(exist_ok=True)
        with open(str(DOWNLOADED_IMAGE_LIST), 'a') as f:
            f.write(f'{code}\n')


