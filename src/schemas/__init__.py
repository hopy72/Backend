from typing import Optional, List
from pydantic import BaseModel


class UserInSchema(BaseModel):
    username: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "Mister Twister",
            }
        }

        from_attributes = True


class UserSchema(BaseModel):
    id: int
    username: str
    collections: Optional[List[int]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "username": "Mister Twister",
                "collections": ["1", "2", "3"],
            }
        }

        from_attributes = True


class CollectionInSchema(BaseModel):
    name: str
    author_id: int
    pictures: Optional[List[int]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Best memes 2024",
                "author_id": "23",
                "pictures": ["1", "2", "3"],
            }
        }

        from_attributes = True


class CollectionSchema(BaseModel):
    id: int
    name: str
    author_id: int
    pictures: Optional[List[int]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "name": "Best memes 2024",
                "author_id": "23",
                "pictures": ["1", "2", "3"],
            }
        }

        from_attributes = True


class CollectionUpdateSchema(BaseModel):
    id: int
    name: str
    pictures: Optional[List[int]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "name": "Best memes 2024",
                "pictures": ["1", "2", "3"],
            }
        }

        from_attributes = True
