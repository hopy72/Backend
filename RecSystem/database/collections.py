from sqlalchemy.orm import relationship

from database.db import Base
from database.col_to_pic_enrol import CollectionToPictureEnrollment
import sqlalchemy as sa


class Collection(Base):
    __tablename__ = "collections"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment="Идентификатор коллекции", unique=True)
    name = sa.Column(sa.String, comment="Название коллекции")
    author_id = sa.Column(sa.Integer,
                          sa.ForeignKey('users.id', ondelete="CASCADE", onupdate="CASCADE"),
                          comment="Идентификатор автора")

    author = relationship("User", back_populates="collections")
    pictures = relationship(
        "Picture",
        secondary=CollectionToPictureEnrollment.__table__,
        back_populates="collections",
    )
