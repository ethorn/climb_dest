from flask import Blueprint

bp = Blueprint('currency', __name__)

from app.currency import routes