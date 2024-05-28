import sqlalchemy as sa
import datetime
from database.db import Base


class CollectionToPictureEnrollment(Base):
    __tablename__ = "col_to_pic_enrol"

    collection_id = sa.Column(sa.Integer, sa.ForeignKey("collections.id"), primary_key=True)
    picture_id = sa.Column(sa.Integer, sa.ForeignKey("pictures.id"), primary_key=True)
    add_date = sa.Column(sa.DateTime, comment="Дата добавления в коллекцию", default=datetime.datetime.utcnow)

