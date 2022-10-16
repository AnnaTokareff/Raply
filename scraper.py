from lyricsgenius import Genius
import json
from retry import retry
import logging
import time
logger = logging.basicConfig()

TOKEN =  "pOL7qoeTlL-x-AcrexYQcfoONbSw4YwQBwIJ2bh0lAjljSnTZaNxIPGa5vbNJmjE"
#pOL7qoeTlL-x-AcrexYQcfoONbSw4YwQBwIJ2bh0lAjljSnTZaNxIPGa5vbNJmjE
#Kmu9g1nBxLLztk7cwlZtuLiRum6nAAM7mNqFxQTOQSssLFNrn_W4mkp42-QHfuhO
DELAY = 30
RETRIES = 20

def parse_jsons():
    """ Get each rapper's json file, extract lyrics and metadata"""
    with open("Lyrics_50Cent.json") as f:
        data = json.load(f)

def merge_jsons():
    return 0

def save_last_rapper(rapper):
    with open("last_rapper.txt", mode="w") as f:
        f.write(rapper)

rappers_db = set()
with open('rappers_clean.csv') as f:
    rappers = f.readlines()

for r in rappers:
    art = r.split(",")
    rappers_db.add(art[0])

def get_last_rapper():
    with open("last_rapper.txt") as f:
            last_rapper = f.read()
    return last_rapper

rappers_db = list(sorted(rappers_db))

@retry(tries=RETRIES, delay=DELAY, logger=logger)
def scrape_data():
    last_rapper = get_last_rapper()
    genius = Genius(TOKEN)
    start = rappers_db.index(last_rapper)
    print(start)
    for rapper in rappers_db[start:]: 
        print(rapper)
        last_rapper = rapper
        save_last_rapper(last_rapper)
        artist = genius.search_artist(rapper, sort='popularity',
                                    get_full_info=True)
        artist.save_lyrics()
        time.sleep(30)

scrape_data()
