import numpy as np
import faiss
from config import *
from load_data import *
from models import *


movie_df = get_movie_df()
user_rates = get_user_rates_df()

index = get_embed_vectors()

client = get_google_model()

def get_user_movies():
    user_dict = {}

    while (True):
        try:
            input_movie_id = input("Input movie ID: ").strip()
            if (input_movie_id == "exit"):
                break
            input_movie_id = int(input_movie_id)

            if input_movie_id not in movie_df.index:
                raise ValueError("Movie ID not found in database.")

            input_rating = input("Rating of that movie: ").strip()
            input_rating = float(input_rating)

            if (input_rating < 0 or input_rating > 5):
                raise ValueError("Rating must be between 0 and 5!!")
            
            user_dict[input_movie_id] = input_rating
        except ValueError as e:
            print(f"Invalid input: {e} Try again.")
        except Exception as e:
            print(f"Unexpected error: {e}. Try again.")
    
    id_list = list(user_dict.keys())
    rating_list = [user_dict[id] for id in id_list]

    user_df = movie_df.loc(id_list)
    user_df["rating"] = rating_list

    return user_df


def main():
    pass


if __name__ == "__main__":
    main()