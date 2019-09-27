from flask_mail import Message
from app import mail
from app import app
from threading import Thread


def send_async_email(app, msg):
    # Flask-mail needs the app context in order to work, because it has settings in app.config
    # the context is normally passed automatically, but when threading it needs to be passed manually
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()
