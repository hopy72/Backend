from sqlalchemy.orm import relationship

from database.db import Base
import sqlalchemy as sa


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment="Идентификатор пользователя", unique=True)
    username = sa.Column(sa.String, comment="Имя пользователя", unique=True)

    collections = relationship("Collection",
                               back_populates="author",
                               cascade="all, delete-orphan",
                               passive_deletes=True)
    liked_pictures = relationship(
        "Picture",
        secondary="likes",
        back_populates="users_liked",
    )
