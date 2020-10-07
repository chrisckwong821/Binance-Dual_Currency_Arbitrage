


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


# curdict = {'SUSHI': {'enum':3, 'SUSHIBNB' : [bidprice, bidquan, askprice, askquan], 'SUSHIBTC':[.....] }}
# main_dict = the dual currencies, {'BNBBTC': [bidprice, bidquant, askprice, askquant]}
def checker(cur, cur_dict, main_dict, arb_limit, Basecur1, Basecur2, env):
	enum = cur_dict['enum']
	#print(cur_dict)
	pairs = list(cur_dict.keys())
	pairs.remove('enum')
	pairs.sort()
	#print(cur_dict)

	base1, base2 = pairs[0], pairs[1]

	
	main_pair, feed = list(main_dict.items())[0]
	#print('debugger : ', main_pair, feed)
	midprice = (float(feed[0]) + float(feed[2])) * 0.5
	#make sure price of main_dict is quoted as b1b2, flip it if it is b2b1
	if main_pair.split(Basecur1).index('') == 1:
		midprice /= midprice

	base1_b = float(cur_dict[base1][0])
	base1_bq = float(cur_dict[base1][1])
	base1_a = float(cur_dict[base1][2])
	base1_aq = float(cur_dict[base1][3])

	base2_b = float(cur_dict[base2][0])
	base2_bq = float(cur_dict[base2][1])
	base2_a = float(cur_dict[base2][2])
	base2_aq = float(cur_dict[base2][3])

	if cur_dict['enum'] == 0:
		s1b2 = (base1_b / base2_a) #sell base1, buy base2
		s1b2_q = min(base1_bq, base2_aq)
		ps1b2 = (s1b2 / midprice) - 1

		b1s2 = (base1_a / base2_b) #buy base1, sell base2
		b1s2_q = min(base1_aq, base2_bq)
		pb1s2 = (b1s2 / midprice) - 1

	elif cur_dict['enum'] == 1:
		s1b2 = (base1_b * base2_a) #sell base1, buy base2
		s1b2_q = min(base1_bq, base2_aq)
		ps1b2 = (s1b2 * midprice) - 1

		b1s2 = (base1_a * base2_b) #buy base1, sell base2
		b1s2_q = min(base1_aq, base2_bq)
		pb1s2 = (b1s2 * midprice) - 1

	elif cur_dict['enum'] == 2:
		s1b2 = (base1_b * base2_a) #sell base1, buy base2
		s1b2_q = min(base1_bq, base2_aq)
		ps1b2 = (s1b2 / midprice) - 1

		b1s2 = (base1_a * base2_b) #buy base1, sell base2
		b1s2_q = min(base1_aq, base2_bq)
		pb1s2 = (b1s2 / midprice) - 1

	elif cur_dict['enum'] == 3:
		
		s1b2 = (base1_b / base2_a) #sell base1, buy base2
		s1b2_q = min(base1_bq, base2_aq)
		ps1b2 = (s1b2 * midprice) - 1
		#print('x', base1_b , base2_a, midprice, ps1b2)

		b1s2 = (base1_a / base2_b) #buy base1, sell base2
		b1s2_q = min(base1_aq, base2_bq)
		pb1s2 = (b1s2 * midprice) - 1
	else:
		pass

	def logger(ps1b2, pb1s2, arb_limit, cur_dict, s1b2_q, b1s2_q, base1_b):
		if ps1b2 < arb_limit:
			if cur_dict['enum'] == 0 or cur_dict['enum']  == 2:
				PL_b1 = round(-ps1b2 * s1b2_q / base1_b, 3)
			else:
				PL_b1 = round(-ps1b2 * s1b2_q * base1_b, 3)
			p_cur = base1.replace(cur,'')
			#print(enum, base1_b / base2_b * midprice, ps1b2, pb1s2)
			print('(+{})s1b2: sell {} buy {} make {}({})'.format(p_cur, base1, base2, PL_b1, Basecur1), round(-ps1b2,3), round(s1b2_q,3))
			
		if pb1s2 < arb_limit:
			if cur_dict['enum'] == 0 or cur_dict['enum']  == 2:
				PL_b1 = round(-pb1s2 * b1s2_q / base1_b, 3)
			else:
				PL_b1 = round(-pb1s2 * b1s2_q * base1_b, 3)
			p_cur = base2.replace(cur,'')
			print('(+{})s1b2: buy {} sell {} make {}({})'.format(p_cur, base1, base2, PL_b1, Basecur1), round(-pb1s2,3), round(b1s2_q,3))
	
	# if pass arb threshold / printer function 
	# in production, should pass to order sender
	if env == "DEMO":
		logger(ps1b2, pb1s2, arb_limit, cur_dict, s1b2_q, b1s2_q, base1_b)
	if env == "LIVE":
		send_order(ps1b2, pb1s2, arb_limit, cur_dict, s1b2_q, b1s2_q, base1_b)
	

	