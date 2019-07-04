import pandas as pd
import numpy as np
import talib
import math
from pandas_datareader import data as pdr

def acumtag():
	data = pdr.get_data_yahoo("SAN", start="2017-01-01", end="2019-03-30")
	data['dif'] = talib.MOM(data['Close'],1)  # Calculate the difference with last day
	data['dif'][0] = -0.01
	data_tag = [0] * data.shape[0]

	negative_acum = 0
	positive_acum = 0
	max_negative_acum = 0
	max_positive_acum = 0

	positive = True

	# Taking the max positive and negative diference consecutive
	for dif in data['dif']:
		if positive: # Crescent Trend
			if dif > 0: # If still crescent sum acumulation
				positive_acum += dif
			else:   # If started decrescent save the acumulation
				max_positive_acum = max(positive_acum, max_positive_acum)
				negative_acum = dif
				positive = False

		else:      # Descendent Trend
			if dif < 0: # If still decrescent sum acumulation
				negative_acum += dif
			else: # If started crescent save the acumulation
				max_negative_acum = min(negative_acum, max_negative_acum)
				positive_acum = dif
				positive = True


	positive = False
	negative_acum = 0
	positive_acum = 0
	ichange = 0
	max_negative_acum = (max_negative_acum)/6		# The trend is considered to change when the rupture
	max_positive_acum = (max_positive_acum)/6		# is greater than 1/6 of the max trend


	for dif,i in zip(data['dif'],list(range(0,data.shape[0]))):
		if positive:
			data_tag[i] = 1 #Tag 1 if crescent
			if dif < 0:
				if negative_acum == 0:    # Rectification
					ichange = i-1
				negative_acum += dif
				if negative_acum < max_negative_acum:  # Limit of rectification trespassed - TAG 2 for the last max
					data_tag[ichange:i+1] = [-1]*(i-ichange+1) # Retag all the rectification days - TAG -1 for decrescent
					data_tag[ichange] = 2
					positive = False
					positive_acum = 0
					ichange = i+1
			else:
				negative_acum += dif
				if negative_acum > 0:
					negative_acum = 0
				if negative_acum == 0:
					ichange = i
		else:
			data_tag[i] = -1 #Tag -1 if decrescent
			if dif > 0:
				if positive_acum == 0:  # Rectification
					ichange = i-1
				positive_acum += dif
				if positive_acum > max_positive_acum: # Limit of rectification trespassed - TAG -2 for the last min
					data_tag[ichange:i+1] = [1]*(i-ichange+1) # Retag all the rectification days - TAG -1 for decrescent
					data_tag[ichange] = -2
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
	#print('max_neg_acum:' + str(max_negative_acum) + ' max_pos_acum:' + str(max_positive_acum))
	data.to_csv("tagged_data/SAN.csv")
acumtag()
