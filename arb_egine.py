
import sys
import json
import websocket #install websocket-client
from subscribe import subscriber
from enum_arbpath import enum_arbpath, taker_check

import threading

import traceback

env = "DEMO"
	# arb_limit in standard unit(0.01 = 1%), arb_quantity_limit (in main_pair) 1 for BNBBTC = 1 BNB:
strategy = {'taker':
				{'arb_limit': 0.01, 'arb_quantity_limit' : 0.4, 'env': 'DEMO'}
			}

class arb_engine(subscriber):
	def __init__(self, strategy=None, *args, **kwargs):
		super(arb_engine, self).__init__(*args, **kwargs) 

		self.strategy = strategy

		self.main_dict = dict() #base1base2 rate
		self.aggregator = dict()
		#override
		self.callback = self.message_handler
		
		

	def init(self):
		for cur_dict in self.symbols_group:
			cur = cur_dict.keys()
			cur, pairs = list(cur_dict.items())[0]
			#alphabet sorting of two pairs 
			pairs.sort()
			#print(cur, value)
			self.aggregator[cur] = dict()
			self.aggregator[cur]['enum'] = enum_arbpath(cur, pairs[0], pairs[1])
			#print(cur, pairs[0], pairs[1], self.aggregator[cur]['enum'])

		 #eg :stream : UNIBTC, 10000, 100001
	def update_bidask(self, stream, b_bid, b_ask, bid_depth_ratio):
		if stream.replace(self.Basecur1, '').replace(self.Basecur2, '') == '':
			self.main_dict[stream] = b_bid + b_ask
			return 1
		if len(self.main_dict) < 1:
			return -1

		mask = stream.replace(self.Basecur1,'')
		if  mask == stream:
			cur = stream.replace(self.Basecur2,'')
		else: cur = mask

		self.aggregator[cur][stream] = b_bid + b_ask + [bid_depth_ratio]# [bid, bquant, ask, aquant, depth_ratio(bid)]

		cur_dict = self.aggregator[cur]
		
		#checker(cur, cur_dict, self.main_dict, self.arb_limit, self.Basecur1, self.Basecur2, 'DEMO')
		taker = threading.Thread(target=taker_check, args=(cur, cur_dict, self.main_dict, self.strategy, self.Basecur1, self.Basecur2))
		taker.start()

		#maker = threading.Thread(target=maker_check, args=(cur, cur_dict, self.main_dict, self.arb_limit, self.Basecur1, self.Basecur2, 'DEMO'))
		#maker.start()
		
	def message_handler(self, message):
		feed = json.loads(message)
		#print(feed)
		stream = feed['stream'].replace(self.mode,'').upper() #self.mode = '@depth5@100ms' 

		b_ask = feed['data']['asks'][0]
		b_bid = feed['data']['bids'][0]

		asks_quantity = sum([float(i[1]) for i in feed['data']['asks']])
		bids_quantity = sum([float(i[1]) for i in feed['data']['bids']])
		bid_depth_ratio = bids_quantity / asks_quantity
		#print('bid ratio', bid_depth_ratio)
		#print(stream, b_bid, b_ask, bid_depth_ratio)
		self.update_bidask(stream, b_bid, b_ask, bid_depth_ratio)



if __name__ == '__main__':
#quick sanity test
	if sys.argv[1:]:
		arb_engine = arb_engine(sys.argv[1], sys.argv[2],strategy=strategy)
		arb_engine.init()
		arb_engine.start()
	else:
		#subscriber = subscriber('BNB', 'BTC', print)	
		arb_engine = arb_engine(Basecur1='BNB', Basecur2='BTC',strategy=strategy)
		arb_engine.init()
		arb_engine.start()
