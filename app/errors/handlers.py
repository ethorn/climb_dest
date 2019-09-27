from flask import render_template
from app import db
from app.errors import bp
from app.forms import CurrencyForm


@bp.app_errorhandler(404)
def not_found_error(error):
    currency_form = CurrencyForm()
    return render_template('errors/404.html', currency_form=currency_form), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    currency_form = CurrencyForm()
    return render_template('errors/500.html', currency_form=currency_form), 500
