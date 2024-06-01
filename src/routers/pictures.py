from pathlib import Path
from typing import List

from dependencies.db import get_db
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from schemas import PictureSchema, PictureUpdateSchema
from models.pictures import Picture
from models.users import User
from models.collections import Collection
from models.tags import Tag
from models.likes import Like
import aiofiles
import os


router = APIRouter(prefix="/pictures", tags=["pictures"])


@router.post("", response_model=PictureSchema)
async def create_picture(
        file: UploadFile,
        db: Session = Depends(get_db),
):
    new_picture_db = Picture(tags=[])
    db.add(new_picture_db)
    db.commit()
    db.refresh(new_picture_db)
    new_picture_db.path = f"picture{new_picture_db.id}.jpg"
    db.commit()
    db.refresh(new_picture_db)
    async with aiofiles.open(f"./pictures/{new_picture_db.path}", 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    return PictureSchema.from_orm(new_picture_db)


@router.get("/{path}")
async def get_picture_file(
        path: str,
):
    image_path = Path(f"./pictures/{path}")
    return FileResponse(image_path)


@router.get("/likes/{picture_id}", response_model=int)
async def get_picture_likes_number(
        picture_id: int,
        db: Session = Depends(get_db),
):
    res = db.query(Like).filter(Like.picture_id == picture_id).count()
    return res


@router.post("/pic_list", response_model=List[PictureSchema])
async def get_pictures_by_ids(
        ids: List[int],
        db: Session = Depends(get_db),
):
    pictures = db.query(Picture).filter(Picture.id.in_(ids)).all()
    return [PictureSchema.from_orm(pic) for pic in pictures]


@router.put("", response_model=PictureSchema)
async def update_picture(
        new_picture: PictureUpdateSchema,
        db: Session = Depends(get_db),
):
    old_picture = db.query(Picture).filter(Picture.id == new_picture.id).first()
    if not old_picture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Картинка не найдена")
    old_picture.tags = db.query(Tag).filter(Tag.id.in_(new_picture.tags)).all()
    db.commit()
    db.refresh(old_picture)
    return PictureSchema.from_orm(old_picture)


@router.delete("/{picture_id}", response_model=PictureSchema)
async def delete_picture(
        picture_id: int,
        db: Session = Depends(get_db),
):
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if not picture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Картинка не найдена")
    res = PictureSchema.from_orm(picture)
    db.delete(picture)
    db.commit()
    os.remove(f"./pictures/{picture.path}")
    return res
