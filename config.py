import os
from dotenv import load_dotenv
load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADS_DEFAULT_DEST = 'app/static/uploads'
    UPLOADS_DEFAULT_URL = os.getenv('UPLOADS_DEFAULT_URL') or 'https://climbit.ericthorn.me/static/uploads/'
    UPLOADED_IMAGES_DEST = 'app/static/uploads/images'
    UPLOADED_IMAGES_URL = os.getenv('UPLOADED_IMAGES_URL') or 'https://climbit.ericthorn.me/static/uploads/images/'
    UPLOADS_PILLOW = os.path.join(basedir, 'app/static/uploads/images')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    ADMINS = ['eric.m.thorn@gmail.com']
