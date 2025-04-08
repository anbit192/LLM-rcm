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


@app.post("/create_user", response_model=UserInfo, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserInfo):
    """
    Tạo mới một user nếu chưa tồn tại.
    """
    return services.create_user(user)


@app.get("/get_all_users", response_model=List[UserInfo], status_code=status.HTTP_200_OK)
async def get_all_users():
    """
    Lấy danh sách tất cả user trong hệ thống.
    """
    return services.get_all_users()


@app.post("/select_user", response_model=UserInfo, status_code=status.HTTP_200_OK)
async def select_user(user: UserInfo):
    """
    Chọn user hiện tại để dùng trong hệ thống (giống login tạm thời).
    """
    return services.select_user(user)


@app.get("/get_current_user", response_model=UserInfo, status_code=status.HTTP_200_OK)
async def get_current_user():
    """
    Lấy thông tin user hiện tại đã được chọn.
    """
    return services.session.get_user()
 

@app.get("/get_user_ratings", response_model=List[WatchedMovieOut], status_code=status.HTTP_200_OK)
async def get_user_ratings():
    """
    Lấy tất cả đánh giá của user hiện tại.
    """
    current_user = services.session.get_user()
    return services.get_user_rates(UserInfo(**current_user))






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


@app.post("/input_user_movies", response_model=WatchedMovieOut, status_code=status.HTTP_200_OK)
async def rate_movies(rate: WatchedMovie):
    """
    Đánh giá 1 bộ phim. Nếu muốn đánh giá lại, có thể gửi lại cùng Id của phim đó.
    """
    return services.create_rating(rate)


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