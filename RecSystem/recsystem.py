from sqlalchemy import func
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase, Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime
from database.pictures import Picture
from database.users import User
from database.collections import Collection
from database.tags import Tag
from database.likes import Like
from database.db import get_db
import uvicorn
import random


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
    random_pictures = db.query(Picture).order_by(func.random()).limit(1000).all()

    # Собираем все теги из базы данных
    all_tags = []
    pictures_id = []
    for picture in random_pictures:
        all_tags.append(' '.join([tag.name for tag in picture.tags]))
        pictures_id.append(picture.id)
    # Создаем TF-IDF векторизатор и вычисляем TF-IDF для тегов
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(all_tags)

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


    # Возвращаем рекомендованные посты

    recommended_posts = [random_pictures[index].path for index in recommended_indices]

    db.close()
    return recommended_posts[:num_recommendations]


# Создание экземпляра FastAPI
app = FastAPI()

# Маршрут для добавления лайка


# Маршрут для получения рекомендаций
# по дате добавления рекомендовать
@app.post("/recommendations/")
async def get_recommendations_endpoint(user_id: int, num_recommendations: int, db: Session = Depends(get_db)):
    recommendations = get_recommendations(user_id, num_recommendations, db)
    if not recommendations:
        raise HTTPException(status_code=404, detail="Recommendations not found")
    return {"recommendations": recommendations}


# uvicorn.run(app)
