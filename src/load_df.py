import pandas as pd
import numpy as np
from pathlib import Path

parent_ = Path().cwd().parent

def get_movie_df():
    return pd.read_csv(parent_ / "data/movie_infos_2.csv")

def get_user_rates_df():
    return pd.read_pickle(parent_ / "data/sorted_ratings.pkl")


# get_movie_df()
# df = get_user_rates_df()

# print(parent_.cwd().parent / "data")

# print(df)