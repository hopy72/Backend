from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost:5433/auth"

db_name = 'auth'
db_user = 'postgres'
db_pass = 'root'
db_host = 'authdb'
db_port = '5432'

# Connect to the database
db_string = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(db_user, db_pass, db_host, db_port, db_name)

engine = create_engine(db_string)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class UserInDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)


def get_user_by_email(db_session, email):
    return db_session.query(UserInDB).filter(UserInDB.email == email).first()


def add_user(db_session, email, hashed_password, access_token, refresh_token):
    new_user = UserInDB(
        email=email,
        hashed_password=hashed_password,
        access_token=access_token,
        refresh_token=refresh_token
    )
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    return new_user
