from typing import Optional, List
from pydantic import BaseModel


class UserInSchema(BaseModel):
    email: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "mistertwister@mail.com",
            }
        }

        from_attributes = True


class UserSchema(BaseModel):
    id: int
    email: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "email": "mistertwister@mail.com",
                "collections": [1, 2, 3],
            }
        }

        from_attributes = True


class LikeInSchema(BaseModel):
    user_id: int
    picture_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "picture_id": 321,
            }
        }

        from_attributes = True


class LikeSchema(BaseModel):
    user_id: int
    picture_id: int
    is_liked: bool

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "picture_id": 321,
                "is_liked": True,
            }
        }

        from_attributes = False


class TagInSchema(BaseModel):
    name: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "funny",
            }
        }

        from_attributes = True


class TagSchema(BaseModel):
    id: int
    name: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "name": "funny",
            }
        }

        from_attributes = True


class PictureSchema(BaseModel):
    id: int
    path: str
    tags: List[TagSchema]

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "path": "cat meme.jpg",
                "tags": [
                    {
                        "id": 1,
                        "name": "funny",
                    },
                    {
                        "id": 2,
                        "name": "cat",
                    },
                    {
                        "id": 3,
                        "name": "meme",
                    }
                ],
            }
        }

        from_attributes = True


class PictureUpdateSchema(BaseModel):
    id: int
    tags: List[int]

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "tags": [1, 2, 3],
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
                "author_id": 23,
                "pictures": [1, 2, 3],
            }
        }

        from_attributes = True


class CollectionSchema(BaseModel):
    id: int
    name: str
    author_id: int
    pictures: List[PictureSchema]

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "name": "Best memes 2024",
                "author_id": 23,
                "pictures": [
                    {
                        "id": 1,
                        "path": "cat meme1.jpg",
                        "tags": [1, 2, 3],
                    },
                    {
                        "id": 2,
                        "path": "cat meme2.jpg",
                        "tags": [1, 2, 3],
                    },
                    {
                        "id": 3,
                        "path": "cat meme3.jpg",
                        "tags": [1, 2, 3],
                    }
                ],
            }
        }

        from_attributes = True


class CollectionUpdateSchema(BaseModel):
    id: int
    name: Optional[str] = None
    pictures: Optional[List[int]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "name": "Best memes 2024",
                "pictures": [1, 2, 3],
            }
        }

        from_attributes = True


class CollectionAndPicsSchema(BaseModel):
    id: int
    pictures: List[int]

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "pictures": [1, 2, 3],
            }
        }

        from_attributes = True
