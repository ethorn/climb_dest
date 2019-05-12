from flask import Flask  # Fordi jeg har installert flask i den virtuelle environmenten
from config import Config  # Kan importa från "en folder upp" eftersom climb_dest.py importar hela appen till den filen
from flask_sqlalchemy import SQLAlchemy  # från paketet importeras klassen SQLAlchemy
from flask_migrate import Migrate  # från paketet importeras klassen SQLAlchemy
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os
from flask_mail import Mail

app = Flask(__name__)  # skapar en app objekt instans från klassen Flask
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'  # To use the login-required feature to show certain views only if logged in. 'login' is the function/endpoint for the login view
mail = Mail(app)


# Configure the image uploading via Flask-Uploads
images = UploadSet('images', IMAGES)
configure_uploads(app, images)


if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='climb_dest Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/climbing_destinations.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Climbit startup')


from app import routes, models, errors
