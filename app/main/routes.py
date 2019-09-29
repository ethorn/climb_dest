from flask import json, render_template, request
from sqlalchemy import and_, or_, true

from app.main import bp
from app.main.forms import CurrencyForm
from app.main.load_destinations import get_filter_and_order_array
from app.models import (Accomodation, Approach, Car, Cost, Destination, Months,
                        Routes, User)


@bp.route('/')
@bp.route('/index')
def index():

    # Gjør en general purpose funksjon for både index og _load_destinations
    if request.args:
        url_filter_data = request.args.to_dict()

        if request.args.getlist('accomodation[]'):
            accomodations = request.args.getlist('accomodation[]')
            url_filter_data['accomodation'] = accomodations
            url_filter_data.pop('accomodation[]', None)

        if request.args.getlist('car[]'):
            car = request.args.getlist('car[]')
            url_filter_data['car'] = car
            url_filter_data.pop('car[]', None)

        if request.args.getlist('secondary_discipline[]'):
            secondary_discipline = request.args.getlist('secondary_discipline[]')
            url_filter_data['secondary_discipline'] = secondary_discipline
            url_filter_data.pop('secondary_discipline[]', None)

        if request.args.getlist('months[]'):
            months = request.args.getlist('months[]')
            url_filter_data['months'] = months
            url_filter_data.pop('months[]', None)

        print('GET', url_filter_data)

        # Get filters and orders array for query
        filters, order = get_filter_and_order_array(url_filter_data)

        # joins
        joins = []
        joins.append(Cost)
        joins.append(Routes)
        joins.append(Accomodation)
        joins.append(Months)
        joins.append(Car)
        ######

        # Query
        if filters:
            destinations = Destination.query.join(*joins).filter(*filters).order_by(order).all()
        else:
            destinations = Destination.query.join(*joins).order_by(order).all()
    else:
        destinations = Destination.query.all()

    currency_form = CurrencyForm()

    return render_template('index.html', title='Home', destinations=destinations, request=request,
                           currency_form=currency_form, user=User)


# Gets called from .load() call in filter.js from function loadDestinations
@bp.route('/_load_destinations', methods=['POST', 'GET'])
def load_destinations():

    # Process incoming data: Make stringified json into json object
    data_as_string = request.form.get('jsonDataAsString')
    json_filter_data = json.loads(data_as_string)  # OK

    print('json', json_filter_data)

    # Get filters and orders array for query
    filters, order = get_filter_and_order_array(json_filter_data)

    # Joins: Makes it possible to query filters on several tables at the same time
    # -- All tables that can be filtered with the filter options should be here
    joins = []
    joins.append(Cost)
    joins.append(Routes)
    joins.append(Accomodation)
    joins.append(Months)
    joins.append(Approach)
    joins.append(Car)

    # Query
    if filters:
        destinations = Destination.query.join(*joins).filter(*filters).order_by(order).all()
    else:
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
