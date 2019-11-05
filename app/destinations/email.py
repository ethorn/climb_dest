from flask import render_template, current_app
from app.email import send_email


def send_suggest_update_email(subject, sender_email, destination_title, message):
    send_email(subject=subject,
               sender=sender_email,
               recipients=current_app.config['ADMINS'],
               text_body=render_template('email/suggest_update.txt',
                                         destination_title=destination_title, sender_email=sender_email, message=message),
               html_body=render_template('email/suggest_update.html',
                                         destination_title=destination_title, sender_email=sender_email, message=message))
