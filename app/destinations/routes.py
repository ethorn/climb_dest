import os
import secrets
from decimal import Decimal

import pycountry_convert
import requests
from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db, images
from app.destinations import bp
from app.destinations.forms import DestinationForm, EditDestinationForm
from app.models import (Accomodation, AdditionalPhotos, Approach, Car, Cost,
                        Destination, Months, Routes)
from app.tasks import create_image_set
from app.destinations.save_destination import save_destination


@bp.route('/add_destination', methods=['GET', 'POST'])
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
            if save_destination(form, new=True):
                flash('Destination "{}" added!'.format(str(form.title.data)))
                return redirect(url_for('main.index'))
        else:
            flash_errors(form)
            flash('ERROR! Destination was not added.', 'error')
    return render_template('destinations/add_destination.html',
                           title='Add Destination',
                           form=form)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    def flash_errors(form):
        for field, errors in form.errors.items():
            for error in errors:
                flash(u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                ))

    d = Destination.query.get(id)

    if request.method == 'POST':  # image upload
        form = EditDestinationForm()
        if form.validate_on_submit():
            if save_destination(form, d, new=False):
                flash('Destination "{}" edited!'.format(str(form.title.data)))
                return redirect(url_for('main.index'))
        else:
            flash_errors(form)
            flash('ERROR! Destination was not edited.', 'error')
            return redirect(url_for('main.index', id=d.id))

    # BELOW FOR PREPOPULATING FORM

    routes = d.routes.first()
    additional_photos = d.additional_photos.all()
    cost = d.cost.first()
    months = d.months.first()
    accomodation = d.accomodation.first()
    approach = d.approach.first()
    car = d.car.first()

    # Country
    d.country_code = pycountry_convert.country_name_to_country_alpha2(d.country)

    # additional_photos
    d.addit_photos = additional_photos

    # routes
    d.main_discipline = routes.main_discipline
    d.traditional = routes.traditional
    d.sport = routes.sport
    d.bouldering = routes.bouldering
    d.total_routes = routes.total_routes
    d.total_sport = routes.total_sport
    d.total_trad = routes.total_trad
    d.total_boulders = routes.total_boulders
    d.easy_routes = routes.easy_routes
    d.intermediate_routes = routes.intermediate_routes
    d.hard_routes = routes.hard_routes
    d.very_hard_routes = routes.very_hard_routes

    # cost
    d.cost_form_currency = cost.cost_form_currency
    d.beer_at_establishment = cost.beer_at_establishment
    d.coffee_at_establishment = cost.coffee_at_establishment
    d.restaurant_inexpensive_meal = cost.restaurant_inexpensive_meal
    d.groceries_one_week = cost.groceries_one_week
    d.car_rent_one_week = cost.car_rent_one_week
    d.gas_one_liter = cost.gas_one_liter
    d.km_per_day = cost.km_per_day
    d.tent_per_day = cost.tent_per_day
    d.van_per_day = cost.van_per_day
    d.camping_per_day = cost.camping_per_day
    d.hostel_per_day = cost.hostel_per_day
    d.apartment_per_day = cost.apartment_per_day
    d.house_per_day = cost.house_per_day
    d.hotel_per_day = cost.hotel_per_day

    # months
    d.january = months.january
    d.february = months.february
    d.march = months.march
    d.april = months.april
    d.may = months.may
    d.june = months.june
    d.july = months.july
    d.august = months.august
    d.september = months.september
    d.october = months.october
    d.november = months.november
    d.december = months.december

    # accomodation
    d.tent = accomodation.tent
    d.van = accomodation.van
    d.hostel = accomodation.hostel
    d.camping = accomodation.camping
    d.apartment = accomodation.apartment
    d.house = accomodation.house
    d.hotel = accomodation.hotel

    # approach
    d.easy = approach.easy
    d.moderate = approach.moderate
    d.hardcore = approach.hardcore

    # car
    d.not_needed = car.not_needed
    d.good_to_have = car.good_to_have
    d.must_have = car.must_have

    form = EditDestinationForm(obj=d)

    return render_template('destinations/edit_destination.html',
                           title='Edit Destination',
                           form=form,
                           destination=d)


@bp.route('/<int:id>/delete')
@login_required
def delete(id):
    d = Destination.query.get(id)
    db.session.delete(d)
    db.session.commit()
    flash('Destination "{}" deleted!'.format(d.title))
    return redirect(url_for('main.index'))

@bp.route('/<int:id>/additional_photo/<int:photo_id>/delete')
@login_required
def delete_additional_img(id, photo_id):
    photo = AdditionalPhotos.query.get(photo_id)
    db.session.delete(photo)
    db.session.commit()
    flash('Additional image deleted!')
    return redirect(url_for('main.index'))
