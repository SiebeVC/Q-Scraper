from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import  CORSMiddleware

import os

#from mainapp import reload_playlist


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

@app.get("/", response_class=HTMLResponse)
def read_root():
    return '<h1>Test</h1>'


@app.get('/top40')
def reload_TOP40():
    print(spot_client)
    return {"action": "reload"}