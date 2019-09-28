import requests
from flask import jsonify, make_response, request

from app.currency import bp


@bp.route('/_convert_currency')
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
