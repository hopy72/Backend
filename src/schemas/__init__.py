from typing import Optional
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
    id: Optional[int] = None
    username: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "username": "Mister Twister",
            }
        }

        from_attributes = True
