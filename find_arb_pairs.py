import asyncio
import os
import sys
import time
import json
import hmac
import hashlib
from urllib.parse import urljoin, urlencode

import requests

sys.path.append('./key')
from read_key import read_key

API_KEY,SECRET_KEY = read_key()

BASE_URL = 'https://api.binance.com'
headers = {
    'X-MBX-APIKEY': API_KEY
}


class arb_symbol_finder:
    def __init__(self, Basecur1, Basecur2):
        tmp = [Basecur1, Basecur2]
        tmp.sort()
        self.Basecur1 = tmp[0]
        self.Basecur2 = tmp[1]
        self.coin_set = self.get_coins()
        self.symbol_set = self.get_tradeble_pairs()

    def get_coins(self):
        endpoint = '/sapi/v1/capital/config/getall'
        url = BASE_URL + endpoint
        timestamp = int(time.time() * 1000)
        params = {
        'timestamp': timestamp
        }
        query_string = urlencode(params)
        params['signature'] = hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        r = requests.get(url, headers=headers, params=params)
        if r.status_code == 200:
             data = r.json()
             coins = [i['coin'] for i in data]
             
             return coins
        else:
            raise Exception("cannot call config/getall")

    def get_tradeble_pairs(self):
        endpoint = '/api/v3/exchangeInfo'
        r = requests.get(BASE_URL + endpoint)
        if r.status_code == 200:
            data = r.json()
            symbols = [i['symbol'] for i in data['symbols'] if i['status']=="TRADING"]
            return symbols
        else:
            raise Exception("cannot call exchangeInfo")

    # space = [{'PAX': ["PAXBNB", "PAXBTC"]}, ... ]


    def get_arb_pairs(self):
        arb_pairs = []
        for i, symbol in enumerate(self.symbol_set):
            if self.Basecur1 in symbol and self.Basecur2 not in symbol:
                cur = symbol.replace(self.Basecur1,'')
                #print(symbol, cur)
                for j, x in enumerate(self.symbol_set[i:]):
                    if self.Basecur2 in x and cur in x :
                        if cur in self.coin_set:
                            arb_pairs.append({ cur : [symbol, x]})
        #remove Leveraged Token:
        arb_pairs_ = []
        for i, arb_pair in enumerate(arb_pairs):
            #print(arb_pair)
            for k,v in arb_pair.items():
                if not(v[1].replace(k,'') == self.Basecur1 or v[1].replace(k,'') == self.Basecur2):
                    break
                if not(v[0].replace(k,'') == self.Basecur1 or v[0].replace(k,'') == self.Basecur2):
                    break
                arb_pairs_.append(arb_pair)
                       
        #print(arb_pairs, len(arb_pairs))
        return arb_pairs_


if __name__ == '__main__':
    #quick sanity test
    if sys.argv[1:]:
        bnbbtc = arb_symbol_finder(sys.argv[1], sys.argv[2])
        print(bnbbtc.get_arb_pairs(), len(bnbbtc.get_arb_pairs()))
    else:
        bnbbtc = arb_symbol_finder('BNB','BTC')
        print(bnbbtc.get_arb_pairs())
