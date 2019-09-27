from flask import Blueprint

bp = Blueprint('destinations', __name__)

from app.destinations import routes