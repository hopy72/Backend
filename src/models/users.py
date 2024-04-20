from sqlalchemy.orm import relationship

from dependencies.db import Base
from models.likes import Like
import sqlalchemy as sa


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment="Идентификатор пользователя", unique=True)
    username = sa.Column(sa.String, comment="Имя пользователя")
    # hashed_password = sa.Column(sa.String, comment="Зашифрованный пароль")

    collections = relationship("Collection",
                               back_populates="author",
                               cascade="all, delete-orphan",
                               passive_deletes=True)
    liked_pictures = relationship(
        "Like",
        secondary=Like.__table__,
        back_populates="users_liked",
    )
