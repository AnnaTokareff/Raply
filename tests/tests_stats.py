import pandas as pd
import numpy as np
from tqdm import tqdm
import json
import itertools
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

def get_all_stats(test_file):
    df = pd.read_csv(test_file)
    print(df.shape)
    #'Unnamed: 0', 'line', 'next_line', 'generated_text',
    #   'orig_l_slurs_count', 'orig_l_slurs_ratio', 'orig_l_categories',
    #   'orig_nl_slurs_count', 'orig_nl_slurs_ratio', 'orig_nl_categories',
    #   'gen_nl_slurs_count', 'gen_nl_slurs_ratio', 'gen_nl_categories',
    #   'rd_test', 'rd_gen'
    slurs_ratios = [df['gen_nl_slurs_ratio'].mean(), df['orig_nl_slurs_ratio'].mean(), df['orig_l_slurs_ratio'].mean()]
    rds =  [df['rd_gen'].mean(), df['rd_test'].mean()]
    counts = [sum(df['orig_l_slurs_count']), sum(df['orig_nl_slurs_count']), sum(df['gen_nl_slurs_count'])]
    print(slurs_ratios)
    print("ratios slurs line, newline, generated", slurs_ratios)
    print("counts line, newline, generated", counts)
    print("rd_gen, rd_test", rds)
    df["rd_gen"].plot.hist()
    plt.show()
    print(rds)
    #df_cat = df[['orig_l_categories', 'orig_nl_categories', 'gen_nl_categories']]
    nls = df["orig_nl_categories"].to_list()
    gens = df["gen_nl_categories"].to_list()
    categories_1 = []
    categories_2 = []
    for i, cat in enumerate(df["orig_l_categories"].to_list()):
        parsed_ol = json.loads(cat.replace('\'', '"')).keys()
        parsed_onl = json.loads(nls[i].replace('\'', '"')).keys()
        parsed_gnl = json.loads(gens[i].replace('\'', '"')).keys()
        combinaisons_1 = list(itertools.product(parsed_ol, parsed_onl))
        combinaisons_2 = list(itertools.product(parsed_ol, parsed_gnl))
        if len(combinaisons_1) == 0:
            categories_1+=[("","")]
        else:
            categories_1+=combinaisons_1
        if len(combinaisons_2) == 0:
            categories_2+=[("","")]
        else:
            categories_2+=combinaisons_2
    cat_ol, cat_onl = list(zip(*categories_1))
    cat_ol2, cat_gnl = list(zip(*categories_2))
    """print(set(cat_ol+cat_onl+cat_gnl))
    labels = ['', 'racial / ethnic slurs', 'sexual orientation / gender', 'bodily fluids / excrement', 'religious offense', 'sexual anatomy / sexual acts']
    cm = confusion_matrix(cat_ol, cat_onl, labels=labels)
    cmd = ConfusionMatrixDisplay(cm, display_labels=labels)
    cmd.plot(xticks_rotation="vertical")
    plt.show()"""

    print(set(cat_ol+cat_onl+cat_gnl))
    labels = ['', 'racial / ethnic slurs', 'sexual orientation / gender', 'bodily fluids / excrement', 'religious offense', 'sexual anatomy / sexual acts']
    cm = confusion_matrix(cat_ol2, cat_gnl, labels=labels)
    cmd = ConfusionMatrixDisplay(cm, display_labels=labels)
    cmd.plot(xticks_rotation="vertical")
    plt.show()
    #sns.heatmap(cm, annot=True)
    # plt.show()


get_all_stats("tests/data/no_slurs/full_no_slurs_test_summary22.csv")

"""corpus_path = './gpt_rap.txt'
test_path = "tests/data/slurs/test_slurs22.csv"

with open(corpus_path) as tr:
    lyrics = tr.read()
    lyrics = lyrics.strip("\n").split("<|endoftext|>")

train, test = train_test_split(lyrics, test_size=0.01)
train = [t.strip() + " <|endoftext|>" for t in train]
test = [t.strip() + " <|endoftext|>" for t in test]
train, test = pd.DataFrame(train), pd.DataFrame(test)
test.to_csv(test_path, index=False)
print(test)"""





