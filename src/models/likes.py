import sqlalchemy as sa
from dependencies.db import Base


class Like(Base):
    __tablename__ = "likes"

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), primary_key=True)
    picture_id = sa.Column(sa.Integer, sa.ForeignKey("pictures.id"), primary_key=True)

