import sys
import time
import json
import hmac
import hashlib
import requests

from urllib.parse import urljoin, urlencode

from read_key import read_key

class BinanceException(Exception):
    def __init__(self, status_code, data):
        self.status_code = status_code
        if data:
            self.code = data['code']
            self.msg = data['msg']
        else:
            self.code = None
            self.msg = None
        message = f"{status_code} [{self.code}] {self.msg}"
        print(message)

def taker_send(orders):
    # create and fire three orders in order
    for order in orders:
        side = order[0]
        symbol = order[1]
        quantity = order[2]
        create_order(symbol, 'market', side, quantity)
        print('EXECUTED : ', side, symbol, quantity)

def create_order(symbol, order_type, side, quantity):
    BASE_URL = 'https://api.binance.com'
    PATH = '/api/v3/order'

    API_KEY,SECRET_KEY = read_key()

    headers = {
        'X-MBX-APIKEY': API_KEY
    }   

    timestamp = int(time.time() * 1000)

    params = {
        'side' : side,
        'symbol': symbol,
        'quantity': quantity,
        'type': order_type,
        #'recvWindow': 5000,
        'timestamp': timestamp
    }

    query_string = urlencode(params)
    params['signature'] = hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    url = urljoin(BASE_URL, PATH)
    r = requests.post(url, headers=headers, params=params)
    #print(query_string)
    print(params)
    if r.status_code == 200:
        data = r.json()
        print(json.dumps(data, indent=2))
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())
