import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, status
from validate_model import *
import services

app = FastAPI()

# print("Dit me!")

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
        "message":"Ei yoo"
    }


@app.get("/get_movie/{id}", response_model=MovieInfosOut, status_code=status.HTTP_200_OK)
async def get_movie_by_id(id: int):
    """
    Lấy ra thông tin của 1 bộ phim từ Id của phim trong database.
    """
    return services.get_movie_by_id(id)


@app.post("/get_movies", response_model=List[MovieInfosOut], status_code=status.HTTP_200_OK)
async def get_movies_infos(id_list:MovieIdsList):
    """
    Lấy ra thông tin của nhiều bộ phim từ một list các Id có trong database.
    """
    return services.get_movies_from_ids(id_list.movieIds)


@app.get("/search/{query_str}", response_model=List[MovieInfosOut], status_code=status.HTTP_200_OK)
async def search_movies(query_str):
    """
    Tìm kiếm các bộ phim có tên giống với query tìm kiếm.
    """
    return services.search_movie_from_query(query_str)


@app.post("/input_user_movies", response_model=WatchedMovie, status_code=status.HTTP_200_OK)
async def rate_movies(rate: WatchedMovie):
    """
    Đánh giá 1 bộ phim. Nếu muốn đánh giá lại, có thể gửi lại cùng Id của phim đó.
    """
    return services.rate_movie(rate)


@app.get("/get_recommend_movies", response_model=MoviesResponse, status_code=status.HTTP_200_OK)
async def get_recommend_movies():
    """
    Lấy ra 10 phim được recommend, nếu user chưa đánh giá phim nào thì sẽ hiển thị ra 10 phim mặc định của hệ thống.
    """
    return services.recommend_movies()



def main():
    pass


if __name__ == "__main__":
    main()