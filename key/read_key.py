import os

import json


def read_key(): 
	#cwd = os.getcwd()
	f = open('{}'.format('./key/key.json'),'r')
	txt = f.read()
	f.close()
	api = json.loads(txt)
	key = api["API_Key"]
	secret = api["API_Secret"]
	return key,secret
