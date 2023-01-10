import pandas as pd

def match_slurs(slurs_filename, data_filename):
    df_slurs = pd.read_csv(slurs_filename, sep=";")
    slurs = dict(zip(df_slurs.text, df_slurs.severity_rating))
    with open(data_filename, "w") as generated:
        text = generated.read()
    text.split("")

def get_matched_words(df, slurs):
    for ind, (_, row) in enumerate(df.iterrows()):
        match_words = []
        new_set = set()
        for word in new_set:
            if word in slurs:
                match_words.append(word)
        row["slurs"] = match_words
        row["num_slurs"] = len(row["slurs"])
        formula_song = 0.0
        for word in match_words:
            formula_song += float(slurs[word])
        row["formula_song"] = formula_song / len(row["lyrics_tokenized"])
        df.at[ind] = row