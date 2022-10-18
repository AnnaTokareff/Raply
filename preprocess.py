import json
import csv
import pandas as pd
import glob
import os

header = ['rapper', 'song', 'year', 'lyrics']
def extract_lyrics(filename):
    """Get each rapper's json file, extract lyrics and metadata"""
    with open("{}.json".format(filename)) as f:
        data = json.load(f)
    with open("{}.csv".format(filename), mode="w", encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for song in data["songs"]:
            year = None
            if song["release_date_components"]:
                year = song["release_date_components"]["year"]
            lyrics = song["lyrics"]
            lyrics  = lyrics.replace("\n", "|")
            row = [song["artist"], song["title"], 
                    year, lyrics]
            writer.writerow(row)

def extract_all_lyrics():
    extension = 'json'
    all_filenames = [os.path.splitext(i)[0] for i in glob.glob('data/*.{}'.format(extension))]
    for filename in all_filenames: extract_lyrics(filename)
    combined_csv = pd.concat([pd.read_csv(f+".csv") for f in all_filenames ])
    combined_csv.to_csv( "raw_corpus.csv", index=False, encoding='utf-8')

extract_all_lyrics()