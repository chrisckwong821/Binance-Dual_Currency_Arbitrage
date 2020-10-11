import json
import websocket #install websocket-client
import sys
from find_arb_pairs import arb_symbol_finder

 # for > 1 stream
#socket = 'wss://stream.binance.com:9443/ws' # for single stream

class subscriber(object):
    def __init__(self, Basecur1, Basecur2, callback=None, target_currency=None, maker_only=False, *args, **kwargs):
        self.socket = 'wss://stream.binance.com:9443/stream?streams='
        self.mode = '@depth20@100ms'
        self.Basecur1 = Basecur1
        self.Basecur2 = Basecur2
        self.maker_only = maker_only

        self.callback = callback
        self.target_currency = target_currency
        self.symbols_group = arb_symbol_finder(self.Basecur1, self.Basecur2).get_arb_pairs()
        self.subscribe_message = self.compose_params()
        self.ws = websocket.WebSocketApp(self.socket, on_open=lambda ws: self.on_open(ws), on_message=lambda ws,msg: self.on_message(ws, msg, callback), on_close=lambda ws: self.on_close(ws))
        

    # need  target currency(ies) to try making market// make target currency a list
    def get_maker_pairs(self):
        space = self.symbols_group
        result = []
        if self.target_currency is None:
            pass
        else:
            target_cur_space = [i for i in space if self.target_currency in i.keys()]
            result += target_cur_space
        return result
            
    def compose_params(self):
        all_symbols = []
        if self.target_currency is not None and self.maker_only:
            space = self.get_maker_pairs()
        else:
            space = self.symbols_group
            
        for arb_pair in space:
            print(arb_pair)
            for _,  v in arb_pair.items():
                all_symbols.append(v[0].lower())
                all_symbols.append(v[1].lower())


        params = [i + self.mode for i in all_symbols]
        # append the main_pair basecur1 + basecur2
        params.append(self.Basecur1.lower() + self.Basecur2.lower() + self.mode)
        
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": params,
             "id": 1
             }

        return subscribe_message

    def export_toconfig(self):
        tmp = {"Basecur1": self.Basecur1, "Basecur2": self.Basecur2, "Arb_Space": self.symbols_group}
        f = open("config.json",'w')
        json.dump(tmp, f)

    def start(self):
        self.export_toconfig()
        self.ws.run_forever()

    def on_open(self, ws):
        print("opened")
        print(self.subscribe_message)
        ws.send(json.dumps(self.subscribe_message))

    def on_message(self, ws, message, callback):
        #print("received a message")
        self.callback(message)

    def on_close(self, ws):
        print("closed connection")        

def printer(message):
    print('testing printer func')
    print(message)


if __name__ == '__main__':
    #quick sanity test
    if sys.argv[1:]:
        subscriber = subscriber(sys.argv[1], sys.argv[2], callback=printer)
        subscriber.start()
    else:
        subscriber = subscriber('BNB', 'BTC', callback=printer)
        subscriber.start()
    
