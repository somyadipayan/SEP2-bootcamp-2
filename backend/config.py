import os
class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///store.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False    
    JWT_SECRET_KEY = "Bootcamp"
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")