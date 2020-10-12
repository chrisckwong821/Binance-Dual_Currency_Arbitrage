from taker_send import taker_send

# for base1 base2 currency: 
# 0 : base1cur base2cur
# 1 : curbase1 base2cur
# 2 : base1cur curbase2
# 3 : curbase1 curbase2
#pair1 < pair2 in terms of alphabets
def enum_arbpath(cur, pair1, pair2):
	if pair1.split(cur).index('') == 1 and pair2.split(cur).index('') == 1:
		return 0
	elif pair1.split(cur).index('') == 0 and pair2.split(cur).index('') == 1:
		return 1
	elif pair1.split(cur).index('') == 1 and pair2.split(cur).index('') == 0:
		return 2
	elif pair1.split(cur).index('') == 0 and pair2.split(cur).index('') == 0:
		return 3
	else:
		return -1

#helper to align new order quantity with current book quantity
def num_after_point(x):
    s = str(x)
    if not '.' in s:
        return 0
    return len(s) - s.index('.') - 1

# curdict = {'SUSHI': {'enum':3, 'SUSHIBNB' : [bidprice, bidquan, askprice, askquan], 'SUSHIBTC':[.....] }}
# main_dict = the dual currencies, {'BNBBTC': [bidprice, bidquant, askprice, askquant]}

def taker_check(cur, cur_dict, main_dict, strategy, Basecur1, Basecur2):
	arb_limit = strategy['taker']['arb_limit']
	arb_quantity_limit = strategy['taker']['arb_quantity_limit']
	env = strategy['taker']['env']

	enum = cur_dict['enum']
	#print(cur_dict)
	pairs = list(cur_dict.keys())
	pairs.remove('enum')
	pairs.sort()
	#print('pairs : ', pairs)
	try:
		base1, base2 = pairs[0], pairs[1]
	except IndexError:
		return

	
	main_pair, feed = list(main_dict.items())[0]
	#print('debugger : ', main_pair, feed)
	main_bid = float(feed[0])
	main_ask = float(feed[2])
	midprice = (main_bid + main_ask) * 0.5
	#make sure price of main_dict is quoted as b1b2, flip it if it is b2b1
	if main_pair.split(Basecur1).index('') == 1:
		midprice = 1 / midprice
		main_ask = 1 / main_ask
		main_bid = 1 / main_bid

	base1_b = float(cur_dict[base1][0])
	base1_bq = float(cur_dict[base1][1])
	base1_a = float(cur_dict[base1][2])
	base1_aq = float(cur_dict[base1][3])

	base2_b = float(cur_dict[base2][0])
	base2_bq = float(cur_dict[base2][1])
	base2_a = float(cur_dict[base2][2])
	base2_aq = float(cur_dict[base2][3])

# 0 : base1cur base2cur
	if cur_dict['enum'] == 0:
		s1b2 = (base2_a / base1_b) #sell base1, buy base2
		#apply quantity threshold in b1 form, retransform back to their original quantity
		#q1 => order 1, q2 => order 2, q3 => final main trade
		s1b2q1, s1b2q2, = base1_bq , base2_aq / main_ask
		s1b2q3 = s1b2_q = min(s1b2q1, s1b2q2, arb_quantity_limit)
		s1b2q1, s1b2q2 = s1b2_q, s1b2_q * main_ask
		#s1b2_q = min(base1_bq, base2_aq)
		ps1b2 = (s1b2 * main_ask) - 1

		# 1.00 1.001  & 1.005 1.006 & 0.999 1.001
		b1s2 = (base2_b / base1_a) #buy base1, sell base2
		b1s2q1, b1s2q2, = base1_aq, base2_bq / main_bid
		b1s2q3 = b1s2_q = min(b1s2q1, b1s2q2, arb_quantity_limit)
		b1s2q1, b1s2q2 = b1s2_q, b1s2_q * main_bid
		pb1s2 = (b1s2 * main_bid) - 1
# 1 : curbase1 base2cur
	elif cur_dict['enum'] == 1:
		s1b2 = (base1_a * base2_a) #sell base1, buy base2
		
		s1b2q1, s1b2q2, = base1_aq / base1_a, base2_aq / main_ask

		s1b2q3 = s1b2_q = min(s1b2q1, s1b2q2, arb_quantity_limit)
		s1b2q1, s1b2q2 = s1b2_q, s1b2_q * main_ask
		ps1b2 = (s1b2 / main_ask) - 1


		b1s2 = (base1_b * base2_b) #buy base1, sell base2

		b1s2q1, b1s2q2, = base1_bq / base1_b, base2_bq / main_bid

		b1s2q3 = b1s2_q = min(b1s2q1, b1s2q2, arb_quantity_limit)
		b1s2q1, b1s2q2 = b1s2_q, b1s2_q * main_bid
		pb1s2 = (b1s2 / mid_bid) - 1

# 2 : base1cur curbase2
	elif cur_dict['enum'] == 2:
		# 1.00 1.001  & 1.005 1.006 & 0.999 1.001
		s1b2 = (base1_b * base2_b) #sell base1, buy base2
		#s1b2_q = min(base1_bq, base2_bq)
		s1b2q1, s1b2q2, = base1_bq, (base2_bq * base2_b) / main_bid

		s1b2q3 = s1b2_q = min(s1b2q1, s1b2q2, arb_quantity_limit)
		s1b2q1, s1b2q2 = s1b2_q, s1b2_q * main_bid / base2_b
		ps1b2 = (s1b2 / main_bid) - 1


		b1s2 = (base1_a * base2_a) #buy base1, sell base2
		
		b1s2q1, b1s2q2, = base1_aq, (base2_aq / base2_a) / main_ask
		b1s2q3 = b1s2_q = min(b1s2q1, b1s2q2, arb_quantity_limit)
		b1s2q1, b1s2q2 = b1s2_q, b1s2_q * main_ask * base2_a
		#b1s2_q = min(base1_aq, base2_aq)
		pb1s2 = (b1s2 / main_ask) - 1
# 3 : curbase1 curbase2
	elif cur_dict['enum'] == 3:
		# 0.00099 0.001  & 0.00101 0.00102 & 0.999 1 1.001
		s1b2 = ((1 / base1_a) * base2_b) #sell base1, buy base2
		s1b2q1, s1b2q2, = base1_aq * base1_a, (base2_bq * base2_b) / main_bid

		s1b2q3 = s1b2_q = min(s1b2q1, s1b2q2, arb_quantity_limit)
		s1b2q1, s1b2q2 = s1b2_q / base1_a, s1b2_q * main_bid / base2_b
		#s1b2_q = min(base1_bq, base2_aq)
		ps1b2 = (s1b2 / main_bid) - 1
		#print('x', base1_b , base2_a, midprice, ps1b2)

		b1s2 = ((1 / base1_b) * base2_a) #buy base1, sell base2
		b1s2q1, b1s2q2, = base1_bq * base1_b, (base2_aq * base2_a) / main_ask
		b1s2q3 = b1s2_q = min(b1s2q1, b1s2q2, arb_quantity_limit)
		b1s2q1, b1s2q2 = b1s2_q / base1_b, b1s2_q * main_ask / base2_a
		#b1s2_q = min(base1_aq, base2_bq)
		pb1s2 = (b1s2 / main_ask) - 1

	def logger(ps1b2, pb1s2, arb_limit, cur_dict, s1b2q1, b1s2q1, base1_b):
		if ps1b2 > arb_limit:
			if cur_dict['enum'] == 0 or cur_dict['enum']  == 2:
				PL_b1 = round(-ps1b2 * s1b2q1 / base1_b, 3)
			else:
				PL_b1 = round(-ps1b2 * s1b2q1 * base1_b, 3)
			p_cur = base1.replace(cur,'')
			#print(enum, base1_b / base2_b * midprice, ps1b2, pb1s2)
			print('(+{})s1b2: sell {} buy {} make {}({}) {}%'.format(p_cur, base1, base2, PL_b1, Basecur1, round(-ps1b2,3)*100), round(s1b2q1,3))
			
		if pb1s2 < -arb_limit:
			if cur_dict['enum'] == 0 or cur_dict['enum']  == 2:
				PL_b1 = round(-pb1s2 * b1s2q1 / base1_b, 3) * 100
			else:
				PL_b1 = round(-pb1s2 * b1s2q1 * base1_b, 3) * 100
			p_cur = base2.replace(cur,'')
			print('(+{})b1s2: buy {} sell {} make {}({}) {}%'.format(p_cur, base1, base2, PL_b1, Basecur1, round(-pb1s2,3)*100), round(b1s2q1,3))
	# in production, should pass to order sender
	#print('arb_compaire:', base1, base2, "sell at (+)", round(ps1b2 * 100,2), 'buy from (-)',round(pb1s2 * 100,2))
	if env == "DEMO":
		logger(ps1b2, pb1s2, arb_limit, cur_dict, s1b2q1, b1s2q1, base1_b)

	if env == 'LIVE':
		if ps1b2 > arb_limit:
			print('s1b2q2 before ',base2 , s1b2q2, base1_bq)
			s1b2q1 = round(s1b2q1, num_after_point(base1_bq))
			s1b2q2 = round(s1b2q2, num_after_point(base2_bq))
			s1b2q3 = round(s1b2q3, num_after_point(float(feed[1]))) #feed[1] is bid quantity in main_pair
			print('s1b2q2 after ', base2, s1b2q2)
			orders = []
			#append according to execution sequence
			if cur_dict['enum'] == 0:
				orders.append(['SELL',base1, s1b2q1])
				orders.append(['BUY', base2, s1b2q2]) 
			elif cur_dict['enum'] == 1:
				orders.append(['SELL', base2, s1b2q2])
				orders.append(['SELL', base1, s1b2q1])
			elif cur_dict['enum'] == 2:
				orders.append(['BUY', base2, s1b2q2])
				orders.append(['BUY', base1, s1b2q1]) 
			elif cur_dict['enum'] == 3:
				orders.append(['BUY', base1, s1b2q1])
				orders.append(['SELL', base2, s1b2q2])
			orders.append(['BUY', main_pair, s1b2q3])
			print(orders)
			taker_send(orders)

		# basically reverse of ps1b2
		if pb1s2 < -arb_limit:
			b1s2q1 = round(b1s2q1, num_after_point(base1_bq))
			b1s2q2 = round(b1s2q2, num_after_point(base2_bq))
			b1s2q3 = round(b1s2q3, num_after_point(float(feed[1]))) #feed[1] is bid quantity in main_pair
			orders = []
			if cur_dict['enum'] == 0:
				orders.append(['SELL', base2, b1s2q2]) 
				orders.append(['BUY',base1, b1s2q1])
			elif cur_dict['enum'] == 1:
				orders.append(['BUY', base1, b1s2q1])
				orders.append(['BUY', base2, b1s2q2]) 
			elif cur_dict['enum'] == 2:
				orders.append(['SELL', base1, b1s2q1])
				orders.append(['SELL', base2, b1s2q2])
			elif cur_dict['enum'] == 3:
				orders.append(['BUY', base2, b1s2q2]) 
				orders.append(['SELL',base1, b1s2q1])
			orders.append(['SELL', main_pair, b1s2q3])
			print(orders)
			taker_send(orders)

	
