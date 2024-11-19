import os
class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///store.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False    
    JWT_SECRET_KEY = "Bootcamp"
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    CELERY_BROKER_URL = "redis://localhost:6379/1" # DB 1
    CELERY_RESULT_BACKEND = "redis://localhost:6379/2" # DB 2
    MAIL_SERVER = "localhost"
    MAIL_PORT = 1025
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = "redis://localhost:6379/0"