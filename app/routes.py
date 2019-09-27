from decimal import Decimal

import pycountry_convert
import requests
from flask import (flash, json, jsonify, make_response, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required
from sqlalchemy import and_, or_, true  # , false

from app import app, db, images
from app.forms import (CurrencyForm, DestinationForm, EditDestinationForm)
from app.models import (Accomodation, AdditionalPhotos, Approach, Car, Cost,
                        Destination, Months, Routes, User)
from app.tasks import create_image_set
import os
import secrets
from app import q





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


@app.route('/_convert_currency')
def convert_currency():

    # name = request.cookies.get('userID')

    # Selected currency from index (selected by user)
    c = request.args.get('c', "EUR", type=str)

    # base currency
    get_c = request.cookies.get('currency')
    if get_c:
        c_base = request.cookies.get('currency')
    else:
        c_base = 'EUR'

    # Get rate
    payload = {'base': c_base, 'symbols': c}
    r = requests.get('https://api.ratesapi.io/api/latest', params=payload)

    if r.status_code != 200:
        return 'Error: the translation service failed.'

    j = r.json()
    rate = j['rates'][c]

    if c_base == 'EUR':
        rate_from_euro = rate
    elif c == 'EUR':
        rate_from_euro = 1
    else:
        payload_eur = {'base': 'EUR', 'symbols': c}
        r_e = requests.get('https://api.ratesapi.io/api/latest', params=payload_eur)
        j_e = r_e.json()
        rate_from_euro = j_e['rates'][c]

    # store in cookie
    resp = make_response(jsonify(rate=rate, new_currency=c))
    resp.set_cookie('currency', c)
    resp.set_cookie('rate', str(rate))
    resp.set_cookie('rate_from_euro', str(rate_from_euro))

    return resp


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


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    destinations = Destination.query.filter_by(user_id=user.id)
    return render_template('user.html', user=user, destinations=destinations)


@app.route('/add_destination', methods=['GET', 'POST'])
@login_required
def add_destination():
    # Cannot pass in 'request.form' to AddRecipeForm constructor, as this will cause 'request.files' to not be
    # sent to the form.  This will cause AddRecipeForm to not see the file data.
    # Flask-WTF handles passing form data to the form, so not parameters need to be included.
    def flash_errors(form):
        for field, errors in form.errors.items():
            for error in errors:
                flash(u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                ))

    form = DestinationForm()
    if request.method == 'POST':  # image upload
        if form.validate_on_submit():

            # Featured Photo
            photo_folder_name = form.title.data + '-' + secrets.token_hex(16)
            featured_photo_with_folder = images.save(request.files['featured_photo'], folder=photo_folder_name)
            featured_photo = featured_photo_with_folder.split('/')[1]
            featured_photo_filename = featured_photo.split('.')[0]
            featured_photo_extension = featured_photo.split('.')[-1]
            photo_dir = os.path.join(app.config["UPLOADED_IMAGES_DEST"], photo_folder_name)
            
            photo_folder_url = images.url(featured_photo_with_folder).split(featured_photo)[0]

            q.enqueue(create_image_set, photo_dir, featured_photo)

            # X 1) save image in dir (DEFAULT DIR IN CONFIG?)
            # X 2) enqueue resize function
            # X 3) store filename, dir (secret hex), and extension in database

            # Destination main stuff
            # -- Convert from country code to country name
            country = pycountry_convert.country_alpha2_to_country_name(form.country.data)
            # -- Convert from country code to continent
            continent = pycountry_convert.country_alpha2_to_continent_code(form.country.data)

            destination = Destination(title=form.title.data,
                                      country=country,
                                      continent=continent,
                                      weather_ltd=form.weather_ltd.data,
                                      weather_lng=form.weather_lng.data,
                                      photo_folder_url=photo_folder_url,
                                      featured_photo_filename=featured_photo_filename,
                                      featured_photo_extension=featured_photo_extension,
                                      description=form.description.data,
                                      author=current_user)
            # Add new destination to database
            db.session.add(destination)
            db.session.commit()

            # Get this destination from database, in order to add to all other tables with the destination_id
            d = Destination.query.order_by(Destination.id.desc()).first()

            # Additional photos
            additional_photos_object = []
            for photo in request.files.getlist('additional_photos'):
                photo_filename = images.save(photo)
                photo_url = images.url(photo_filename)
                additional_photos_object.append(AdditionalPhotos(additional_photo_filename=photo_filename,
                                                                 additional_photo_url=photo_url,
                                                                 destination_id=d.id))
            db.session.bulk_save_objects(additional_photos_object)

            # COST
            cost_form_currency = form.cost_form_currency.data
            if cost_form_currency != 'EUR':
                # Getting rate from ratesAPI
                payload = {'base': cost_form_currency, 'symbols': 'EUR'}
                api_currency_data = requests.get('https://api.ratesapi.io/api/latest', params=payload)

                if api_currency_data.status_code == 200:
                    json_api_currency_data = api_currency_data.json()
                    conversion_rate = json_api_currency_data['rates']['EUR']

                    cost_form_currency = 'EUR'

                    beer_at_establishment = Decimal(conversion_rate) * form.beer_at_establishment.data  # required
                    coffee_at_establishment = Decimal(conversion_rate) * form.coffee_at_establishment.data  # required
                    restaurant_inexpensive_meal = Decimal(conversion_rate) * form.restaurant_inexpensive_meal.data  # required
                    groceries_one_week = Decimal(conversion_rate) * form.groceries_one_week.data  # required
                    car_rent_one_week = \
                        (Decimal(conversion_rate) * form.car_rent_one_week.data) if (type(form.car_rent_one_week.data) == Decimal) \
                        else 0
                    gas_one_liter = \
                        (Decimal(conversion_rate) * form.gas_one_liter.data) if (type(form.gas_one_liter.data) == Decimal) else 0
                    km_per_day = \
                        (Decimal(conversion_rate) * form.km_per_day.data) if (type(form.km_per_day.data) == Decimal) else 0
                    tent_per_day = \
                        (Decimal(conversion_rate) * form.tent_per_day.data) if (type(form.tent_per_day.data) == Decimal) else None
                    van_per_day = \
                        (Decimal(conversion_rate) * form.van_per_day.data) if (type(form.van_per_day.data) == Decimal) else None
                    camping_per_day = \
                        (Decimal(conversion_rate) * form.camping_per_day.data) if (type(form.camping_per_day.data) == Decimal) \
                        else None
                    hostel_per_day = \
                        (Decimal(conversion_rate) * form.hostel_per_day.data) if (type(form.hostel_per_day.data) == Decimal) \
                        else None
                    apartment_per_day = \
                        (Decimal(conversion_rate) * form.apartment_per_day.data) if (type(form.apartment_per_day.data) == Decimal) \
                        else None
                    house_per_day = \
                        (Decimal(conversion_rate) * form.house_per_day.data) if (type(form.house_per_day.data) == Decimal) else None
                    hotel_per_day = \
                        (Decimal(conversion_rate) * form.hotel_per_day.data) if (type(form.hotel_per_day.data) == Decimal) else None
                else:
                    beer_at_establishment = form.beer_at_establishment.data  # required
                    coffee_at_establishment = form.coffee_at_establishment.data  # required
                    restaurant_inexpensive_meal = form.restaurant_inexpensive_meal.data  # required
                    groceries_one_week = form.groceries_one_week.data  # required
                    car_rent_one_week = form.car_rent_one_week.data if (type(form.car_rent_one_week.data) == Decimal) \
                        else 0
                    gas_one_liter = form.gas_one_liter.data if (type(form.gas_one_liter.data) == Decimal) else 0
                    km_per_day = form.km_per_day.data if (type(form.km_per_day.data) == Decimal) else 0
                    tent_per_day = form.tent_per_day.data if (type(form.tent_per_day.data) == Decimal) else None
                    van_per_day = form.van_per_day.data if (type(form.van_per_day.data) == Decimal) else None
                    camping_per_day = form.camping_per_day.data if (type(form.camping_per_day.data) == Decimal) else None
                    hostel_per_day = form.hostel_per_day.data if (type(form.hostel_per_day.data) == Decimal) else None
                    apartment_per_day = form.apartment_per_day.data if (type(form.apartment_per_day.data) == Decimal) \
                        else None
                    house_per_day = form.house_per_day.data if (type(form.house_per_day.data) == Decimal) else None
                    hotel_per_day = form.hotel_per_day.data if (type(form.hotel_per_day.data) == Decimal) else None
            else:
                beer_at_establishment = form.beer_at_establishment.data  # required
                coffee_at_establishment = form.coffee_at_establishment.data  # required
                restaurant_inexpensive_meal = form.restaurant_inexpensive_meal.data  # required
                groceries_one_week = form.groceries_one_week.data  # required
                car_rent_one_week = form.car_rent_one_week.data if (type(form.car_rent_one_week.data) == Decimal) else 0
                gas_one_liter = form.gas_one_liter.data if (type(form.gas_one_liter.data) == Decimal) else 0
                km_per_day = form.km_per_day.data if (type(form.km_per_day.data) == Decimal) else 0
                tent_per_day = form.tent_per_day.data if (type(form.tent_per_day.data) == Decimal) else None
                van_per_day = form.van_per_day.data if (type(form.van_per_day.data) == Decimal) else None
                camping_per_day = form.camping_per_day.data if (type(form.camping_per_day.data) == Decimal) else None
                hostel_per_day = form.hostel_per_day.data if (type(form.hostel_per_day.data) == Decimal) else None
                apartment_per_day = form.apartment_per_day.data if (type(form.apartment_per_day.data) == Decimal) else None
                house_per_day = form.house_per_day.data if (type(form.house_per_day.data) == Decimal) else None
                hotel_per_day = form.hotel_per_day.data if (type(form.hotel_per_day.data) == Decimal) else None

            accomodations_form_data = {
                    "tent_per_day": tent_per_day,
                    "van_per_day": van_per_day,
                    "camping_per_day": camping_per_day,
                    "hostel_per_day": hostel_per_day,
                    "apartment_per_day": apartment_per_day,
                    "house_per_day": house_per_day,
                    "hotel_per_day": hotel_per_day
            }

            for key in list(accomodations_form_data):
                if accomodations_form_data[key] is None:
                    del accomodations_form_data[key]

            if accomodations_form_data:  # Checking so it's not empty
                cheapest_accomodation = min(accomodations_form_data, key=accomodations_form_data.get)
            else:  # if it is empty
                accomodations_form_data = {
                    'no_info': 0
                }
                cheapest_accomodation = 'no_info'

            def CalcAvgWeeklyCost():
                avg_weekly_cost = \
                    3 * beer_at_establishment + \
                    3 * coffee_at_establishment + \
                    2 * restaurant_inexpensive_meal + \
                    1 * groceries_one_week + \
                    1 * car_rent_one_week + \
                    7 * gas_one_liter * km_per_day + \
                    7 * accomodations_form_data[cheapest_accomodation]
                return avg_weekly_cost

            avg_weekly_cost = CalcAvgWeeklyCost()
            avg_weekly_cost_rounded = int(avg_weekly_cost)

            cost = Cost(cost_form_currency=cost_form_currency,
                        beer_at_establishment=beer_at_establishment,
                        coffee_at_establishment=coffee_at_establishment,
                        restaurant_inexpensive_meal=restaurant_inexpensive_meal,
                        groceries_one_week=groceries_one_week,
                        car_rent_one_week=car_rent_one_week,
                        gas_one_liter=gas_one_liter,
                        km_per_day=km_per_day,
                        tent_per_day=tent_per_day,
                        van_per_day=van_per_day,
                        camping_per_day=camping_per_day,
                        hostel_per_day=hostel_per_day,
                        apartment_per_day=apartment_per_day,
                        house_per_day=house_per_day,
                        hotel_per_day=hotel_per_day,
                        accomodation_used_for_avg_weekly_cost=cheapest_accomodation,
                        avg_weekly_cost=avg_weekly_cost_rounded,
                        destination_id=d.id)
            db.session.add(cost)

            # ROUTES
            routes = Routes(traditional=form.traditional.data,
                            sport=form.sport.data,
                            bouldering=form.bouldering.data,
                            main_discipline=form.main_discipline.data,
                            easy_routes=form.easy_routes.data,
                            intermediate_routes=form.intermediate_routes.data,
                            hard_routes=form.hard_routes.data,
                            very_hard_routes=form.very_hard_routes.data,
                            total_routes=form.total_routes.data,
                            total_trad=form.total_trad.data,
                            total_sport=form.total_sport.data,
                            total_boulders=form.total_boulders.data,
                            destination_id=d.id)
            db.session.add(routes)

            # MONTHS
            months = Months(january=form.january.data, february=form.february.data, mars=form.mars.data,
                            april=form.april.data, may=form.may.data, june=form.june.data, july=form.july.data,
                            august=form.august.data, september=form.september.data, october=form.october.data,
                            november=form.november.data, december=form.december.data, destination_id=d.id)
            db.session.add(months)

            # ACCOMODATION
            accomodation = Accomodation(tent=form.tent.data, van=form.van.data, hostel=form.hostel.data,
                                        camping=form.camping.data, apartment=form.apartment.data,
                                        house=form.house.data, hotel=form.hotel.data, destination_id=d.id)
            db.session.add(accomodation)

            # APPROACH
            approach = Approach(easy=form.easy.data, moderate=form.moderate.data, hardcore=form.hardcore.data,
                                destination_id=d.id)
            db.session.add(approach)

            # CAR
            car = Car(not_needed=form.not_needed.data, good_to_have=form.good_to_have.data,
                      must_have=form.must_have.data, rent_scooter_locally=form.rent_scooter_locally.data,
                      rent_car_locally=form.rent_car_locally.data, destination_id=d.id)
            db.session.add(car)

            # Commit everything to database
            db.session.commit()
            flash('Destination "{}" added!'.format(str(form.title.data)))
            return redirect(url_for('index'))
        else:
            flash_errors(form)
            flash('ERROR! Destination was not added.', 'error')
    return render_template('add_destination.html',
                           title='Add Destination',
                           form=form)


@app.route('/<int:id>')
def single(id):
    d = Destination.query.get(id)
    currency_form = CurrencyForm()
    return render_template('destination_single_page.html',
                           title='Single Destination',
                           destination=d,
                           currency_form=currency_form)


@app.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    d = Destination.query.get(id)
    form = EditDestinationForm(obj=d)
    if form.validate_on_submit():
        # form.populate_obj(d)
        filename = images.save(request.files['image'])
        url = images.url(filename)

        d.image_filename = filename
        d.image_url = url
        db.session.add(d)
        db.session.commit()
        flash('Destination edited')
        return redirect(url_for('index', id=d.id))

    return render_template('edit_destination.html',
                           title='Edit Destination',
                           form=form,
                           destination=d)


@app.route('/<int:id>/delete')
@login_required
def delete(id):
    d = Destination.query.get(id)
    db.session.delete(d)
    db.session.commit()
    flash('Destination "{}" deleted!'.format(d.title))
    return redirect(url_for('index'))


@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


@app.route('/vote')
def vote():
    return """Här kan man rösta på vilka destinationer som ska läggas till.
              Man kan lägga till en destination eller upvota.
              Bonus: Man kan också kommentera på varje destination."""
