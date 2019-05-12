from flask import render_template
from app import app, db
from app.forms import CurrencyForm


@app.errorhandler(404)
def not_found_error(error):
    currency_form = CurrencyForm()
    return render_template('404.html', currency_form=currency_form), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    currency_form = CurrencyForm()
    return render_template('500.html', currency_form=currency_form), 500
