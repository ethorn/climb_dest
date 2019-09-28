from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField


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
