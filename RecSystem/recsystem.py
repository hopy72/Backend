from sqlalchemy import select, func, desc, exists, and_, Column, String, Integer, DateTime, Table, MetaData
from sqlalchemy.future import select
from typing import List, Optional
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import FastAPI, HTTPException, Depends
from database.pictures import Picture
from database.users import User
from database.collections import Collection
from database.tags import Tag
from database.likes import Like
from database.col_to_pic_enrol import CollectionToPictureEnrollment
from database.tag_to_pic_enrol import TagToPictureEnrollment
from database.db import get_db
from database.db import init_db
from pydantic import BaseModel
import boto3
import uvicorn
import random
import datetime
import sqlalchemy as sa


# Функция для получения рекомендованных постов
def get_recommendations(user_id, num_recommendations, db):
    

    # Получаем теги лайкнутых и добавленных в коллекцию картинок пользователя
    liked_picture_tags = []
    collection_picture_tags = []

    liked_pictures = db.query(Like).filter_by(user_id=user_id).all()
    collection_pictures = db.query(Collection).filter_by(author_id=user_id).all()

    liked_pictures_id = []

    for like in liked_pictures:
        picture = db.query(Picture).filter_by(id=like.picture_id).first()
        liked_picture_tags.append(' '.join([tag.name for tag in picture.tags]))
        liked_pictures_id.append(like.picture_id)

    collection_pictures_id = []

  #  for collection in collection_pictures:
    #     picture = db.query(Picture).filter_by(id=collection.pictures.id).first()
  #      collection_picture_tags.append(' '.join([tag.name for tag in picture.tags]))
   #     collection_pictures_id.append(collection.picture_id)

    # Собираем все теги пользователя в один список
    user_tags = liked_picture_tags + collection_picture_tags
    # Получаем случайные 1000 картинок
    random_pictures = db.query(Picture).order_by(func.random()).limit(100).all()

    # Собираем все теги из базы данных
    all_tags = []
    pictures_id = []
    for picture in random_pictures:
        all_tags.append(' '.join([tag.name for tag in picture.tags]))
        pictures_id.append(picture.id)
    # Создаем TF-IDF векторизатор и вычисляем TF-IDF для тегов
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(all_tags)

    if not user_tags:
        return random_pictures[:num_recommendations]

    # Преобразуем теги пользователя в TF-IDF представление
    user_tfidf = tfidf_vectorizer.transform(user_tags)

    # Вычисляем косинусную схожесть между тегами пользователя и всеми постами
    similarities = cosine_similarity(user_tfidf, tfidf_matrix)

    # Получаем индексы постов, отсортированных по убыванию схожести
    similar_indices = similarities.argsort(axis=1)[:, ::-1]

    # Получаем индексы рекомендуемых постов (исключаем посты, которые пользователь уже лайкнул или добавил в коллекцию)
    recommended_indices = []
    fix_list = []
    for indices in similar_indices:
        for index in indices:
            key = pictures_id[index]
            if key not in liked_pictures_id and key not in collection_pictures_id and key not in fix_list:
                recommended_indices.append(index)
                fix_list = [random_pictures[index].id for index in recommended_indices]


    recommended_posts = [random_pictures[index] for index in recommended_indices]
    returned_random_pictures = [pic for pic in random_pictures if pic not in recommended_posts and pic not in liked_pictures]
    num_recommendations_half = num_recommendations // 2
    returned_posts = recommended_posts[:num_recommendations_half] + returned_random_pictures[:(num_recommendations - num_recommendations_half)]
    db.close()
    return returned_posts


# Создание экземпляра FastAPI
app = FastAPI()
init_db()
class PictureResponse(BaseModel):
    id: int
    path: str
    is_liked_by_user: bool
    tags: List[int]

    class Config:
        orm_mode = True

# Маршрут для получения рекомендаций
# по дате добавления рекомендовать
@app.post("/recommendations/", response_model=List[PictureResponse])
async def get_recommendations_endpoint(user_id: int, num_recommendations: int, db: Session = Depends(get_db)):
    recommended_posts = get_recommendations(user_id, num_recommendations, db)
    picture_ids = [pic.id for pic in recommended_posts]
    tags = db.query(Tag.id, TagToPictureEnrollment.picture_id).join(TagToPictureEnrollment, Tag.id == TagToPictureEnrollment.tag_id)\
            .filter(TagToPictureEnrollment.picture_id.in_(picture_ids)).all()
    
    tags_dict = {}
    for tag_id, picture_id in tags:
        if picture_id not in tags_dict:
            tags_dict[picture_id] = []
        tags_dict[picture_id].append(tag_id)

    response = []
    for picture in recommended_posts:
        response.append(PictureResponse(
            id=picture.id,
            path=picture.path,
            is_liked_by_user=False,
            tags=tags_dict.get(picture.id, [])
        ))
    
    if not recommended_posts:
        raise HTTPException(status_code=404, detail="Recommendations not found")
    return response



@app.get("/top_pictures", response_model=List[PictureResponse])
def get_top_pictures(user_id: int, db: Session = Depends(get_db)):
    one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(weeks=1)
    
    # Подзапрос для проверки, лайкнул ли пользователь картинку
    is_liked_subquery = db.query(Like.picture_id)\
                          .filter(Like.user_id == user_id)\
                          .subquery()
    
    # Запрос для получения топ 50 картинок с наибольшим числом лайков за последнюю неделю
    top_pictures = db.query(
        Picture.id,
        Picture.path,
        func.count(Like.picture_id).label("like_count"),
        (Picture.id.in_(is_liked_subquery)).label("is_liked_by_user")
    ).join(Like, Picture.id == Like.picture_id)\
     .filter(Like.like_date >= one_week_ago)\
     .group_by(Picture.id)\
     .order_by(desc("like_count"))\
     .limit(50)\
     .all()
    
    # Получение тегов для каждой картинки
    picture_ids = [pic.id for pic in top_pictures]
    tags = db.query(Tag.id, TagToPictureEnrollment.picture_id).join(TagToPictureEnrollment, Tag.id == TagToPictureEnrollment.tag_id)\
            .filter(TagToPictureEnrollment.picture_id.in_(picture_ids)).all()
    
    tags_dict = {}
    for tag_id, picture_id in tags:
        if picture_id not in tags_dict:
            tags_dict[picture_id] = []
        tags_dict[picture_id].append(tag_id)

    # Формирование списка картинок для ответа
    response = []
    for picture in top_pictures:
        response.append(PictureResponse(
            id=picture.id,
            path=picture.path,
            is_liked_by_user=picture.is_liked_by_user,
            tags=tags_dict.get(picture.id, [])
        ))
    
    return response

s3_client = boto3.client(
    's3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id='YCAJEwiniJk6C_9N9bJqI_v-c',
    aws_secret_access_key='YCO8KK0Bn5Sf1_blUoVJh9pesRi9O2rDHzbziphU'
)

bucket_name = 'memerest-pictures'

def get_s3_object_keys(bucket_name):
    # Получение списка всех объектов в указанном бакете
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    keys = [content['Key'] for content in response.get('Contents', [])]
    return keys

def clear_database(db: Session):
    # Очистка всех таблиц
    db.query(Like).delete()
    db.query(TagToPictureEnrollment).delete()
    db.query(CollectionToPictureEnrollment).delete()
    db.query(Collection).delete()
    db.query(Picture).delete()
    db.query(Tag).delete()
    db.query(User).delete()
    db.commit()

def populate_test_data(db: Session):
    clear_database(db)
    # Создание пользователей
    users = []
    for i in range(1, 15):
        user = User(username=f"user{i}")
        users.append(user)
    db.add_all(users)
    db.commit()

    # Создание тэгов
    tags = []
    for i in range(1, 51):
        tag = Tag(name=f"tag{i}")
        tags.append(tag)
    db.add_all(tags)
    db.commit()

    # Получение списка объектов из Yandex S3
    object_keys = get_s3_object_keys(bucket_name)

    # Создание картинок
    pictures = []
    for key in random.sample(object_keys, 1000):
        picture = Picture(path=f"https://storage.yandexcloud.net/{bucket_name}/{key}")
        pictures.append(picture)
    db.add_all(pictures)
    db.commit()

    # Добавление тэгов к картинкам
    for picture in pictures:
        picture_tags = random.sample(tags, 4)
        for tag in picture_tags:
            tag_to_pic = TagToPictureEnrollment(tag_id=tag.id, picture_id=picture.id)
            db.add(tag_to_pic)
    db.commit()

    # Создание лайков
    likes = set()
    for _ in range(300):
        while True:
            user = random.choice(users)
            picture = random.choice(pictures)
            if (user.id, picture.id) not in likes:
                likes.add((user.id, picture.id))
                like = Like(user_id=user.id, picture_id=picture.id, like_date=datetime.datetime.utcnow())
                db.add(like)
                break
    db.commit()

    # Создание коллекций и добавление в них картинок
    collection1 = Collection(name="Collection1", author_id=users[0].id)
    collection2 = Collection(name="Collection2", author_id=users[1].id)
    db.add_all([collection1, collection2])
    db.commit()

    # Добавление картинок в коллекции
    for collection in [collection1, collection2]:
        collection_pictures = random.sample(pictures, 2)
        for picture in collection_pictures:
            col_to_pic = CollectionToPictureEnrollment(collection_id=collection.id, picture_id=picture.id, add_date=datetime.datetime.utcnow())
            db.add(col_to_pic)
    db.commit()

# Функция для вызова заполнения данных
@app.post("/populate_test_data")
def populate_data(db: Session = Depends(get_db)):
    populate_test_data(db)
    return {"message": "Test data populated successfully"}


