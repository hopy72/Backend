# Memerest - лента с мемами, аналог Pinterest
## Участники проекта
- [Поволяев Андрей](https://github.com/hopy72) 5130904/10104
- [Свиридов Артём](https://github.com/TemSV) 5130904/10104
- [Ермаков Никита](https://github.com/makniker) 5130904/10104
- [Кузьмин Владислав](https://github.com/ValamintH) 5130904/10104

## Задачи проекта
Проектирование и разработка мобильного приложения под Android в котором можно смотреть мемы, делиться ими с друзьями, лайкать, добавлять в коллекции, а также загружать свои собственные мемы, таким образом, заслужив репутацию человека с чувством юмора.

## Требования
- Просмотр контента
  > Пользователь должен иметь возможность листать бесконечную ленту с мемами, а также иметь бесперебойный доступ к "Ленте недели"
- Авторизация
  > Пользователь имеет возможность создать аккаунт и авторизоваться в приложении. Сессия клиента периодически протухает, пользователю приходится авторизовываться заново.
- Загрузка контента
  > Пользователь имеет возможность загрузить картинку, присвоить ей теги из числа предложенных разработчиками. Есть гарантия, что картинка появится в ленте других пользователей.
- Взаимодействие с картинками
  > Пользователь должен иметь возможность поставить "лайк" понравившейся картике, а также добавить её в коллекцию.
- Рекомендации и Лента недели
  > В бесконечной ленте каждого пользователя должны отображаться картинки по индексу заинтересованности пользователя. Каждую неделю генерируется лента с подборкой самых популярных картинок, она доступна пользователю всю неделю и затем обновляется.
- Доступ к приложения без интернет-соединения
  > Пользователь должен иметь доступ просматривать картинки в своих коллекциях даже в оффлайн-режиме.
## Архитектура проекта
### System Context Diagram
![](https://github.com/Memerest/Backend/blob/main/system_context_diagram.png)
### Container Diagram
![](https://github.com/Memerest/Backend/blob/main/container_diagram.jpg)
### Database scheme
![](https://github.com/Memerest/Backend/blob/main/database_scheme.png)

## Технологический стек
- Frontend:
    - Kotlin
    - Retrofit
    - Coil
    - Android Jetpack
    - Jetpack Compose
- Backend:
    - Python
    - FastAPI
    - SQLalchemy
    - alembic
    - pydantic
    - Nginx
- Tools for data storage, image storage and deployment application
    - PostgreSQL 15
    - Yandex S3 Object Storage
    - Docker
- VCS
    - GitHub
- Testing and documentation tools
    - Postman
    - SwaggerAPI
    - pytest
    - TestClient

## Начало работы
### Требования
- Nginx
- Python 3.8+
- Docker
### Установка
1. Клонируйте репозиторий
```
git clone https://github.com/Memerest/Backend.git
cd Backend
git checkout test_nginx
```
2.  Убедитесь, что Docker установлен на вашем компьютере
```
docker --version
```
3. Перейдите в директорию системы рекомендаций, создайте там файл **token.py** и поместите туда ваш ключ доступа и секретный ключ S3 Object Storage
```
cd ./RecSystem
nano token.py

def aws_access_key():
    aws_access_key_id = '<your_aws_access_key_id>'
    return aws_access_key_id
def aws_secret_access():
    aws_secret_access_key = '<your_aws_secret_access_key>'
    return aws_secret_access_key
```
### Запуск
1. Собираем наш проект
```
docker-compose build
```
2. И запускаем
```
docker-compose up
```


