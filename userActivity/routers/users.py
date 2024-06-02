from dependencies.db import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import UserInSchema, UserSchema, LikeSchema, LikeInSchema
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
    user = db.query(User).filter(User.email == new_user.email).first()
    if user:
        raise HTTPException(status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                            detail="Пользователь с таким юзернеймом уже существует")
    new_user_db = User(
        email=new_user.email
    )
    db.add(new_user_db)
    db.commit()
    db.refresh(new_user_db)
    return UserSchema.from_orm(new_user_db)


@router.get("/email/{email}", response_model=UserSchema)
async def get_user_by_email(
        email: str,
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользоваетль не найден")
    return UserSchema.from_orm(user)


@router.get("/id/{user_id}", response_model=UserSchema)
async def get_user_by_id(
        user_id: int,
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользоваетль не найден")
    return UserSchema.from_orm(user)


@router.put("/like", response_model=LikeSchema)
async def toggle_like(
        new_like: LikeInSchema,
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == new_like.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    picture = db.query(Picture).filter(Picture.id == new_like.picture_id).first()
    if not picture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Картинка не найдена")
    old_like = db.query(Like)\
        .filter(Like.user_id == new_like.user_id and Like.picture_id == new_like.picture_id).first()
    if old_like:
        like_out = LikeSchema(user_id=old_like.user_id, picture_id=old_like.picture_id, is_liked=False)
        db.delete(old_like)
        db.commit()
    else:
        new_like_db = Like(user_id=new_like.user_id, picture_id=new_like.picture_id)
        db.add(new_like_db)
        db.commit()
        db.refresh(new_like_db)
        like_out = LikeSchema(user_id=new_like_db.user_id, picture_id=new_like_db.picture_id, is_liked=True)

    return like_out


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
