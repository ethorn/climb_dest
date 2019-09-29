from app.models import (Accomodation, Car, Cost, Destination, Months, Routes)
from sqlalchemy import and_, or_, true
from flask import request


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

    return filters, order_p_final
