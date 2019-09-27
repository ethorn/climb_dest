# CORE FUNCTIONALITY BLUEPRINT
from flask import Blueprint

bp = Blueprint('main', __name__)

from app.errors import routes

# Refactor routes and other functions
# change url_for, intex -> main.index etc.
# add blueprint to __init__.py

# ## Alle routes, forms og funksjoner skal inn i ulike blueprints
# Poeng med blueprints: It encapsulates a feature, separation of concerns, easy to use in other projects
# Andre blueprints jeg kan lage:
# * Image resize/compression ??
# * Add destination
# * load destinations / filtering
# * Currency
# *
