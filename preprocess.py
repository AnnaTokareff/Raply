import json
import csv
import pandas as pd
import glob
import os
import re 
import string 
from langdetect import detect

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
    # seperate each verse with exactly one break line
    verse_no_boundaries = re.sub(r'\n{2,}', '\n\n', verse_no_boundaries).strip()
    no_weird_endings = re.compile(r'You might also like\d*Embed"')
    verse_no_boundaries = no_weird_endings.sub('',verse_no_boundaries)
    verse_no_boundaries = re.sub(r'\s\s+' , ' ', verse_no_boundaries).strip() 
    return verse_no_boundaries

def is_english_text(lyrics):
    try:
        language = detect(row[-1])
        if language == 'en':
            return True
    except:
        language = "error"
    return False

def count_sentences(lyric):
    if not lyric:
        return 0
    lyric = lyric.split("\n")
    return len(lyric)

s=0
with open("raw_corpus.csv") as corpus:
    csvreader = csv.reader(corpus)
    header = next(csvreader)
    with open("clean_corpus_eng_only.csv", "w") as clean:
        writer = csv.writer(clean)
        writer.writerow(header)
        for row in csvreader:
            row[-1] = extract_verses_only(row[-1])
            # ignore empty lyrics and songs with less than 3 lines
            if count_sentences(row[-1]) < 3:
                    continue
            # check if language is english
            if is_english_text(row[-1]):
                writer.writerow(row)
print(s)