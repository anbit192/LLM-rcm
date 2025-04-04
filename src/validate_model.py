from pydantic import BaseModel, RootModel
from typing import List, Dict


class MovieInfosOut(BaseModel):
    movieId: int
    title: str
    genres: List[str]
    tags: List[str]
    weight_rating: float
    model_config = {
            "json_schema_extra": {
                        "examples": [
                            {
                                "movieId": 1,
                                "title": "Toy Story",
                                "genres": ["Animation", "Family"],
                                "tags": ["kids", "family"],
                                "weight_rating": 3.9
                }
            ]
        }
    }


class WatchedMovie(BaseModel):
    movieId: int
    user_rate: float = 3.0
    model_config = {
            "json_schema_extra": {
                        "examples": [
                        {
                                "movieId": 1,
                                "user_rate":3.0
                        }
            ]
        }
    }

class WatchedMovieOut(WatchedMovie):
    timestamp:str
    model_config = {
            "json_schema_extra": {
                        "examples": [
                        {
                                "movieId": 1,
                                "user_rate":3.0,
                                "timestamp":"2025-08-19"
                        }
            ]
        }
    }


class MovieIdsList(BaseModel):
    movieIds: List[int]
    model_config = {
            "json_schema_extra": {
                        "examples": [
                        {
                                "movieIds": [1, 2, 3]
                        }
            ]
        }
    }


class SearchQuery(BaseModel):
    query: str
    model_config = {
            "json_schema_extra": {
                        "examples": [
                        {
                                "query": "toy   st",
                        }
            ]
        }
    }


class MovieTitle(BaseModel):
    title: str

class GenreMovies(BaseModel):
    genre: Dict[str, List[MovieTitle]]

class MoviesResponse(RootModel):
    root: List[Dict[str, List[MovieTitle]]]
    model_config = {
        "json_schema_extra": {
            "examples": [
                [
                {
                    "Genre1": [
                        {"title": "Movie1"},
                        {"title": "Movie2"}
                    ]
                },
                {
                    "Genre2": [
                        {"title": "Movie3"},
                        {"title": "Movie2"}
                    ]
                }
                ]
            ]
        }
    }
