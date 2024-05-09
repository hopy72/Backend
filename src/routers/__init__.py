from dependencies.db import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import UserInSchema, UserSchema
from models.pictures import Picture
from models.users import User
from models.collections import Collection
from models.tags import Tag


user_router = APIRouter()


@user_router.post("/create_user", response_model=UserSchema)
async def create_user(
        new_user: UserInSchema,
        db: Session = Depends(get_db),
):
    new_user_db = User(
        username=new_user.username
    )

    user1 = User(username="user1")
    user2 = User(username="user2")
    pic1 = Picture(path="/dic/pic1")
    pic2 = Picture(path="/dic/pic2")
    db.add(user1)
    db.add(user2)
    db.add(pic1)
    db.add(pic2)
    pic1.users_liked = [user1, user2]
    pic2.users_liked = [user1]

    # по сути весь не мой код начинается отсюда
    db.add(new_user_db)
    db.commit()
    db.refresh(new_user_db)
    # и заканчивается здесь
    return UserSchema.from_orm(new_user_db)
