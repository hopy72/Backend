from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Предположим, что у нас есть некоторые посты с их тегами
posts = {
    'post1': 'python data science machine learning',
    'post2': 'python programming tutorial',
    'post3': 'exit process posts school',
    'post4': 'beer bear mouse school',
    'post5': 'royal modern school',
    'post6': 'beer keyboard',
    'post7': 'machine learning course'
}

# Пример лайкнутых постов и постов в коллекции пользователя
liked_posts = ['post1']
collection_posts = []

# Соединяем теги постов в единый список для создания корпуса
corpus = [tags for post, tags in posts.items()]

# Создаем TF-IDF векторизатор и вычисляем TF-IDF для тегов
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)

# Функция для получения рекомендаций постов
# Функция для получения рекомендаций постов
def get_recommendations(liked_posts, collection_posts, num_recommendations=3):
    # Собираем все теги, которые пользователь лайкнул или добавил в коллекцию
    user_tags = []
    for post in liked_posts + collection_posts:
        user_tags.append(posts[post])

    # Преобразуем теги пользователя в TF-IDF представление
    user_tfidf = tfidf_vectorizer.transform(user_tags)

    # Вычисляем косинусную схожесть между тегами пользователя и всеми постами
    similarities = cosine_similarity(user_tfidf, tfidf_matrix)

    # Получаем индексы постов, отсортированных по убыванию схожести
    similar_indices = similarities.argsort(axis=1)[:, ::-1]

    # Получаем индексы рекомендуемых постов (исключаем посты, которые пользователь уже лайкнул или добавил в коллекцию)
    recommended_indices = []
    for indices in similar_indices:
        for index in indices:
            post_key = list(posts.keys())[index]
            if post_key not in liked_posts and post_key not in collection_posts:
                recommended_indices.append(index)
              #  break

    # Возвращаем рекомендованные посты
    recommended_posts = [list(posts.keys())[index] for index in recommended_indices[:num_recommendations]]

    return recommended_posts

# Получаем рекомендации для пользователя
recommendations = get_recommendations(liked_posts, collection_posts)
print("Рекомендованные посты:", recommendations)