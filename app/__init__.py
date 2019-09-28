from flask import Flask 
from config import Config
from flask_sqlalchemy import SQLAlchemy  
from flask_migrate import Migrate 
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os
from flask_mail import Mail
import redis
from rq import Queue

app = Flask(__name__)  # skapar en app objekt instans från klassen Flask
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'auth.login'  # To use the login-required feature to show certain views only if logged in. 'login' is the function/endpoint for the login view
mail = Mail(app)
# Setup Flask-User and specify the User data-model

# Configure the image uploading via Flask-Uploads, redis, rq
images = UploadSet('images', ('jpeg', 'jpg'))
configure_uploads(app, images)
patch_request_class(app, size=33554432)
r = redis.Redis()
q = Queue(connection=r)

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
    file_handler = RotatingFileHandler('logs/climb_dest.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Climbit startup')


# Blueprints

from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)


from app.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')


from app.user import bp as user_bp
app.register_blueprint(user_bp)


from app.destinations import bp as destinations_bp
app.register_blueprint(destinations_bp)


from app.currency import bp as currency_bp
app.register_blueprint(currency_bp)


from app.main import bp as main_bp
app.register_blueprint(main_bp)

# ##


from app import models, tasks
