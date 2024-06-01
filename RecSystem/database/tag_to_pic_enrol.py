import sqlalchemy as sa
from database.db import Base


class TagToPictureEnrollment(Base):
    __tablename__ = "tag_to_pic_enrol"

    tag_id = sa.Column(sa.Integer, sa.ForeignKey("tags.id"), primary_key=True)
    picture_id = sa.Column(sa.Integer, sa.ForeignKey("pictures.id"), primary_key=True)

