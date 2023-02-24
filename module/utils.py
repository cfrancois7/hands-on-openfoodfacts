import requests, shutil
import re
from pathlib import Path

def parse(string, prefix):
    code = string['code']
    if len(code) > 8:
        tmp = re.split(r'(...)(...)(...)(.*)$', code)[1:-1]
    else:
        tmp = [code]
    newprefix = prefix + '/'.join(tmp) + '/'
    to_check = ('front_', 'ingredients_', 'nutrition_')
    names = [name for name in string['images'].keys()
             if not name.startswith(to_check)]
    urls = [f'{newprefix}{s}.400.jpg' for s in names]
    return urls

def get_image(image_url):
    r = requests.get(image_url, stream = True)
    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True
        # Open a local file with wb ( write binary ) permission.
    return r.raw

def save_image(repository, code, image_url, image):
    filename = image_url.split('/')[-1]
    Path(f'{repository}/{code}').mkdir(parents=True, exist_ok=True)
    with open(f'{repository}/{code}/{code}__{filename}','wb') as f:
        shutil.copyfileobj(image, f)