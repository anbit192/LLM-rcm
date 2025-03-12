import numpy as np
from config import *
from load_data import *
from models import *
from datetime import datetime
from recommender import Recommender


movie_df = get_movie_df()
user_rates = get_user_rates_df()
index = get_embed_vectors()

client = get_google_model()


def _get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_user_movies():
    user_dict = {}

    while (True):
        try:
            input_movie_id = input("Input movie ID (exit to quit): ").strip()
            if (input_movie_id == "exit"):
                break
            input_movie_id = int(input_movie_id)

            if input_movie_id not in movie_df.index:
                raise ValueError("Movie ID not found in database.")

            input_rating = input("Rating of that movie: ").strip()
            input_rating = float(input_rating)
            current_timestamp = _get_current_timestamp()

            if (input_rating < 0 or input_rating > 5):
                raise ValueError("Rating must be between 0 and 5!!")
            
            user_dict[input_movie_id] = (input_rating, current_timestamp)
        except ValueError as e:
            print(f"Invalid input: {e} Try again.")
        except Exception as e:
            print(f"Unexpected error: {e}. Try again.")
    
    id_list = list(user_dict.keys())
    rating_list = [user_dict[id][0] for id in id_list]
    time_list = [user_dict[id][1] for id in id_list]

    # print(f"id list: {id_list}")
    # print(f"ratings: {rating_list}")

    user_df = movie_df.loc[id_list]
    user_df["rating"] = rating_list
    user_df["timestamp"] = time_list

    return user_df[["vectorID", "title", "genres", "tags", "rating", "weight_rating", "timestamp", "page_content"]]




def main():
    movie_list = get_user_movies()
    
    rec = Recommender.get_instance(index=index, movie_list=movie_list, output_k=20)
    print(rec._get_rcm_ranking())
    top_k = rec.get_top_k()

    print(movie_df.iloc[top_k][["title", "genres"]])

    print("Done")


if __name__ == "__main__":
    main()