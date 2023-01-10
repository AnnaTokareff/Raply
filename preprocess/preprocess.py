import json
import csv
import pandas as pd
import glob
import os
import re 
import string 
from langdetect import detect
from lyrics import Lyrics

FORMULAS_THRESHOLDS = {
    1 : 0.004852,
    2 : 0.056121
}
SONG_TAGS = ['remix', 'instrumental', 'interlude', 'intro']

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
    all_filenames = [os.path.splitext(i)[0] for i in glob.glob('data/scraped/*.{}'.format(extension))]
    for filename in all_filenames: extract_lyrics(filename)
    combined_csv = pd.concat([pd.read_csv(f+".csv") for f in all_filenames ])
    combined_csv.to_csv( "raw_corpus.csv", index=False, encoding='utf-8')

def clean_extract_verses_only(lyrics):
    """ Clean unwanted parts and 
        extract all the verses parts of the lyrics while ignoring any other part """
    lyrics = lyrics.replace("|", "\n")
    verse_pattern = re.compile(r'\[Verse[^][]*][^[]*')
    # extract verses blocks
    all_verses = verse_pattern.findall(lyrics)
    all_verses = "\n".join(all_verses)
    # remove the "[Verse...]" boundaries
    verse_no_boundaries = re.sub(r'\[Verse.*?\]', "\n", all_verses)
    # seperate each verse with exactly one break line
    verse_no_boundaries = re.sub(r'\n{2,}', '\n\n', verse_no_boundaries).strip()
    verse_no_boundaries = verse_no_boundaries.replace('You might also like', '')
    verse_no_boundaries = re.sub(r'\d*Embed' , ' ', verse_no_boundaries)
    # remove text between brackets
    verse_no_boundaries = re.sub(r'\([^()]*\)', '', verse_no_boundaries)
    verse_no_boundaries = re.sub(r'\s\s+' , ' ', verse_no_boundaries).strip()
    return verse_no_boundaries

def is_english_text(lyrics):
    try:
        language = detect(lyrics)
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

def generate_clean_corpus():
    with open("data/raw/raw_corpus.csv") as corpus:
        csvreader = csv.reader(corpus)
        header = next(csvreader)
        with open("data/clean/clean_corpus_eng_only.csv", "w") as clean:
            writer = csv.writer(clean)
            writer.writerow(header)
            for row in csvreader:
                for tag in SONG_TAGS: 
                    if tag in row[1].lower():
                        continue 
                row[-1] = clean_extract_verses_only(row[-1])                
                # ignore empty lyrics and songs with less than 3 lines
                if count_sentences(row[-1]) < 3:
                        continue
                # check if language is english
                if is_english_text(row[-1]):
                    writer.writerow(row)

def prepare_gpt2_data_slurs():
    # prepare for gpt2
    with open("data/clean/clean_corpus_eng_only.csv") as corpus:
            csvreader = csv.reader(corpus)
            header = next(csvreader)
            with open("gpt_rap.txt", "w") as gpt_rap:
                for row in csvreader:
                    paragraphs = row[-1].split("\n\n")
                    for par in paragraphs:
                        sentences = par.split("\n")
                        slice_at = len(sentences) - len(sentences) % 2
                        sentences = sentences[:slice_at]
                        slice1 = sentences[::2]
                        slice2 = sentences[1::2]
                        merged = ["Line: {} \nNext Line: {}\n<|endoftext|>\n".format(line, next_line)
                                        for line, next_line in zip(slice1, slice2)]
                        merged = "\n".join(merged)
                        #print(merged)
                        gpt_rap.write(merged)

def prepare_gpt3_data_slurs():
    # prepare for gpt3
    with open("data/clean/clean_corpus_eng_only.csv") as corpus:
            csvreader = csv.reader(corpus)
            header = next(csvreader)
            with open("data/clean/gpt3_rap.csv", "w") as gpt_rap:
                writer = csv.writer(gpt_rap)
                writer.writerow(["lyrics"])
                for row in csvreader:
                    paragraphs = row[-1].split("\n\n")
                    for par in paragraphs:
                        sentences = par.split("\n")
                        slice_at = len(sentences) - len(sentences) % 2
                        sentences = sentences[:slice_at]
                        slice1 = sentences[::2]
                        slice2 = sentences[1::2]
                        merged = ["Line: {} \nNext Line: {}\n<|endoftext|>\n".format(line, next_line)
                                        for line, next_line in zip(slice1, slice2)]
                        for m in merged : writer.writerow([m])

def prp_gpt2_data_no_slurs(output_file, formula_type=2):
    df = pd.read_csv("data/clean/slurs_annotated_data.csv")
    df = df[df['formula_2_lyrics'] <= 0.03]#FORMULAS_THRESHOLDS[formula_type]]
    print(len(df))
    lyrics = df['lyrics'].to_list()
    output_filename = "{}_f{}.txt".format(output_file, formula_type)
    with open(output_filename, "w") as gpt_rap:
        for l in lyrics:
            merged = reformat_lyrics(l)
            merged = "\n".join(merged) + "\n"
            gpt_rap.write(merged)

def check_high_quality_text(line, next_line):
    lyrics_obj = Lyrics(text=line+"\n"+next_line, print_stats=False, 
          language="english")
    rl = lyrics_obj.get_avg_rhyme_length()
    return has_end_rhyme(line, next_line) or rl > 1

def has_end_rhyme(vow1, vow2):
  return vow1[-1] == vow2[-1]

def filter_rhyming_only():
    with open("data/clean/gpt_rap.txt") as gpt_rap:
        lyrics = gpt_rap.read()
        couples = lyrics.split("<|endoftext|>")
    couples = [t.split("Next Line:") for t in couples]
    for i, _ in enumerate(couples) : couples[i][0] = couples[i][0].strip().replace("Line: ", "")    
    with open("data/clean/gpt_rap_gold.txt", "w") as gpt_rap:
        for c in couples:
            if len(c)==2:
                line, next_line = c[0], c[1]
                if check_high_quality_text(line, next_line):
                    instance = line + "\n" + next_line + "\n" + "<|endoftext|>" + "\n"
                    gpt_rap.write(instance)


def reformat_lyrics(lyrics):
    paragraphs = lyrics.split("\n\n")
    for par in paragraphs:
        sentences = par.split("\n")
        slice_at = len(sentences) - len(sentences) % 2
        sentences = sentences[:slice_at]
        slice1 = sentences[::2]
        slice2 = sentences[1::2]
        merged = ["Line: {} \nNext Line: {}\n<|endoftext|>\n".format(line, next_line)
                        for line, next_line in zip(slice1, slice2)]
        return merged

def prp_gpt2_data_para(output_file):
    df = pd.read_csv("data/clean/slurs_annotated_data.csv")
    print(len(df))
    lyrics = df['lyrics'].to_list()
    print(len(lyrics))
    output_filename = "{}.txt".format(output_file)
    with open(output_filename, "w") as gpt_rap:
        for l in lyrics:
            merged = format_per_paragraph(l)
            merged = "\n".join(merged) + "\n"
            gpt_rap.write(merged)


def format_per_paragraph(lyrics):
    paragraphs = lyrics.split("\n\n")
    slices = []
    for par in paragraphs:
        sentences = par.split("\n")
        sentences = ["Line: " + s for s in sentences]
        slice = [ "\n".join(sentences[i * 4:(i + 1) * 4]) + "\n<|endoftext|>" for i in range((len(sentences) + 4 - 1) // 4 )]
        slices+=slice
    return slices

#generate_clean_corpus()
prp_gpt2_data_para("gpt_rap_para")
#prp_gpt2_data_no_slurs(formula_type=1)
#prp_gpt2_data_no_slurs(formula_type=2)
#prp_gpt2_data_no_slurs("gpt2_rap_nosl_th3")

#filter_rhyming_only()
"""with open("gpt_rap_gold.txt", "r") as tr:
    lyrics = tr.read()
    lyrics = lyrics.split("<|endoftext|>")

with open("gpt_rap_gold_final.txt", "w") as tr:
    for l in lyrics:
        try:
            line, next_line = l.strip().split("\n")
            line = "Line: " + line
            next_line = "Next line: " + next_line
            inst = line + "\n" + next_line + "\n" + "<|endoftext|>" + "\n"
            tr.write(inst)
        except:
            print(l)
        #print(line, next_line)"""
