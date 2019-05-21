from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login
from flask_login import UserMixin
from time import time
import jwt
from app import app


# En Class för varje table i databasen
class User(UserMixin, db.Model):
    # UserMixin is a class that includes the required items is_authenticated, is_active, is_anonymous, get_id(), etc.
    # db.Model provides database methods/functions, for example: User.query.get(#)
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:  # noqa: E722
            return
        return User.query.get(id)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    displayname = db.Column(db.String(64), index=True)
    location = db.Column(db.String(64), index=True)
    bio = db.Column(db.String(280))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    destinations = db.relationship('Destination', backref='author', lazy='dynamic')
    # lazy='dynamic' returns object instead of list

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)  # sets the variable password_hash above

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader  # for flask_login, user for example for current_user to get the current user object
def load_user(id):
    return User.query.get(int(id))


class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True, unique=True)
    country = db.Column(db.String(64), index=True)
    continent = db.Column(db.String(64), index=True)
    # discipline = db.Column(db.String(64), index=True)
    weather_ltd = db.Column(db.Integer)
    weather_lng = db.Column(db.Integer)
    featured_photo_filename = db.Column(db.String(64))
    featured_photo_url = db.Column(db.String(256))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # user.id refers to table user, column id
    additional_photos = db.relationship('AdditionalPhotos', backref='destination', lazy='dynamic')
    routes = db.relationship('Routes', backref='destination', lazy='dynamic')
    # lazy='dynamic' returns object instead of list
    cost = db.relationship('Cost', backref='destination', lazy='dynamic')
    accomodation = db.relationship('Accomodation', backref='destination', lazy='dynamic')
    months = db.relationship('Months', backref='destination', lazy='dynamic')
    approach = db.relationship('Approach', backref='destination', lazy='dynamic')
    car = db.relationship('Car', backref='destination', lazy='dynamic')

    def __repr__(self):
        return '<Destination {}>'.format(self.title)


class AdditionalPhotos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    additional_photo_filename = db.Column(db.String(64))
    additional_photo_url = db.Column(db.String(256))
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), index=True)


class Routes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    traditional = db.Column(db.Boolean, index=True, default=False)
    sport = db.Column(db.Boolean, index=True, default=False)
    bouldering = db.Column(db.Boolean, index=True, default=False)
    main_discipline = db.Column(db.String(64), index=True)
    easy_routes = db.Column(db.Float, index=True, default=0)
    intermediate_routes = db.Column(db.Float, index=True, default=0)
    hard_routes = db.Column(db.Float, index=True, default=0)
    very_hard_routes = db.Column(db.Float, index=True, default=0)
    total_routes = db.Column(db.Integer, index=True, default=0)
    total_trad = db.Column(db.Integer, index=True, default=0)
    total_sport = db.Column(db.Integer, index=True, default=0)
    total_boulders = db.Column(db.Integer, index=True, default=0)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), index=True)


class Cost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cost_form_currency = db.Column(db.String(32))
    beer_at_establishment = db.Column(db.Float, index=True, default=0)
    coffee_at_establishment = db.Column(db.Float, index=True, default=0)
    restaurant_inexpensive_meal = db.Column(db.Float, index=True, default=0)
    groceries_one_week = db.Column(db.Float, index=True, default=0)
    car_rent_one_week = db.Column(db.Float, index=True, default=0)
    gas_one_liter = db.Column(db.Float, index=True, default=0)
    km_per_day = db.Column(db.Float, index=True, default=0)
    tent_per_day = db.Column(db.Float, index=True, default=0)
    van_per_day = db.Column(db.Float, index=True, default=0)
    camping_per_day = db.Column(db.Float, index=True, default=0)
    hostel_per_day = db.Column(db.Float, index=True, default=0)
    apartment_per_day = db.Column(db.Float, index=True, default=0)
    house_per_day = db.Column(db.Float, index=True, default=0)
    hotel_per_day = db.Column(db.Float, index=True, default=0)
    accomodation_used_for_avg_weekly_cost = db.Column(db.String, index=True)
    avg_weekly_cost = db.Column(db.Float, index=True, default=0)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), index=True)


class Months(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    january = db.Column(db.Boolean, index=True, default=False)
    february = db.Column(db.Boolean, index=True, default=False)
    mars = db.Column(db.Boolean, index=True, default=False)
    april = db.Column(db.Boolean, index=True, default=False)
    may = db.Column(db.Boolean, index=True, default=False)
    june = db.Column(db.Boolean, index=True, default=False)
    july = db.Column(db.Boolean, index=True, default=False)
    august = db.Column(db.Boolean, index=True, default=False)
    september = db.Column(db.Boolean, index=True, default=False)
    october = db.Column(db.Boolean, index=True, default=False)
    november = db.Column(db.Boolean, index=True, default=False)
    december = db.Column(db.Boolean, index=True, default=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), index=True)


class Accomodation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tent = db.Column(db.Boolean, index=True, default=False)
    van = db.Column(db.Boolean, index=True, default=False)
    hostel = db.Column(db.Boolean, index=True, default=False)
    camping = db.Column(db.Boolean, index=True, default=False)
    apartment = db.Column(db.Boolean, index=True, default=False)
    house = db.Column(db.Boolean, index=True, default=False)
    hotel = db.Column(db.Boolean, index=True, default=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), index=True)


class Approach(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    easy = db.Column(db.Boolean, index=True, default=False)
    moderate = db.Column(db.Boolean, index=True, default=False)
    hardcore = db.Column(db.Boolean, index=True, default=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), index=True)


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    not_needed = db.Column(db.Boolean, index=True, default=False)
    good_to_have = db.Column(db.Boolean, index=True, default=False)
    must_have = db.Column(db.Boolean, index=True, default=False)
    rent_scooter_locally = db.Column(db.Boolean, index=True, default=False)
    rent_car_locally = db.Column(db.Boolean, index=True, default=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), index=True)
