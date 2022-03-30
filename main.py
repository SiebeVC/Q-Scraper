import requests
import os
from dotenv import load_dotenv

load_dotenv()

url_get_editions = os.getenv('url_get_editions')
url_get_top40 = os.getenv('url_get_top40')

try:
    editons = requests.get(url_get_editions).json()
    last_edition = editons['editions'][0]
except Exception as e:
    print(e)
    print('ERROR getting edition Q-Top 40')

try:
    response = requests.get(url_get_top40.format(last_edition["id"]))
    top40 = response.json()['tracks']

    for i in top40:
        print(i['title'])
except Exception as e:
    print(e)
    print(f'ERROR getting last edition with id {last_edition["id"]} op datum {last_edition["name"]}')