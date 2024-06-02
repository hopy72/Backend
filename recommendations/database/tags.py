from sqlalchemy.orm import relationship

from database.db import Base
from database.tag_to_pic_enrol import TagToPictureEnrollment
import sqlalchemy as sa


class Tag(Base):
    __tablename__ = "tags"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment="Идентификатор тега", unique=True)
    name = sa.Column(sa.String, comment="Имя тега", unique=True)

    pictures = relationship(
        "Picture",
        secondary=TagToPictureEnrollment.__table__,
        back_populates="tags",
    )
