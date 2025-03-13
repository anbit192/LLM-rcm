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

def augmented(movies):
    recommend_contents = "\n======\n".join(
    movies["page_content"].tolist())

    system_prompt = (
    "You are an AI assistant majoring in categorize things. Your task is to group the given movies by their genres into categories"
    """Your task is as follows:
        1. Group the movies into categories based on their genres.
        2. If a movie has multiple genres, assign it to the category corresponding to its primary genre (choose the first listed genre).
        3. For each category, list all movies that belong to that category."""
    )

    user_prompt = f"""
    Below is a list of movies. Each movie is formatted as follows:

    --------------------------------------------------
    Movie Format:
    (Title)
    (Genres)        // A comma-separated list of genres.
    (Tags)          // A comma-separated list of tags.
    --------------------------------------------------
    For example:
    Now, Voyager (1942)
    Drama, Romance
    Classic, Timeless, Iconic
    --------------------------------------------------

    Please group these movies into categories based on their genres in the following format:
    **Genre1**
    - Movie1
    - Movie2
    ...

    **Genre2**
    - Movie1
    ...

    Here are the movies:
    {recommend_contents}
    """

    res = client.models.generate_content(
        model=GEN_MODEL,
        contents=[system_prompt, user_prompt]
    )

    system_prompt_2 = "You are a JSON formatter AI assistant, your job is convert given data into valid JSON format."
    user_prompt_2 = f"""Please convert the following text into JSON format as follow:  
    {{
    "Genre1": [
        {{"title": "Movie Title 1"}},
        {{"title": "Movie Title 3"}}
    ],
    "Genre2": [
        {{"title": "Movie Title 1"}},
        {{"title": "Movie Title 5"}},
        ...
    ],
    ...
    }}


    Here's the text:
    {res.text}

    Please return ONLY the JSON in the format above, WITHOUT any explaination, additional informations or enclosing triple backticks.

    """

    final_res = client.models.generate_content(
        model=GEN_MODEL,
        contents=[system_prompt_2, user_prompt_2]
    )

    return final_res.text.strip("```json").strip("```").strip()




def main():
    movie_list = get_user_movies()
    
    rec = Recommender.get_instance(index=index, movie_list=movie_list, output_k=20)
    print(rec._get_rcm_ranking())
    top_k = rec.get_top_k()

    print(movie_df.iloc[top_k][["title", "genres"]])

    print(augmented(movie_df.iloc[top_k]))

    print("Done")


if __name__ == "__main__":
    main()