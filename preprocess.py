import json
import csv
import pandas as pd
import glob
import os
import re 

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

def extract_verses_only(lyrics):
    """ Extract all the verses parts of the lyrics while ignoring any other part """
    lyrics = lyrics.replace("|", "\n")
    verse_pattern = re.compile(r'\[Verse[^][]*][^[]*')
    # extract verses blocks
    all_verses = verse_pattern.findall(lyrics)
    all_verses = "\n".join(all_verses)
    # remove the "[Verse...]" boundaries
    verse_no_boundaries = re.sub(r'\[Verse.*?\]', "\n", all_verses)
    # Seperate each verse with exactly one break line
    verse_no_boundaries = re.sub(r'\n{2,}', '\n\n', verse_no_boundaries).strip()
    return verse_no_boundaries

with open("raw_corpus.csv") as corpus:
    csvreader = csv.reader(corpus)
    header = next(csvreader)
    with open("verse_only_corpus.csv", "w") as clean:
        writer = csv.writer(clean)
        writer.writerow(header)
        for row in csvreader:
            row[-1] = extract_verses_only(row[-1])
            writer.writerow(row)

#extract_all_lyrics()