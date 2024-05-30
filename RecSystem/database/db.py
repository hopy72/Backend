from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base = declarative_base()
def init_db():
    # Импортируем модели здесь, чтобы избежать циклического импорта
    from database.pictures import Picture
    from database.users import User
    from database.collections import Collection
    from database.tags import Tag
    from database.col_to_pic_enrol import CollectionToPictureEnrollment
    from database.likes import Like
    from database.tag_to_pic_enrol import TagToPictureEnrollment
    Base.metadata.create_all(bind=engine)
