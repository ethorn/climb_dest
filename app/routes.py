import requests
from flask import (json, jsonify, make_response,
                   render_template, request)
from sqlalchemy import and_, or_, true  # , false

from app import app
from app.forms import CurrencyForm
from app.models import (Accomodation, Car, Cost,
                        Destination, Months, Routes, User)


# Gets called from .load() call in loadDestinations
@app.route('/_load_destinations', methods=['POST', 'GET'])
def load_destinations():

    # ---------- Ny funksjon -----
    # - Process incoming data: Make stringified json into json object
    data_as_string = request.form.get('jsonDataAsString')
    data = json.loads(data_as_string)

    # sort_by (Cost/Time added/routes in 4/routes in 5/...)
    sort_by = data['sort_by']
    if sort_by == "cost":
        order_parameter = Cost.avg_weekly_cost
    elif sort_by == "time":
        order_parameter = Destination.timestamp
    elif sort_by == "total_routes":
        order_parameter = Routes.total_routes
    elif sort_by == "total_sport":
        order_parameter = Routes.total_sport
    elif sort_by == "total_trad":
        order_parameter = Routes.total_trad
    elif sort_by == "total_boulders":
        order_parameter = Routes.total_boulders
    elif sort_by == "easy_routes":
        order_parameter = Routes.easy_routes
    elif sort_by == "intermediate_routes":
        order_parameter = Routes.intermediate_routes
    elif sort_by == "hard_routes":
        order_parameter = Routes.hard_routes
    elif sort_by == "very_hard_routes":
        order_parameter = Routes.very_hard_routes
    else:
        order_parameter = Destination.timestamp  # Default order

    # order (DESC/ASC)
    order = data['order']

    if order == "ASC":
        order_p_final = order_parameter.asc()
    elif order == "DESC":
        order_p_final = order_parameter.desc()

    # All Filters together container
    filters = []

    # accomodation (hvis selected, så må destinasjonen ha det.)
    if data.get('accomodation'):
        accomodation_filters = []

        accomodations = data['accomodation']

        for a in accomodations:
            accomodation_filters.append(getattr(Accomodation, a) == true())

        filters.append(and_(*accomodation_filters))

    # car
    if data.get('car'):
        car_filters = []
        cars = data['car']

        for c in cars:
            car_filters.append(getattr(Car, c) == true())

        filters.append(or_(*car_filters))

    # cost
    if data.get('cost'):
        max_cost = data['cost']

        filters.append(Cost.avg_weekly_cost <= max_cost)

    # main_discipline & secondary_discipline (hvis selected, så må destinasjonen ha det.)
    discipline_filters = []

    if data.get('main_discipline'):
        m_d = data['main_discipline']
        discipline_filters.append(Routes.main_discipline == m_d)

    if data.get('secondary_discipline'):
        secondary_disciplines = data['secondary_discipline']

        for d in secondary_disciplines:
            discipline_filters.append(getattr(Routes, d) == true())

    if discipline_filters:
        filters.append(and_(*discipline_filters))

    # months
    if data.get('months'):
        months_filters = []

        months_from_ajax = data['months']
        for m in months_from_ajax:
            months_filters.append(getattr(Months, m) == true())

        filters.append(or_(*months_filters))
    # ----------

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
        destinations = Destination.query.join(*joins).filter(*filters).order_by(order_p_final).all()
    else:
        destinations = Destination.query.join(*joins).filter(*filters).order_by(order_p_final).all()
    ######

    # Return
    return render_template('loop_wrapper.html', destinations=destinations)
    ######


@app.route('/')
@app.route('/index')
def index():

    # Må sjekke hvis hver parameter finnes
    # gøra dette till en blueprint?

    if request.args:
        if request.args.get('sort_by'):
            sort_by = request.args.get('sort_by')
            if sort_by == "cost":
                order_parameter = Cost.avg_weekly_cost
            elif sort_by == "time":
                order_parameter = Destination.timestamp
            elif sort_by == "total_routes":
                order_parameter = Routes.total_routes
            elif sort_by == "total_sport":
                order_parameter = Routes.total_sport
            elif sort_by == "total_trad":
                order_parameter = Routes.total_trad
            elif sort_by == "total_boulders":
                order_parameter = Routes.total_boulders
            elif sort_by == "easy_routes":
                order_parameter = Routes.easy_routes
            elif sort_by == "intermediate_routes":
                order_parameter = Routes.intermediate_routes
            elif sort_by == "hard_routes":
                order_parameter = Routes.hard_routes
            elif sort_by == "very_hard_routes":
                order_parameter = Routes.very_hard_routes
            else:
                order_parameter = Destination.timestamp  # Default order
        else:
            order_parameter = Destination.timestamp

        # order (DESC/ASC)
        if request.args.get('order'):
            order = request.args.get('order')

            if order == "ASC":
                order_p_final = order_parameter.asc()
            elif order == "DESC":
                order_p_final = order_parameter.desc()
            else:
                order_p_final = order_parameter.asc()
        else:
            order_p_final = order_parameter.desc()

        # All Filters together container
        filters = []

        # accomodation (hvis selected, så må destinasjonen ha det.)
        if request.args.getlist('accomodation[]'):
            accomodation_filters = []
            accomodations = request.args.getlist('accomodation[]')

            for a in accomodations:
                if hasattr(Accomodation, a):
                        accomodation_filters.append(getattr(Accomodation, a) == true())

            if accomodation_filters:
                filters.append(and_(*accomodation_filters))

        # car
        if request.args.getlist('car[]'):
            car_filters = []
            cars = request.args.getlist('car[]')

            for c in cars:
                if hasattr(Car, c):
                    car_filters.append(getattr(Car, c) == true())

            if car_filters:
                filters.append(or_(*car_filters))

        # cost
        if request.args.get('cost'):
            max_cost = request.args.get('cost')

            try:
                max_cost = int(max_cost)
            except ValueError:
                max_cost = 9999999999999

            filters.append(Cost.avg_weekly_cost <= max_cost)

        # main_discipline & secondary_discipline (hvis selected, så må destinasjonen ha det.)

        discipline_filters = []

        if request.args.get('main_discipline'):
            m_d = request.args.get('main_discipline')

            if m_d in ('sport', 'traditional', 'bouldering'):
                discipline_filters.append(Routes.main_discipline == m_d)

        if request.args.getlist('secondary_discipline[]'):
            secondary_disciplines = request.args.getlist('secondary_discipline[]')

            for d in secondary_disciplines:
                if hasattr(Routes, d):
                    discipline_filters.append(getattr(Routes, d) == true())

        if discipline_filters:
            filters.append(and_(*discipline_filters))

        # months
        if request.args.getlist('months[]'):
            months_filters = []
            months_from_ajax = request.args.getlist('months[]')

            for m in months_from_ajax:
                if hasattr(Months, m):
                    months_filters.append(getattr(Months, m) == true())

            if months_filters:
                filters.append(or_(*months_filters))
        # ----------

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
            destinations = Destination.query.join(*joins).filter(*filters).order_by(order_p_final).all()
        else:
            destinations = Destination.query.join(*joins).order_by(order_p_final).all()
    else:
        destinations = Destination.query.all()

    currency_form = CurrencyForm()

    return render_template('index.html', title='Home', destinations=destinations, request=request,
                           currency_form=currency_form, user=User)


@app.route('/<int:id>')
def single(id):
    d = Destination.query.get(id)
    currency_form = CurrencyForm()
    return render_template('destination_single_page.html',
                           title='Single Destination',
                           destination=d,
                           currency_form=currency_form)

