import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ast 
from nltk import word_tokenize

df = pd.read_csv("data/raw/slurs_annotated_data.csv")
#print(df["formula_2_lyrics"].describe())

def count_stats(df):
    k = df["lyrics_tokenized"]
    k["tokens"] = df["lyrics_splitted"].apply(lambda text: word_tokenize(text))
    k["size"] = k["tokens"].str.len()
    print("tokens", k["size"].sum())
    print(k.size)


df = df[df['formula_2_lyrics'] <= 0.05]
df.to_csv("Mitislurs.csv")