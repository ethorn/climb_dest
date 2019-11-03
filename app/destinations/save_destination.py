import os
import secrets
from app.models import (Accomodation, AdditionalPhotos, Approach, Car, Cost,
                        Destination, Months, Routes)
from flask import request, current_app, flash
from flask_login import current_user
from app.destinations.forms import EditDestinationForm
from app import images, db
from app.tasks import create_image_set
import pycountry_convert
from decimal import Decimal
import requests

# TODO
# current_app kanskje failar?


def flash_errors(form):
        for field, errors in form.errors.items():
            for error in errors:
                flash(u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                ))


def save_destination(form, destination=None, new=True):
    # PHOTOS
    try:
        request_featured_photo = request.files['featured_photo']
    except KeyError:
        request_featured_photo = False

    if request_featured_photo:
        if new:
            photo_folder_name = form.title.data + '-' + secrets.token_hex(16)
            featured_photo_with_folder = images.save(request.files['featured_photo'], folder=photo_folder_name)
            featured_photo = featured_photo_with_folder.split('/')[1]
            featured_photo_filename = featured_photo.split('.')[0]
            featured_photo_extension = featured_photo.split('.')[-1]
            photo_dir = os.path.join(current_app.config["UPLOADED_IMAGES_DEST"], photo_folder_name)

            photo_folder_url = images.url(featured_photo_with_folder).split(featured_photo)[0]

            current_app.q.enqueue(create_image_set, photo_dir, featured_photo)
        else:
            # Bruke tidligere skapt folder, og hente featured_photo fra form:
            photo_folder_name = destination.photo_folder_url.split('/static/uploads/images/')[-1]  # http://127.0.0.1:5000/static/uploads/images/Oskarshamn-7296b6784120247d3125ace582cdc17e/
            featured_photo_with_folder = images.save(request.files['featured_photo'], folder=photo_folder_name)
            featured_photo = featured_photo_with_folder.split('/')[1]
            featured_photo_filename = featured_photo.split('.')[0]
            featured_photo_extension = featured_photo.split('.')[-1]
            photo_dir = os.path.join(current_app.config["UPLOADED_IMAGES_DEST"], photo_folder_name)  # samma struktur som photo_dir: app/static/uploads/images/Oskarshamn-7296b6784120247d3125ace582cdc17e/
            # photo_folder_url = images.url(featured_photo_with_folder).split(featured_photo)[0]
            # Sende til enqueue
            current_app.q.enqueue(create_image_set, photo_dir, featured_photo)
            # Oppdatere befintlig destination med url/fil/extension
            # - Gjørs nedan

    # COUNTRY & CONTINENT
    country = pycountry_convert.country_alpha2_to_country_name(form.country.data)

    continent_code = pycountry_convert.country_alpha2_to_continent_code(form.country.data)
    continents = {
        'AF': 'Africa',
        'AN': 'Antarctica',
        'AS': 'Asia',
        'EU': 'Europe',
        'NA': 'North America',
        'OC': 'Oceania',
        'SA': 'South America'
    }
    continent = continents[continent_code]

    # Add new destination
    if new:
        d = Destination(title=form.title.data,
                        country=country,
                        continent=continent,
                        weather_ltd=form.weather_ltd.data,
                        weather_lng=form.weather_lng.data,
                        photo_folder_url=photo_folder_url,
                        featured_photo_filename=featured_photo_filename,
                        featured_photo_extension=featured_photo_extension,
                        description=form.description.data,
                        author=current_user)
        db.session.add(d)
        db.session.commit()
    else:
        destination.title = form.title.data
        destination.country = country
        destination.continent = continent
        destination.weather_ltd = form.weather_ltd.data
        destination.weather_ltd = form.weather_lng.data
        # destination.photo_folder_url = photo_folder_url  # trenger ikke oppdatere denne
        if request_featured_photo:
            destination.featured_photo_filename = featured_photo_filename
        if request_featured_photo:
            destination.featured_photo_extension = featured_photo_extension
        destination.description = form.description.data
        # edited by ??
        db.session.commit()

    if new:
        d = Destination.query.order_by(Destination.id.desc()).first()
    else:
        d = destination

    # Additional photos
    if request.files.getlist('additional_photos'):
        additional_photos_object = []
        for photo in request.files.getlist('additional_photos'):
            photo_folder_name = d.photo_folder_url.split('/static/uploads/images/')[-1]
            additional_photo_folder_name = photo_folder_name + 'additional_photos'
            additional_photo_with_folder = images.save(photo, folder=additional_photo_folder_name)
            additional_photo = additional_photo_with_folder.split('/')[2]
            additional_photo_filename = additional_photo.split('.')[0]
            additional_photo_extension = additional_photo.split('.')[-1]
            photo_dir = os.path.join(current_app.config["UPLOADED_IMAGES_DEST"], additional_photo_folder_name)

            current_app.q.enqueue(create_image_set, photo_dir, additional_photo)

            additional_photos_object.append(AdditionalPhotos(additional_photo_filename=additional_photo_filename,
                                                             additional_photo_extension=additional_photo_extension,
                                                             destination_id=d.id))
        db.session.bulk_save_objects(additional_photos_object)

    # COST
    cost_form_currency = form.cost_form_currency.data
    if cost_form_currency != 'EUR':  # EUR on default
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

    for key in list(accomodations_form_data):  # Makes a list of al the keys in the dict
        if accomodations_form_data[key] is None:
            del accomodations_form_data[key]

    if accomodations_form_data:  # Checking so it's not empty
        cheapest_accomodation = min(accomodations_form_data, key=accomodations_form_data.get)
    else:  # if it is empty
        accomodations_form_data = {
            'no_info': 0
        }
        cheapest_accomodation = 'no_info'

    avg_weekly_cost = \
        3 * beer_at_establishment + \
        3 * coffee_at_establishment + \
        2 * restaurant_inexpensive_meal + \
        1 * groceries_one_week + \
        1 * car_rent_one_week + \
        7 * gas_one_liter * km_per_day + \
        7 * accomodations_form_data[cheapest_accomodation]

    avg_weekly_cost_rounded = int(avg_weekly_cost)

    if new:
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
    else:
        cost = Cost.query.filter(Cost.destination_id == d.id).first()
        cost.beer_at_establishment = beer_at_establishment
        cost.cost_form_currency = cost_form_currency
        cost.coffee_at_establishment = coffee_at_establishment
        cost.restaurant_inexpensive_meal = restaurant_inexpensive_meal
        cost.groceries_one_week = groceries_one_week
        cost.car_rent_one_week = car_rent_one_week
        cost.gas_one_liter = gas_one_liter
        cost.km_per_day = km_per_day
        cost.tent_per_day = tent_per_day
        cost.van_per_day = van_per_day
        cost.camping_per_day = camping_per_day
        cost.hostel_per_day = hostel_per_day
        cost.apartment_per_day = apartment_per_day
        cost.house_per_day = house_per_day
        cost.hotel_per_day = hotel_per_day
        cost.accomodation_used_for_avg_weekly_cost = cheapest_accomodation
        cost.avg_weekly_cost = avg_weekly_cost_rounded

    # ROUTES
    if new:
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
    else:
        routes = Routes.query.filter(Routes.destination_id == d.id).first()
        routes.traditional = form.traditional.data
        routes.sport = form.sport.data
        routes.bouldering = form.bouldering.data
        routes.main_discipline = form.main_discipline.data
        routes.easy_routes = form.easy_routes.data
        routes.intermediate_routes = form.intermediate_routes.data
        routes.hard_routes = form.hard_routes.data
        routes.very_hard_routes = form.very_hard_routes.data
        routes.total_routes = form.total_routes.data
        routes.total_trad = form.total_trad.data
        routes.total_sport = form.total_sport.data
        routes.total_boulders = form.total_boulders.data
        # db.session.commit()  # her?

    # MONTHS
    if new:
        months = Months(january=form.january.data, february=form.february.data, march=form.march.data,
                        april=form.april.data, may=form.may.data, june=form.june.data, july=form.july.data,
                        august=form.august.data, september=form.september.data, october=form.october.data,
                        november=form.november.data, december=form.december.data, destination_id=d.id)
        db.session.add(months)
    else:
        months = Months.query.filter(Months.destination_id == d.id).first()
        months.january = form.january.data
        months.february = form.february.data
        months.march = form.march.data
        months.april = form.april.data
        months.may = form.may.data
        months.june = form.june.data
        months.july = form.july.data
        months.august = form.august.data
        months.september = form.september.data
        months.october = form.october.data
        months.november = form.november.data
        months.december = form.december.data

    # ACCOMODATION
    if new:
        accomodation = Accomodation(tent=form.tent.data, van=form.van.data, hostel=form.hostel.data,
                                    camping=form.camping.data, apartment=form.apartment.data,
                                    house=form.house.data, hotel=form.hotel.data, destination_id=d.id)
        db.session.add(accomodation)
    else:
        accomodation = Accomodation.query.filter(Accomodation.destination_id == d.id).first()
        accomodation.tent = form.tent.data
        accomodation.van = form.van.data
        accomodation.hostel = form.hostel.data
        accomodation.camping = form.camping.data
        accomodation.apartment = form.apartment.data
        accomodation.house = form.house.data
        accomodation.hotel = form.hotel.data

    # APPROACH
    if new:
        approach = Approach(easy=form.easy.data, moderate=form.moderate.data, hardcore=form.hardcore.data,
                            destination_id=d.id)
        db.session.add(approach)
    else:
        approach = Approach.query.filter(Approach.destination_id == d.id).first()
        approach.easy = form.easy.data
        approach.moderate = form.moderate.data
        approach.hardcore = form.hardcore.data

    # CAR
    if new:
        car = Car(not_needed=form.not_needed.data,
                  good_to_have=form.good_to_have.data,
                  must_have=form.must_have.data,
                  # rent_scooter_locally=form.rent_scooter_locally.data,
                  # rent_car_locally=form.rent_car_locally.data,
                  destination_id=d.id)
        db.session.add(car)
    else:
        car = Car.query.filter(Car.destination_id == d.id).first()
        car.not_needed = form.not_needed.data
        car.good_to_have = form.good_to_have.data
        car.must_have = form.must_have.data
        # car.rent_scooter_locally = form.rent_scooter_locally.data,
        # car.rent_car_locally = form.rent_car_locally.data

    db.session.commit()
    return True  # Hvordan returnere False hvis den failer?
