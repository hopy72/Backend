from typing import List

from dependencies.db import get_db
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from schemas import CollectionSchema, CollectionInSchema, CollectionUpdateSchema, CollectionAndPicsSchema
from models.pictures import Picture
from models.users import User
from models.collections import Collection
from models.tags import Tag
from models.col_to_pic_enrol import CollectionToPictureEnrollment


router = APIRouter(prefix="/collections", tags=["collections"])


@router.post("", response_model=CollectionSchema)
async def create_collection(
        new_collection: CollectionInSchema,
        db: Session = Depends(get_db),
):
    new_author = db.query(User).filter(User.id == new_collection.author_id).first()
    if not new_author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Не найден автор коллекции с указанным id")
    new_collection_db = Collection(
        name=new_collection.name,
        author_id=new_collection.author_id,
        pictures=[] if not new_collection.pictures else
        db.query(Picture).filter(Picture.id.in_(new_collection.pictures)).all()
    )
    db.add(new_collection_db)
    db.commit()
    db.refresh(new_collection_db)
    return CollectionSchema.from_orm(new_collection_db)


@router.get("/username/{username}", response_model=List[CollectionSchema])
async def get_user_collections_by_username(
        username: str,
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользоваетль не найден")
    collections = db.query(Collection).filter(Collection.author_id == user.id).all()  # noqa
    return [CollectionSchema.from_orm(col) for col in collections]


@router.get("/id/{id}", response_model=List[CollectionSchema])
async def get_user_collections_by_id(
        user_id: int,
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользоваетль не найден")
    collections = db.query(Collection).filter(Collection.author_id == user.id).all()  # noqa
    return [CollectionSchema.from_orm(col) for col in collections]


@router.put("", response_model=CollectionSchema)
async def update_collection(
        new_collection: CollectionUpdateSchema,
        db: Session = Depends(get_db),
):
    old_collection = db.query(Collection).filter(Collection.id == new_collection.id).first()
    if not old_collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Коллекция не найдена")
    if new_collection.name:
        old_collection.name = new_collection.name
    if new_collection.pictures:
        old_collection.pictures = db.query(Picture).filter(Picture.id.in_(new_collection.pictures)).all()
    db.commit()
    db.refresh(old_collection)
    return CollectionSchema.from_orm(old_collection)


@router.put("/add_pics", response_model=CollectionSchema)
async def add_pics_to_collection(
        collection: CollectionAndPicsSchema,
        db: Session = Depends(get_db),
):
    old_collection = db.query(Collection).filter(Collection.id == collection.id).first()
    if not old_collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Коллекция не найдена")
    for pic in db.query(Picture).filter(Picture.id.in_(collection.pictures)).all():
        if pic not in old_collection.pictures:
            old_collection.pictures.append(pic)
    db.commit()
    db.refresh(old_collection)
    return CollectionSchema.from_orm(old_collection)


@router.put("/delete_pics", response_model=CollectionSchema)
async def delete_pics_from_collection(
        collection: CollectionAndPicsSchema,
        db: Session = Depends(get_db),
):
    old_collection = db.query(Collection).filter(Collection.id == collection.id).first()
    if not old_collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Коллекция не найдена")
    for pic in db.query(Picture).filter(Picture.id.in_(collection.pictures)).all():
        if pic in old_collection.pictures:
            old_collection.pictures.remove(pic)
    db.commit()
    db.refresh(old_collection)
    return CollectionSchema.from_orm(old_collection)


@router.delete("/{collection_id}", response_model=CollectionSchema)
async def delete_collection(
        collection_id: int,
        db: Session = Depends(get_db),
):
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    res = CollectionSchema.from_orm(collection)
    db.delete(collection)
    db.commit()
    return res
