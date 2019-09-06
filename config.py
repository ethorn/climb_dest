import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADS_DEFAULT_DEST = 'app/static/uploads'
    UPLOADS_DEFAULT_URL = os.environ.get('UPLOADS_DEFAULT_URL') or 'https://climbit.ericthorn.me/static/uploads/'
    UPLOADED_IMAGES_DEST = 'app/static/uploads/images'
    UPLOADED_IMAGES_URL = os.environ.get('UPLOADED_IMAGES_URL') or 'https://climbit.ericthorn.me/static/uploads/images/'
    UPLOADS_PILLOW = os.path.join(basedir, 'app/static/uploads/images')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['eric.m.thorn@gmail.com']
