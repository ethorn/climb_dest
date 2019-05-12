from flask import render_template, flash, redirect, url_for, request, json, jsonify, make_response
from app import app, db, images
from app.forms import LoginForm, RegistrationForm, DestinationForm, EditDestinationForm, CurrencyForm
from app.forms import ResetPasswordRequestForm, ResetPasswordForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Destination, Routes, Cost, Months, Accomodation, Approach, Car, AdditionalPhotos
from werkzeug.urls import url_parse
from sqlalchemy import or_, and_, true  # , false
from app.email import send_password_reset_email

# request for API
import requests


@app.route('/dashboard/<page>', methods=['GET', 'POST'])
@login_required
def dashboard(page):
    if page == "settings":
        form = EditProfileForm()
        if form.validate_on_submit():
            current_user.displayname = form.displayname.data
            current_user.location = form.location.data
            current_user.bio = form.bio.data
            db.session.commit()
            flash('Your settings have been saved.')
            return redirect(url_for('dashboard', page='settings'))
        elif request.method == 'GET':
            form.displayname.data = current_user.displayname
            form.location.data = current_user.location
            form.bio.data = current_user.bio
        return render_template('dashboard/dashboard.html', page=page, form=form)
    return render_template('dashboard/dashboard.html', page=page)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)  # static function, the method is called without a User instance
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


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
        order_parameter = Cost.weekly_avg
    elif sort_by == "time":
        order_parameter = Destination.timestamp
    elif sort_by == "routes23":
        order_parameter = Routes.range_23
    elif sort_by == "routes4":
        order_parameter = Routes.range_4
    elif sort_by == "routes5":
        order_parameter = Routes.range_5
    elif sort_by == "routes6":
        order_parameter = Routes.range_6
    elif sort_by == "routes7":
        order_parameter = Routes.range_7
    elif sort_by == "routes8":
        order_parameter = Routes.range_8
    elif sort_by == "routes9":
        order_parameter = Routes.range_9
    elif sort_by == "total_routes":
        order_parameter = Routes.total_routes
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

        filters.append(Cost.weekly_avg <= max_cost)

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
        destinations = Destination.query.order_by(order_p_final).all()
    ######

    # Return
    return render_template('loop_wrapper.html', destinations=destinations)
    ######


@app.route('/_convert_currency')
def convert():

    # name = request.cookies.get('userID')

    # Selected currency from indes (selected by user)
    c = request.args.get('c', "EUR", type=str)

    # base currency
    get_c = request.cookies.get('currency')
    if get_c:
        c_base = request.cookies.get('currency')
    else:
        c_base = 'EUR'

    # Get rate
    payload = {'base': c_base, 'symbols': c}
    r = requests.get('https://ratesapi.io/api/latest', params=payload)

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
        r_e = requests.get('https://ratesapi.io/api/latest', params=payload_eur)
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
                order_parameter = Cost.weekly_avg
            elif sort_by == "time":
                order_parameter = Destination.timestamp
            elif sort_by == "routes23":
                order_parameter = Routes.range_23
            elif sort_by == "routes4":
                order_parameter = Routes.range_4
            elif sort_by == "routes5":
                order_parameter = Routes.range_5
            elif sort_by == "routes6":
                order_parameter = Routes.range_6
            elif sort_by == "routes7":
                order_parameter = Routes.range_7
            elif sort_by == "routes8":
                order_parameter = Routes.range_8
            elif sort_by == "routes9":
                order_parameter = Routes.range_9
            elif sort_by == "total_routes":
                order_parameter = Routes.total_routes
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

            filters.append(Cost.weekly_avg <= max_cost)

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
            destinations = Destination.query.order_by(order_p_final).all()
    else:
        destinations = Destination.query.all()

    currency_form = CurrencyForm()

    return render_template('index.html', title='Home', destinations=destinations, request=request,
                           currency_form=currency_form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    destinations = [
        {'author': user, 'destination': 'Lofoten test'},
        {'author': user, 'destination': 'Bohuslaen test'}
    ]
    return render_template('user.html', user=user, destinations=destinations)


# imports the LoginForm class from forms.py, puts it into a variable,
# and sends it to the html template
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # checks if the user is logged in or not
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')  # from (/login?next=/index) gets the value of ?next=
        if not next_page or url_parse(next_page).netloc != '':
            # .netloc checks if the URL in ?next= is absolute or relative, if absolute (http://www.domain.com/...)
            # it redirects to index for security purposes
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


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
            featured_photo_filename = images.save(request.files['featured_photo'])
            featured_photo_url = images.url(featured_photo_filename)

            # Destination main stuff
            destination = Destination(title=form.title.data,
                                      country=form.country.data,
                                      weather_ltd=form.weather_ltd.data,
                                      weather_lng=form.weather_lng.data,
                                      featured_photo_filename=featured_photo_filename,
                                      featured_photo_url=featured_photo_url,
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

            # ### CURRENCY TO EUR
            # REQUEST FOR CURRENCY DATA
            # payload = {'base': form.currency.data, 'symbols': 'EUR'}
            # r = requests.get('https://ratesapi.io/api/latest', params=payload)
            # j = r.json()
            # rate = j['rates']['EUR']

            # currency = 'EUR'
            # weekly_avg = round((form.weekly_avg.data * rate), 0)
            # tent_cost = round((form.tent_cost.data * rate), 0)
            # hostel_cost = round((form.hostel_cost.data * rate), 0)
            # apartment_cost = round((form.apartment_cost.data * rate), 0)
            # hotel_cost = round((form.hotel_cost.data * rate), 0)
            ##

            # ### ROUTES PROPERTIES
            range_23 = form.r_2.data + form.r_3.data
            range_4 = form.r_4.data + form.r_4_p.data
            range_5 = form.r_5a.data + form.r_5b.data + form.r_5c.data
            range_6 = form.r_6a.data + form.r_6a_p.data + form.r_6b.data + form.r_6b_p.data + form.r_6c.data + \
                form.r_6c_p.data
            range_7 = form.r_7a.data + form.r_7a_p.data + form.r_7b.data + form.r_7b_p.data + form.r_7c.data + \
                form.r_7c_p.data
            range_8 = form.r_8a.data + form.r_8a_p.data + form.r_8b.data + form.r_8b_p.data + form.r_8c.data + \
                form.r_8c_p.data
            range_9 = form.r_9a.data + form.r_9a_p.data + form.r_9b.data + form.r_9b_p.data + form.r_9c.data
            total_routes = range_23 + range_4 + range_5 + range_6 + range_7 + range_8 + range_9
            ###

            # cost = Cost(currency=currency, weekly_avg=weekly_avg, tent=tent_cost, hostel=hostel_cost,
            #             apartment=apartment_cost, hotel=hotel_cost, destination_id=d.id)
            months = Months(january=form.january.data, february=form.february.data, mars=form.mars.data,
                            april=form.april.data, may=form.may.data, june=form.june.data, july=form.july.data,
                            august=form.august.data, september=form.september.data, october=form.october.data,
                            november=form.november.data, december=form.december.data, destination_id=d.id)
            accomodation = Accomodation(tent=form.tent.data, van=form.van.data, hostel=form.hostel.data,
                                        camping=form.camping.data, apartment=form.apartment.data,
                                        house=form.house.data, hotel=form.hotel.data, destination_id=d.id)
            approach = Approach(easy=form.easy.data, moderate=form.moderate.data, hardcore=form.hardcore.data,
                                destination_id=d.id)
            car = Car(not_needed=form.not_needed.data, good_to_have=form.good_to_have.data,
                      must_have=form.must_have.data, rent_scooter_locally=form.rent_scooter_locally.data,
                      rent_car_locally=form.rent_car_locally.data, destination_id=d.id)
            routes = Routes(traditional=form.traditional.data, sport=form.sport.data, bouldering=form.bouldering.data,
                            main_discipline=form.main_discipline.data, r_2=form.r_2.data, r_3=form.r_3.data,
                            range_23=range_23, r_4=form.r_4.data, r_4_p=form.r_4_p.data, range_4=range_4,
                            r_5a=form.r_5a.data, r_5b=form.r_5b.data, r_5c=form.r_5c.data, range_5=range_5,
                            r_6a=form.r_6a.data, r_6a_p=form.r_6a_p.data, r_6b=form.r_6b.data, r_6b_p=form.r_6b_p.data,
                            r_6c=form.r_6c.data, r_6c_p=form.r_6c_p.data, range_6=range_6, r_7a=form.r_7a.data,
                            r_7a_p=form.r_7a_p.data, r_7b=form.r_7b.data, r_7b_p=form.r_7b_p.data, r_7c=form.r_7c.data,
                            r_7c_p=form.r_7c_p.data, range_7=range_7, r_8a=form.r_8a.data, r_8a_p=form.r_8a_p.data,
                            r_8b=form.r_8b.data, r_8b_p=form.r_8b_p.data, r_8c=form.r_8c.data, r_8c_p=form.r_8c_p.data,
                            range_8=range_8, r_9a=form.r_9a.data, r_9a_p=form.r_9a_p.data, r_9b=form.r_9b.data,
                            r_9b_p=form.r_9b_p.data, r_9c=form.r_9c.data, range_9=range_9, total_routes=total_routes,
                            destination_id=d.id)
            # db.session.add(cost)
            db.session.add(months)
            db.session.add(accomodation)
            db.session.add(approach)
            db.session.add(car)
            db.session.add(routes)
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


@app.route('/find_partner')
def find_partner():
    return "Her skal man kunne finne klatrepartners for sin reise"


@app.route('/vote')
def vote():
    return """Här kan man rösta på vilka destinationer som ska läggas till.
              Man kan lägga till en destination eller upvota.
              Bonus: Man kan också kommentera på varje destination."""


@app.route('/query-example')
def query_example():
    # # Query arguments:
    # http://127.0.0.1:5000/query-example?language=Python
    # query string begins after '?'

    # # Generate query string by:
    # * manually in a function somewhere, and add it to the url
    # * by form with GET method

    # # Process with:
    # request.args.get('language') # The app will continue to run if the language key doesn't exist in the URL
    # request.args['language'] # The app will return a 400 error if the language key doesn't exist in the URL

    language = request.args.get('language')  # if key doesn't exist, returns None
    framework = request.args['framework']  # if key doesn't exist, returns a 400, bad request error
    website = request.args.get('website')

    return '''<h1>The language value is: {}</h1>
              <h1>The framework value is: {}</h1>
              <h1>The website value is: {}'''.format(language, framework, website)


@app.route('/form-example', methods=['GET', 'POST'])  # allow both GET and POST requests)
def form_example():
    """
    Form data comes from a form that has been sent as a POST request to a route.
    So instead of seeing the data in the URL (except for cases when the form is
    submitted with a GET request), the form data will be passed to the app behind
    the scenes. Even though you can't easily see the form data that gets passed,
    your app can still read it.
    """
    """
    Inside the view function, we need to check if the request method is GET or POST.
    If it's GET, we simply display the form we have. If it's POST, then we want to
    process the incoming data.
    """

    # The following form performs a POST request to the same route that generated the form.
    # The keys come from the "name" attribute

    if request.method == 'POST':  # this block is only entered when the form is submitted
        language = request.form.get('language')
        framework = request.form['framework']

        return '''<h1>The language value is: {}</h1>
                  <h1>The framework value is: {}</h1>'''.format(language, framework)

    return '''<form method="POST">
                  Language: <input type="text" name="language"><br>
                  Framework: <input type="text" name="framework"><br>
                  <input type="submit" value="Submit"><br>
              </form>'''


@app.route('/json-example', methods=['POST'])  # GET requests will be blocked
def json_example():
    """
    Like form data, it's not so easy to see. JSON data is normally constructed by a process that calls our route.
    {
        "language" : "Python",
        "framework" : "Flask",
        "website" : "Scotch",
        "version_info" : {
            "python" : 3.4,
            "flask" : 0.12
        },
        "examples" : ["query", "form", "json"],
        "boolean_test" : true
    }
    """
    req_data = request.get_json()

    language = req_data['language']
    framework = req_data['framework']
    python_version = req_data['version_info']['python']  # two keys are needed because of the nested object
    example = req_data['examples'][0]  # an index is needed because of the array
    boolean_test = req_data['boolean_test']

    return '''
           The language value is: {}
           The framework value is: {}
           The Python version is: {}
           The item at index 0 in the example list is: {}
           The boolean value is: {}'''.format(language, framework, python_version, example, boolean_test)


@app.route('/ajax-example')
def ajax_example():
    # Antar at request.get_json() funker?
    # request.form.get('order') funker og
    # request.args.get('a') FUNKER IKKE (virker som at det bare funker på url arguments)
    return "todo.."
