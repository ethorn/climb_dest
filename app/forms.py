from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, PasswordField, BooleanField, SubmitField, SelectField, \
    FileField, MultipleFileField, HiddenField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Length, Email, EqualTo, Optional
from flask_wtf.file import FileAllowed, FileRequired
from app.models import User
from app import images
import pycountry

class CountrySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(CountrySelectField, self).__init__(*args, **kwargs)
        self.choices = [(country.alpha_2, country.name) for country in pycountry.countries]
        self.choices.insert(0, ('', 'Choose Country'))


class EditProfileForm(FlaskForm):
    displayname = StringField('Display name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    bio = TextAreaField('About me', validators=[Length(min=0, max=280)])
    submit = SubmitField('Submit')

    # Dette er kun for å endre username, som trenger å være unikt:

    # def __init__(self, original_username, *args, **kwargs):
    #     super(EditProfileForm, self).__init__(*args, **kwargs)
    #     self.original_username = original_username

    # def validate_username(self, username):
    #     if username.data != self.original_username:
    #         user = User.query.filter_by(username=self.username.data).first()
    #         if user is not None:
    #             raise ValidationError('Please use a different username.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')  # the string gives the text for the label
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):  # When you add any methods that match the pattern validate_<field_name>,
                                            # WTForms takes those as custom validators and invokes them in addition to
                                            # the stock validators. In this case I want to make sure that the username
                                            # and email address entered by the user are not already in the database, so
                                            # these two methods issue database queries expecting there will be no
                                            # results. In the event a result exists, a validation error is triggered
                                            # by raising ValidationError. The message included as the argument in the
                                            # exception will be the message that will be displayed next to the field
                                            # for the user to see.
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class CurrencyForm(FlaskForm):
    currency = SelectField('Currency', choices=[('EUR', 'EUR'), ('AUD', 'AUD'), ('BGN', 'BGN'), ('BRL', 'BRL'),
                                                ('CAD', 'CAD'), ('CHF', 'CHF'), ('CNY', 'CNY'), ('CZK', 'CZK'),
                                                ('DKK', 'DKK'), ('GBP', 'GBP'), ('HKD', 'HKD'), ('HRK', 'HRK'),
                                                ('HUF', 'HUF'), ('IDR', 'IDR'), ('ILS', 'ILS'), ('INR', 'INR'),
                                                ('ISK', 'ISK'), ('JPY', 'JPY'), ('KRW', 'KRW'), ('MXN', 'MXN'),
                                                ('MYR', 'MYR'), ('NOK', 'NOK'), ('NZD', 'NZD'), ('PHP', 'PHP'),
                                                ('PLN', 'PLN'), ('RON', 'RON'), ('RUB', 'RUB'), ('SEK', 'SEK'),
                                                ('SGD', 'SGD'), ('THB', 'THB'), ('TRY', 'TRY'), ('USD', 'USD'),
                                                ('ZAR', 'ZAR')])
    submit = SubmitField('Change')


class DestinationForm(FlaskForm):
    # General information
    title = StringField('Name of destination', render_kw={"placeholder": "e.g. 'Kalymnos'"}, validators=[DataRequired()])
    country = CountrySelectField('Country', validators=[DataRequired()])
    weather_place_autocomplete = StringField('Place to use for weather forecast ', validators=[DataRequired()])
    weather_ltd = HiddenField('Latitude', validators=[DataRequired()])
    weather_lng = HiddenField('Longitude', validators=[DataRequired()])
    featured_photo = FileField('Featured Photo', validators=[FileRequired(), FileAllowed(images, 'Images only!')])
    additional_photos = MultipleFileField('Additional Photos', validators=[FileAllowed(images, 'Images only!')])
    description = TextAreaField('Description')

    # Disciplines
    traditional = BooleanField('Traditional')
    sport = BooleanField('Sport')
    bouldering = BooleanField('Bouldering')
    main_discipline = SelectField('Main discipline',
                                  choices=[('traditional', 'Traditional'),
                                           ('bouldering', 'Bouldering'),
                                           ('sport', 'Sport')],
                                  validators=[DataRequired()])

    # Months/Season
    january = BooleanField('January')
    february = BooleanField('February')
    mars = BooleanField('March')
    april = BooleanField('April')
    may = BooleanField('May')
    june = BooleanField('June')
    july = BooleanField('July')
    august = BooleanField('August')
    september = BooleanField('September')
    october = BooleanField('October')
    november = BooleanField('November')
    december = BooleanField('December')

    # Accomodation
    tent = BooleanField('Tent')
    van = BooleanField('Van')
    hostel = BooleanField('Hostel')
    camping = BooleanField('Camping')
    apartment = BooleanField('Apartment')
    house = BooleanField('House')
    hotel = BooleanField('Hotel')

    # Approach
    easy = BooleanField('Easy')
    moderate = BooleanField('Moderate')
    hardcore = BooleanField('Hardcore')

    # Car
    not_needed = BooleanField('Not needed')
    good_to_have = BooleanField('Good to have')
    must_have = BooleanField('Must have')
    rent_scooter_locally = BooleanField('Scooter available locally')
    rent_car_locally = BooleanField('Car available locally')

    # Cost
    cost_form_currency = SelectField('Currency',
                                     choices=[('EUR', 'EUR'), ('AUD', 'AUD'), ('BGN', 'BGN'),
                                              ('BRL', 'BRL'), ('CAD', 'CAD'), ('CHF', 'CHF'),
                                              ('CNY', 'CNY'), ('CZK', 'CZK'), ('DKK', 'DKK'),
                                              ('GBP', 'GBP'), ('HKD', 'HKD'), ('HRK', 'HRK'),
                                              ('HUF', 'HUF'), ('IDR', 'IDR'), ('ILS', 'ILS'),
                                              ('INR', 'INR'), ('ISK', 'ISK'), ('JPY', 'JPY'),
                                              ('KRW', 'KRW'), ('MXN', 'MXN'), ('MYR', 'MYR'),
                                              ('NOK', 'NOK'), ('NZD', 'NZD'), ('PHP', 'PHP'),
                                              ('PLN', 'PLN'), ('RON', 'RON'), ('RUB', 'RUB'),
                                              ('SEK', 'SEK'), ('SGD', 'SGD'), ('THB', 'THB'),
                                              ('TRY', 'TRY'), ('USD', 'USD'), ('ZAR', 'ZAR')],
                                     validators=[DataRequired()],
                                     default='EUR')
    beer_at_establishment = DecimalField('Beer at establishment', render_kw={"placeholder": "e.g. '2.5'", "class": "integer"}, validators=[DataRequired()])
    coffee_at_establishment = DecimalField('Coffee at establishment', render_kw={"class": "integer"}, validators=[DataRequired()])
    restaurant_inexpensive_meal = DecimalField('Inexpensive meal at restaurant', render_kw={"class": "integer"}, validators=[DataRequired()])
    groceries_one_week = DecimalField('One week of groceries', render_kw={"class": "integer"}, validators=[DataRequired()])
    car_rent_one_week = DecimalField('One week car rental', render_kw={"placeholder": "e.g. '143'", "class": "integer"}, validators=[Optional()])
    gas_one_liter = DecimalField('One liter of gas', render_kw={"class": "integer"}, validators=[Optional()])
    km_per_day = DecimalField('Average kilometers of driving per day', render_kw={"class": "integer"}, validators=[Optional()])
    tent_per_day = DecimalField('Tent (per night)', render_kw={"placeholder": "e.g. '9'", "class": "integer"}, validators=[Optional()])
    van_per_day = DecimalField('Van (per night)', render_kw={"class": "integer"}, validators=[Optional()])
    camping_per_day = DecimalField('Camping (per night)', render_kw={"class": "integer"}, validators=[Optional()])
    hostel_per_day = DecimalField('Hostel (per night)', render_kw={"class": "integer"}, validators=[Optional()])
    apartment_per_day = DecimalField('Apartment (per night)', render_kw={"class": "integer"}, validators=[Optional()])
    house_per_day = DecimalField('House (per night)', render_kw={"class": "integer"}, validators=[Optional()])
    hotel_per_day = DecimalField('Hotel (per night)', render_kw={"class": "integer"}, validators=[Optional()])

    # Routes
    total_routes = IntegerField('Total number of routes (including sport, trad and boulder problems)', render_kw={"placeholder": "e.g. '1250'", "class": "integer"}, validators=[Optional()])
    total_sport = IntegerField('Number of sport routes', render_kw={"class": "integer"}, validators=[Optional()])
    total_trad = IntegerField('Number of traditional routes', render_kw={"class": "integer"}, validators=[Optional()])
    total_boulders = IntegerField('Number of boulder problems', render_kw={"class": "integer"}, validators=[Optional()])
    easy_routes = DecimalField('Number of easy routes (up to 4+)', render_kw={"class": "integer"}, validators=[Optional()])
    intermediate_routes = DecimalField('Number of intermediate routes (5 to 6a+)', render_kw={"class": "integer"}, validators=[Optional()])
    hard_routes = DecimalField('Number of hard routes (6b to 7a)', render_kw={"class": "integer"}, validators=[Optional()])
    very_hard_routes = DecimalField('Number of hard routes (7a+ and up)', render_kw={"class": "integer"}, validators=[Optional()])

    # Submit
    submit = SubmitField('Add Destination!')


class EditDestinationForm(FlaskForm):
    title = StringField('Destination title', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    discipline = SelectField('Main discipline', choices=[(
        'traditional', 'Traditional'), ('bouldering', 'Bouldering'), ('sport', 'Sport')], validators=[DataRequired()])
    image = FileField('Destination Photo', validators=[FileRequired(), FileAllowed(images, 'Images only!')])
    submit = SubmitField('Update')
