from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, PasswordField, BooleanField, SubmitField, SelectField, \
    FileField, MultipleFileField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Length, Email, EqualTo
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
    title = StringField('Name of destination (e.g. "Kalymnos")', validators=[DataRequired()])
    country = CountrySelectField('Country', validators=[DataRequired()])
    weather_place_autocomplete = StringField('Area or city for weather forecast', validators=[DataRequired()])
    weather_ltd = HiddenField('Latitude', validators=[DataRequired()])
    weather_lng = HiddenField('Longitude', validators=[DataRequired()])
    featured_photo = FileField('Featured Photo', validators=[FileRequired(), FileAllowed(images, 'Images only!')])
    additional_photos = MultipleFileField('Additional Photos', validators=[FileAllowed(images, 'Images only!')])
    description = TextAreaField('Destination description')

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
    currency = SelectField('Currency',
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
    beer_at_establishment = IntegerField('Beer at establishment')
    coffee_at_establishment = IntegerField('Coffee at establishment')
    restaurant_inexpensive_meal = IntegerField('Inexpensive meal at restaurant')
    groceries_one_week = IntegerField('One week of groceries')
    car_rent_one_week = IntegerField('Renting car for one week')
    gas_one_liter = IntegerField('One liter of gasoline')
    km_per_day = IntegerField('Average kilometers of driving per day')
    tent_per_day = IntegerField('Cost per night in tent')
    van_per_day = IntegerField('Cost per night in van')
    camping_per_day = IntegerField('Cost per night in camping')
    hostel_per_day = IntegerField('Cost per night in hostel')
    apartment_per_day = IntegerField('Cost per night in apartment')
    house_per_day = IntegerField('Cost per night in house')
    hotel_per_day = IntegerField('Cost per night in hotel')

    # Routes
    r_2 = IntegerField('2', render_kw={"placeholder": "0"}, default=4)
    r_3 = IntegerField('3', render_kw={"placeholder": "0"}, default=4)
    r_4 = IntegerField('4', render_kw={"placeholder": "0"}, default=4)
    r_4_p = IntegerField('4+', render_kw={"placeholder": "0"}, default=4)
    r_5a = IntegerField('5a', render_kw={"placeholder": "0"}, default=4)
    r_5b = IntegerField('5b', render_kw={"placeholder": "0"}, default=4)
    r_5c = IntegerField('5c', render_kw={"placeholder": "0"}, default=4)
    r_6a = IntegerField('6a', render_kw={"placeholder": "0"}, default=4)
    r_6a_p = IntegerField('6a+', render_kw={"placeholder": "0"}, default=4)
    r_6b = IntegerField('6b', render_kw={"placeholder": "0"}, default=4)
    r_6b_p = IntegerField('6b+', render_kw={"placeholder": "0"}, default=4)
    r_6c = IntegerField('6c', render_kw={"placeholder": "0"}, default=4)
    r_6c_p = IntegerField('6c+', render_kw={"placeholder": "0"}, default=4)
    r_7a = IntegerField('7a', render_kw={"placeholder": "0"}, default=4)
    r_7a_p = IntegerField('7a+', render_kw={"placeholder": "0"}, default=4)
    r_7b = IntegerField('7b', render_kw={"placeholder": "0"}, default=4)
    r_7b_p = IntegerField('7b+', render_kw={"placeholder": "0"}, default=4)
    r_7c = IntegerField('7c', render_kw={"placeholder": "0"}, default=4)
    r_7c_p = IntegerField('7c+', render_kw={"placeholder": "0"}, default=4)
    r_8a = IntegerField('8a', render_kw={"placeholder": "0"}, default=4)
    r_8a_p = IntegerField('8a+', render_kw={"placeholder": "0"}, default=4)
    r_8b = IntegerField('8b', render_kw={"placeholder": "0"}, default=4)
    r_8b_p = IntegerField('8b+', render_kw={"placeholder": "0"}, default=4)
    r_8c = IntegerField('8c', render_kw={"placeholder": "0"}, default=4)
    r_8c_p = IntegerField('8c+', render_kw={"placeholder": "0"}, default=4)
    r_9a = IntegerField('9a', render_kw={"placeholder": "0"}, default=4)
    r_9a_p = IntegerField('9a+', render_kw={"placeholder": "0"}, default=4)
    r_9b = IntegerField('9b', render_kw={"placeholder": "0"}, default=4)
    r_9b_p = IntegerField('9b+', render_kw={"placeholder": "0"}, default=4)
    r_9c = IntegerField('9c', render_kw={"placeholder": "0"}, default=4)
    submit = SubmitField('Add Destination!')


class EditDestinationForm(FlaskForm):
    title = StringField('Destination title', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    discipline = SelectField('Main discipline', choices=[(
        'traditional', 'Traditional'), ('bouldering', 'Bouldering'), ('sport', 'Sport')], validators=[DataRequired()])
    image = FileField('Destination Photo', validators=[FileRequired(), FileAllowed(images, 'Images only!')])
    submit = SubmitField('Update')
