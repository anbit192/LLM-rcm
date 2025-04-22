from pydantic import BaseModel, RootModel, Field, GetCoreSchemaHandler
from typing import List, Dict, Optional
from bson import ObjectId
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_wrap_validator_function(
            cls._validate, core_schema.str_schema()
        )

    @classmethod
    def _validate(cls, value: str, info) -> ObjectId:
        if isinstance(value, ObjectId):
            return value
        if isinstance(value, str) and ObjectId.is_valid(value):
            return ObjectId(value)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema.update(type="string")
        return json_schema
    


class MovieInfosOut(BaseModel):
    movieId: int
    title: str
    genres: List[str]
    tags: List[str]
    weight_rating: float
    Actors: List[str]
    Plot: str
    Poster:str
    Director: List[str]
    Language: str
    Runtime:str

    model_config = {
            "json_schema_extra": {
                        "examples": [
                            {
                                "movieId": 1,
                                "title": "Toy Story",
                                "genres": ["Animation", "Family"],
                                "tags": ["kids", "family"],
                                "weight_rating": 3.9,
                                "Actors": ["Tom Hanks", "Tim Allen", "Don Rickles"],
                                "Plot": "example plot",
                                "Poster": "example url",
                                "Director": ["John Lasseter"],
                                "Language":"English",
                                "Runtime":"81 min"
                }
            ]
        }
    }


class WatchedMovie(BaseModel):
    userId: Optional[PyObjectId] = None
    movieId: int
    user_rate: float = 3.0

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "movieId": 1,
                "user_rate": 3.0
            }
        }


class WatchedMovieOut(WatchedMovie):
    timestamp:str
    model_config = {
            "json_schema_extra": {
                        "examples": [
                        {
                                "userId":"67f24f2ab996a5cf558def58",
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
    root: List[Dict[str, List[MovieInfosOut]]]
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


class UserInfo(BaseModel):
    email: str
    username: str

