import pandas as pd
import numpy as np
from pathlib import Path
import faiss

parent_ = Path().cwd().parent

def get_movie_df():
    df = pd.read_csv(parent_ / "data/movie_infos_2.csv")
    return df.set_index("movieId")

def get_user_rates_df():
    return pd.read_pickle(parent_ / "data/sorted_ratings.pkl")

def get_embed_vectors():
    str_ = str(parent_ / "output_index/text-embed-04")
    return faiss.read_index(str_)

# print(get_embed_vectors().ntotal)


# get_movie_df()
# df = get_user_rates_df()

# print(parent_.cwd().parent / "data")

# print(df)