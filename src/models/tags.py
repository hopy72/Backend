from sqlalchemy.orm import relationship

from dependencies.db import Base
from models.tag_to_pic_enrol import TagToPictureEnrollment
import sqlalchemy as sa


class Tag(Base):
    __tablename__ = "tags"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment="Идентификатор тега", unique=True)
    name = sa.Column(sa.String, comment="Имя тега", unique=True)

    pictures = relationship(
        "TagToPictureEnrollment",
        secondary=TagToPictureEnrollment.__table__,
        back_populates="tags",
    )
