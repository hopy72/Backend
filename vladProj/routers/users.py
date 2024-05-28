from dependencies.db import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import UserInSchema, UserSchema, LikeSchema
from models.pictures import Picture
from models.users import User
from models.collections import Collection
from models.tags import Tag
from models.likes import Like


router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserSchema)
async def create_user(
        new_user: UserInSchema,
        db: Session = Depends(get_db),
):
    new_user_db = User(
        username=new_user.username
    )
    db.add(new_user_db)
    db.commit()
    db.refresh(new_user_db)
    return UserSchema.from_orm(new_user_db)


@router.get("/{username}", response_model=UserSchema)
async def get_user_by_username(
        username: str,
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользоваетль не найден")
    return UserSchema.from_orm(user)


@router.put("/like", response_model=LikeSchema)
async def like(
        new_like: LikeSchema,
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == new_like.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    picture = db.query(Picture).filter(Picture.id == new_like.picture_id).first()
    if not picture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Картинка не найдена")
    new_like_db = Like(
        user_id=new_like.user_id,
        picture_id=new_like.picture_id
    )
    db.add(new_like_db)
    db.commit()
    db.refresh(new_like_db)
    return LikeSchema.from_orm(new_like_db)


@router.put("/unlike", response_model=LikeSchema)
async def unlike(
        bad_like: LikeSchema,
        db: Session = Depends(get_db),
):
    old_like = db.query(Like)\
        .filter(Like.user_id == bad_like.user_id and Like.picture_id == bad_like.picture_id)\
        .first()
    if not old_like:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Лайк уже не стоит")
    res = LikeSchema.from_orm(old_like)
    db.delete(old_like)
    db.commit()
    return res


@router.delete("/{user_id}", response_model=UserSchema)
async def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    res = UserSchema.from_orm(user)
    db.delete(user)
    db.commit()
    return res
