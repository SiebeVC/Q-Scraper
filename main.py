from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import  CORSMiddleware

import os
import pickle
import datetime

from mainapp import reload_playlist


app = FastAPI()

origins = [
    "http://localhost",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
spot_client = os.getenv('spot_client')
spot_key = os.getenv('spot_key')
username = os.getenv('username')
url_editions = os.getenv('url_get_editions')
url_top40 = os.getenv('url_get_top40')
playlist = os.getenv('playlist_id')


@app.get("/", response_class=HTMLResponse)
def read_root():
    html = ''
    with open('./test.html', 'r') as f:
            html = f.read()
    return html


@app.get('/top40')
def reload_TOP40():
    if not check_update('top40'):
        return {"action": 'Deze actie is te recent uitgevoerd door iemand. Probeer binnen een paar minuten opnieuw'}

    action = reload_playlist(spot_client, spot_key, username, url_editions, url_top40, playlist)
    return {"action": action}

def check_update(name):
    with open('updates.pickle', 'rb') as fr:
        try:
            dic = pickle.load(fr)
        except:
            dic = dict()

    if name in dic.keys():
        last_date = dic[name]['date']
        if (datetime.datetime.now() - last_date).total_seconds() > 5*60:
            dic[name]['date'] = datetime.datetime.now()
            with open('updates.pickle', 'wb') as to:
                pickle.dump(dic, to, protocol=pickle.HIGHEST_PROTOCOL)
            return True
        return False

    dic[name] = dict()
    dic[name]['date'] = datetime.datetime.now()
    with open('updates.pickle', 'wb') as to:
        pickle.dump(dic, to, protocol=pickle.HIGHEST_PROTOCOL)
    return True
        
