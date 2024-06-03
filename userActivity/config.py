db_name = 'backdb'
db_user = 'postgres'
db_pass = 'root'
db_host = 'backdb'
db_port = '5432'

# Connecto to the database
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg://{}:{}@{}:{}/{}'.format(db_user, db_pass, db_host, db_port, db_name)
# SQLALCHEMY_DATABASE_URI = "sqlite:///example.db"
SECRET_KEY = "secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
