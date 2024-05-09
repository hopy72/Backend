from sqlalchemy.orm import relationship

from dependencies.db import Base
from models.likes import Like
from models.col_to_pic_enrol import CollectionToPictureEnrollment
from models.tag_to_pic_enrol import TagToPictureEnrollment
import sqlalchemy as sa


class Picture(Base):
    __tablename__ = "pictures"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment="Идентификатор картинки", unique=True)
    path = sa.Column(sa.String, comment="Путь к картинке в хранилище")

    users_liked = relationship(
        "User",
        secondary=Like.__table__,
        back_populates="liked_pictures",
    )
    collections = relationship(
        "Collection",
        secondary=CollectionToPictureEnrollment.__table__,
        back_populates="pictures",
    )
    tags = relationship(
        "Tag",
        secondary=TagToPictureEnrollment.__table__,
        back_populates="pictures",
    )
