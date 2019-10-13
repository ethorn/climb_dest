from flask import json, render_template, request
from sqlalchemy import and_, or_, true

from app import db
from app.main import bp
from app.main.forms import CurrencyForm
from app.main.load_destinations import get_joins, get_filter_and_order_array, convert_data_to_dict
from app.models import (Accomodation, Approach, Car, Cost, Destination, Months,
                        Routes, User)


@bp.route('/')
@bp.route('/index')
def index():
    if request.args:
        # Process GET data from url, into dict/json object format 
        url_filter_data = request.args.to_dict()
        converted_url_filter_data = convert_data_to_dict(url_filter_data)

        # Get filters, orders and joins array for query
        filters, order = get_filter_and_order_array(converted_url_filter_data)
        joins = get_joins()  # gets a list which joins the tables going to be queried

        # Query
        destinations = Destination.query.join(*joins).filter(*filters).order_by(order).all()

    else:
        destinations = Destination.query.all()

    countries_query = db.session.query(Destination.country.distinct()).all()
    countries = [value for value, in countries_query]

    currency_form = CurrencyForm()

    return render_template('index.html', title='Home', destinations=destinations, request=request,
                           currency_form=currency_form, user=User, countries=countries)



@bp.route('/_load_destinations', methods=['POST', 'GET'])
def load_destinations():  # Gets called from .load() call in filter.js from function loadDestinations
    # Process incoming data: Make stringified json into json object
    data_as_string = request.form.get('jsonDataAsString')
    json_filter_data = json.loads(data_as_string)  

    # Get filters, orders and joins array for query
    filters, order = get_filter_and_order_array(json_filter_data)
    joins = get_joins()  # gets a list which joins the tables going to be queried

    # Query
    destinations = Destination.query.join(*joins).filter(*filters).order_by(order).all()

    return render_template('loop_wrapper.html', destinations=destinations)


@bp.route('/<int:id>')
def single(id):
    d = Destination.query.get(id)
    currency_form = CurrencyForm()
    return render_template('destination_single_page.html',
                           title='Single Destination',
                           destination=d,
                           currency_form=currency_form)


@bp.route('/feedback')
def feedback():
    return render_template('feedback.html')


@bp.route('/vote')
def vote():
    return """Här kan man rösta på vilka destinationer som ska läggas till.
              Man kan lägga till en destination eller upvota.
              Bonus: Man kan också kommentera på varje destination."""
