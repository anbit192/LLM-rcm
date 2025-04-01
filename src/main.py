import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, status
from validate_model import *
import services

app = FastAPI()

print("Dit me!")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def hello_world():
    return {
        "message":"Dit!"
    }


@app.get("/get_movie/{id}", response_model=MovieInfosOut, status_code=status.HTTP_200_OK)
async def get_movie_by_id(id: int):
    return services.get_movie_by_id(id)


@app.post("/get_movies", response_model=List[MovieInfosOut], status_code=status.HTTP_200_OK)
async def get_movies_infos(id_list:MovieIdsList):
    return services.get_movies_from_ids(id_list.movieIds)


@app.get("/search/{query_str}", response_model=List[MovieInfosOut], status_code=status.HTTP_200_OK)
async def search_movies(query_str):
    return services.search_movie_from_query(query_str)


@app.post("/input_user_movies", response_model=WatchedMovie, status_code=status.HTTP_200_OK)
async def rate_movies(rate: WatchedMovie):
    return services.rate_movie(rate)


@app.get("/get_recommend_movies", response_model=MoviesResponse, status_code=status.HTTP_200_OK)
async def get_recommend_movies():
    return services.recommend_movies()



def main():
    pass


if __name__ == "__main__":
    main()