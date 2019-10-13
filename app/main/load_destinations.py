from app.models import (Accomodation, Car, Cost, Destination, Months, Routes)
from sqlalchemy import and_, or_, true
from flask import request


def convert_data_to_dict(url_filter_data):
    if request.args.getlist('continents[]'):
        continents = request.args.getlist('continents[]')
        url_filter_data['continents'] = continents
        url_filter_data.pop('continents[]', None)

    if request.args.getlist('countries[]'):
        countries = request.args.getlist('countries[]')
        url_filter_data['countries'] = countries
        url_filter_data.pop('countries[]', None)
        
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

    return url_filter_data


def get_joins():
    joins = []
    joins.append(Cost)
    joins.append(Routes)
    joins.append(Accomodation)
    joins.append(Months)
    joins.append(Car)
    return joins


def get_filter_and_order_array(data):

    # sort_by (Cost/Time added/routes in 4/routes in 5/...)
    if 'sort_by' in data:
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
    if 'order' in data:
        order = data['order']
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

    # continents
    if 'continents' in data:
        continents_filters = []
        continents = data['continents']
        for continent in continents:
            continents_filters.append(Destination.continent == continent)
        if continents_filters:
            filters.append(or_(*continents_filters))

    # coutries
    if 'countries' in data:
        countries_filters = []
        countries = data['countries']
        for country in countries:
            countries_filters.append(Destination.country == country)
        if countries_filters:
            filters.append(or_(*countries_filters))

    # accomodation (hvis selected, så må destinasjonen ha det.)
    if 'accomodation' in data:
        accomodation_filters = []
        accomodations = data['accomodation']
        for a in accomodations:
            if hasattr(Accomodation, a):
                accomodation_filters.append(getattr(Accomodation, a) == true())
        if accomodation_filters:
                filters.append(and_(*accomodation_filters))

    # car
    if 'car' in data:
        car_filters = []
        cars = data['car']
        for c in cars:
            if hasattr(Car, c):
                car_filters.append(getattr(Car, c) == true())
        if car_filters:
            filters.append(or_(*car_filters))

    # cost
    if 'cost' in data:
        max_cost = data['cost']
        try:
            max_cost = int(max_cost)
        except ValueError:
            max_cost = 9999999999999
        filters.append(Cost.avg_weekly_cost <= max_cost)

    # main_discipline & secondary_discipline (hvis selected, så må destinasjonen ha det.)
    discipline_filters = []

    if 'main_discipline' in data:
        m_d = data['main_discipline']
        if m_d in ('sport', 'traditional', 'bouldering'):
            discipline_filters.append(Routes.main_discipline == m_d)

    if 'secondary_discipline' in data:
        secondary_disciplines = data['secondary_discipline']
        for d in secondary_disciplines:
            if hasattr(Routes, d):
                discipline_filters.append(getattr(Routes, d) == true())

    if discipline_filters:
        filters.append(and_(*discipline_filters))

    # months
    if 'months' in data:
        months_filters = []
        months_from_ajax = data['months']
        for m in months_from_ajax:
            if hasattr(Months, m):
                months_filters.append(getattr(Months, m) == true())
        if months_filters:
            filters.append(or_(*months_filters))
    # ----------

    return filters, order_p_final
