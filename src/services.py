from validate_model import *
from recommender import Recommender
from load_data import *
from models import *
from datetime import datetime
from state import *
from collections import defaultdict


movie_df = get_movie_df()
index = get_embed_vectors()

client = get_google_model()

default_user_watched = {
    1: (5.0, '2025-04-01 12:50:09'), 
    2: (1.0, '2025-04-01 12:50:26'), 
    3: (3.0, '2025-04-02 12:50:26')
}

def _process_user_input(user_dict):
    if (len(user_dict) <= 0):
        user_dict = default_user_watched

    id_list = list(user_dict.keys())
    ratings, timestamps = zip(*user_dict.values())

    user_df = movie_df.loc[id_list].copy()
    user_df["rating"] = ratings
    user_df["timestamp"] = timestamps

    return user_df[["vectorID", "title", "genres", "tags", "rating", "weight_rating", "timestamp", "page_content"]]

rec = Recommender.get_instance(index, movie_list=_process_user_input(user_watched), k_per_item=15, negative_alpha=-1)

def get_movie_by_id(id):
    movies = get_movies_from_ids([id])
    if not movies:
        raise IndexError(f"Movie with id {id} not found.")
    return movies[0]


def get_movies_from_ids(id_list):
    list_input = list(dict.fromkeys(id_list))
    infos = movie_df.loc[list_input][["title", "genres", "tags", "weight_rating"]].reset_index()
    infos.rename(columns={"index":"movieId"})

    infos["genres"] = infos["genres"].apply(lambda x: x.split(","))
    infos["tags"] = infos["tags"].apply(lambda x: x.split(","))

    movies = [MovieInfosOut(**record) for record in infos.to_dict(orient="records")]

    return movies


def search_movie_from_query(query_str):
    query = query_str
    res = movie_df[movie_df["title"].str.contains(query, case=False, na=False)].reset_index()["movieId"].tolist()[:10]
    return get_movies_from_ids(res)
    

def rate_movie(rate):
    movieId = rate.movieId
    movies = get_movie_by_id(movieId)

    if not movies:
        raise Exception("Movie not exist in database")

    user_watched[movieId] = (rate.user_rate, _get_current_timestamp())
    print(user_watched)
    return rate


def _get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _categorize_movie(movies):
    genre_map = defaultdict(list)
    for i in range(len(movies)):
        title = movies.iloc[i]["title"]
        splitted_genres = [g for g in movies.iloc[i]["genres"].split(",")]
        
        for genre in splitted_genres:
            genre_map[genre].append(
                {
                    "title": title
                }
            )

    return [{ genre: movies } for genre, movies in sorted(genre_map.items())]


def recommend_movies():
    if (len(user_watched) > 0):
        rec.set_movie_list(_process_user_input(user_watched))
    top_k = rec.get_top_k()
    movies = movie_df.iloc[top_k]
    print(movies[["title", "genres"]])
    print(rec._get_rcm_ranking())
    return _categorize_movie(movies)


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
    [
        {{
            "Genre1": [
                {{"title": "Movie Title 1"}},
                {{"title": "Movie Title 3"}}
            ]
        }},
        {{
            "Genre2": [
                {{"title": "Movie Title 1"}},
                {{"title": "Movie Title 5"}},
                ...
            ]
        }},
        ...
    ]


    Here's the text:
    {res.text}

    Please return ONLY the JSON in the format above, WITHOUT any explaination, additional informations or enclosing triple backticks.

    """

    final_res = client.models.generate_content(
        model=GEN_MODEL,
        contents=[system_prompt_2, user_prompt_2]
    )

    print(final_res.text)

    return MoviesResponse.model_validate_json(final_res.text.strip("```json").strip("```").strip())


    
