import requests
from flask import (json, jsonify, make_response,
                   render_template, request)
from sqlalchemy import and_, or_, true  # , false

from app import app
from app.forms import CurrencyForm
from app.models import (Accomodation, Car, Cost,
                        Destination, Months, Routes, User)

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


@app.route('/vote')
def vote():
    return """Här kan man rösta på vilka destinationer som ska läggas till.
              Man kan lägga till en destination eller upvota.
              Bonus: Man kan också kommentera på varje destination."""