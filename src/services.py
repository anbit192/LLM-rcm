from validate_model import *
from recommender import Recommender
from load_data import *
from models import *
from datetime import datetime
from database import *
from collections import defaultdict
from state import UserSession


movie_df = get_movie_df()
index = get_embed_vectors()

# client = get_google_model()

def _get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if (rate_col.count_documents({}) == 0 and user_col.count_documents({}) == 0):
    test_user = {"email":"testuser@example.com", "username":"TestUser"}
    res1 = user_col.insert_one(test_user)

    ratings = [
        {
            "userId": res1.inserted_id,
            "movieId": 1,
            "user_rate": 4.5,
            "timestamp": _get_current_timestamp()
        },
        {
            "userId": res1.inserted_id,
            "movieId": 2,
            "user_rate": 1,
            "timestamp": _get_current_timestamp()
        },
        {
            "userId":res1.inserted_id,
            "movieId": 3,
            "user_rate": 5.0,
            "timestamp": _get_current_timestamp()
        },
    ]

    rate_col.insert_many(ratings)



def get_all_users():
    return [UserInfo(**doc) for doc in user_col.find()]


def _check_exist(user):
    user_ = user_col.find_one({"email":user.email})
    return user_ is not None


def get_user_by_email(email:str):
    return user_col.find_one({"email":email})

session = UserSession.get_instance()
if not session.is_logged_in():
    user = get_user_by_email("testuser@example.com")
    session.set_user(user)

def get_user_by_id(id):
    # print(id)
    return user_col.find_one({"_id":id})



def create_user(user: UserInfo):
    if (_check_exist(user)):
        raise Exception("Email already exist")
    user_col.insert_one(user.model_dump())
    return user

def get_user_rates(user:UserInfo):
    if (_check_exist(user) is None):
        raise Exception("User does not exist")
    
    user_ = get_user_by_email(email=user.email)
    res = rate_col.find({"userId":user_["_id"]})

    return [WatchedMovieOut(**doc) for doc in res]


def create_rating(user_rate:WatchedMovie):
    # print(user_rate)
    current_user = session.get_user()
    
    res = rate_col.find_one({
        "userId":current_user["_id"],
        "movieId": user_rate.movieId
    })

    if (res is not None):
        print("Editted!")
        return edit_rating(user_rate)
    
    temp = user_rate.model_dump()
    temp["timestamp"] = _get_current_timestamp()
    temp["userId"] = current_user["_id"]

    rate_col.insert_one(temp)
 
    return WatchedMovieOut.model_validate(temp)


def select_user(user: UserInfo):
    user_ = get_user_by_email(user.email)
    if (user_ is None):
        raise Exception("User does not exist")
    session.set_user(user_)

    return user_

def edit_rating(user_rate:WatchedMovie):
    current_user = session.get_user()
    
    res = rate_col.find_one({
        "userId":current_user["_id"],
        "movieId": user_rate.movieId
    })

    curr_time = _get_current_timestamp()

    if (res is not None):
        rate_col.update_one(
            {"_id": res["_id"]},
            {"$set": {
                "user_rate":user_rate.user_rate,
                "timestamp":curr_time
            }}
        )
    else:
        raise Exception("Movie not found")
    
    user_rate.userId = current_user["_id"]
    temp = WatchedMovieOut(
        userId=user_rate.userId,
        movieId=user_rate.movieId,
        user_rate=user_rate.user_rate,
        timestamp=curr_time
    )
    print(temp)
    return temp



def _process_user_input(current_user):

    docs = list(rate_col.find({"userId": current_user["_id"]}))

    id_list = [d["movieId"] for d in docs]
    ratings = [d["user_rate"] for d in docs]
    timestamps = [d["timestamp"] for d in docs]

    user_df = movie_df.loc[id_list].copy()
    user_df["rating"] = ratings
    user_df["timestamp"] = timestamps

    

    return user_df[[
        "vectorID", "title", "genres", "tags",
        "rating", "weight_rating", "timestamp", "page_content", "Actors", "Director", "Plot", "Poster", "Language", "Runtime"
    ]].sort_values("timestamp")

rec = Recommender.get_instance(index, movie_list=_process_user_input(session.get_user()), k_per_item=20, negative_alpha=-1, output_k=50)


def get_movie_by_id(id):
    movies = get_movies_from_ids([id])
    if not movies:
        raise IndexError(f"Movie with id {id} not found.")
    return movies[0]


def get_movies_from_ids(id_list):
    list_input = list(dict.fromkeys(id_list))
    infos = movie_df.loc[list_input][["title", "genres", "tags", "weight_rating", "Plot", "Poster", "Actors", "Director", "Language", "Runtime"]].reset_index()
    infos.rename(columns={"index":"movieId"})

    infos["genres"] = infos["genres"].apply(lambda x: x.split(","))
    infos["tags"] = infos["tags"].apply(lambda x: x.split(","))
    infos["Actors"] = infos["Actors"].apply(lambda x: x.split(","))
    infos["Director"] = infos["Director"].apply(lambda x: x.split(","))

    movies = [MovieInfosOut(**record) for record in infos.to_dict(orient="records")]

    return movies


def search_movie_from_query(query_str):
    query = query_str.replace(",", "")
    res = movie_df[movie_df["title"].str.replace(",", "", regex=False).str.contains(query, case=False, na=False)].reset_index()["movieId"].tolist()[:10]
    return get_movies_from_ids(res)
    


def _categorize_movie(movies):
    movies = movies.reset_index()
    genre_map = defaultdict(list)
    for i in range(len(movies)):
        movie = movies.iloc[i][["movieId","title", "genres", "tags", "weight_rating", "Plot", "Poster", "Actors", "Director", "Language", "Runtime"]]

        
        print(movie[["movieId", "Director"]].tolist())

        

        movie["genres"] = movie["genres"].split(",")
        movie["tags"] = movie["tags"].split(",")
        movie["Actors"] = movie["Actors"].split(",")
        movie["Director"] = movie["Director"].split(",")

        # movie.rename(columns={"index":"movieId"})
        splitted_genres = [g for g in movies.iloc[i]["genres"].split(",")]

        
        for genre in splitted_genres:
            genre_map[genre].append(MovieInfosOut(**movie))
            break
            # print(genre_map)

    return [{ genre: movies } for genre, movies in sorted(genre_map.items())]


def recommend_movies():
    rec.set_movie_list(_process_user_input(session.get_user()))
    top_k = rec.get_top_k()
    movies = movie_df.iloc[top_k]
    # print(movies[["title", "genres"]])
    # print(rec._get_rcm_ranking())
    cat = _categorize_movie(movies)
    print("==========================")
    # print(cat)
    return cat

    
def main():
    print(rec.movie_list)
    recommend_movies()


if __name__ == "__main__":
    main()