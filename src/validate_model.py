from pydantic import BaseModel, RootModel
from typing import List, Dict


class MovieInfosOut(BaseModel):
    movieId: int
    title: str
    genres: List[str]
    tags: List[str]
    weight_rating: float


class WatchedMovie(BaseModel):
    movieId: int
    user_rate: float

class WatchedMovieOut(WatchedMovie):
    timestamp:str


class MovieIdsList(BaseModel):
    movieIds: List[int]


class SearchQuery(BaseModel):
    query: str


class MovieTitle(BaseModel):
    title: str

class GenreMovies(BaseModel):
    genre: Dict[str, List[MovieTitle]]

class MoviesResponse(RootModel):
    root: List[Dict[str, List[MovieTitle]]]