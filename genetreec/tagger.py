import pandas as pd
import numpy as np
import talib
import math

def acumtag(data):
	print(data.shape)
	data['dif'] = talib.MOM(data['Close'],1)
	data['dif'][0] = -0.01
	data_tag = [0] * data.shape[0]

	negative_acum = 0
	positive_acum = 0
	max_negative_acum = 0
	max_positive_acum = 0

	positive = True
	
	# Taking the max positive and negative diference consecutive 
	for dif in data['dif']:
		if positive:
			if dif > 0:
				positive_acum += dif
			else:
				max_positive_acum = max(positive_acum, max_positive_acum)
				negative_acum = dif
				positive = False
					
		else:
			if dif < 0:
				negative_acum += dif
			else:
				max_negative_acum = min(negative_acum, max_negative_acum)
				positive_acum = dif
				positive = True


	positive = False
	negative_acum = 0
	positive_acum = 0
	ichange = 0
	max_negative_acum = (-max_negative_acum)/6
	max_positive_acum = (max_positive_acum)	/6


	for dif,i in zip(data['dif'],list(range(0,data.shape[0]))): 
		if positive:
			if dif < 0:
				negative_acum += dif
				if negative_acum < max_negative_acum:
					data_tag[ichange] = 1 #sell
					positive = False
					positive_acum = 0
					ichange = i+1
			else:
				negative_acum += dif
				if negative_acum > 0 :
					negative_acum = 0
				if negative_acum == 0:
					ichange = i
		else:
			if dif > 0:
				positive_acum += dif
				if positive_acum > max_positive_acum:
					print(i)
					data_tag[ichange] = -1 #buy
					positive = True
					negative_acum = 0
					ichange = i+1
			else:
				positive_acum += dif
				if positive_acum < 0 :
					positive_acum = 0
				if positive_acum == 0:
					ichange = i
					
	data['tag'] = data_tag
	print('max_neg_acum:' + str(max_negative_acum) + ' max_pos_acum:' + str(max_positive_acum))
	np.set_printoptions(threshold=0)
	print(data)


df = pd.read_csv('../Data/SAN.csv')
acumtag(df)


