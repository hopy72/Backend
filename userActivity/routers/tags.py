from typing import List

from dependencies.db import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import TagInSchema, TagSchema
from models.pictures import Picture
from models.users import User
from models.collections import Collection
from models.tags import Tag
from models.likes import Like


router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("", response_model=TagSchema)
async def create_tag(
        new_tag: TagInSchema,
        db: Session = Depends(get_db),
):
    tag = db.query(Tag).filter(Tag.name == new_tag.name).first()
    if tag:
        raise HTTPException(status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                            detail="Тэг с таким именем уже существует")
    new_tag_db = Tag(
        name=new_tag.name
    )
    db.add(new_tag_db)
    db.commit()
    db.refresh(new_tag_db)
    return TagSchema.from_orm(new_tag_db)


@router.get("", response_model=List[TagSchema])
async def get_all_tags(
        db: Session = Depends(get_db),
):
    tags = db.query(Tag).all()
    return [TagSchema.from_orm(tag) for tag in tags]


@router.delete("/{tag_id}", response_model=TagSchema)
async def delete_tag(
        tag_id: int,
        db: Session = Depends(get_db),
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тэг не найден")
    res = TagSchema.from_orm(tag)
    db.delete(tag)
    db.commit()
    return res
