import pandas as pd
import numpy as np

def acumtag(data):
	data['dif'] = ''
	negative_acum = 0
	positive_acum = 0
	max_negative_acum = 0
	max_positive_acum = 0

	positive = True
	actual = data['Close'][0]
	size = data.shape[0]
	

	for i in range(1, size) :
		if positive:
			data['dif'][i] = data['Close'][i] - data['Close'][i-1]
			actual = actual + data['dif'][i]			
			if data['Close'][i] - data['Close'][i-1] > 0: 
				max_positive_acum = max([actual, max_positive_acum])
			else:
				positive = False
				actual = data['Close'][i] - data['Close'][i-1]
				data['dif'][i] = actual
				max_negative_acum = min([actual, max_negative_acum])

		else:
			data['dif'][i] = data['Close'][i] - data['Close'][i-1]
			actual = actual + data['dif'][i]
			if data['Close'][i] - data['Close'][i-1] < 0: 
				max_negative_acum = min([actual, max_negative_acum])
			else:
				positive = True
				actual = data['Close'][i] - data['Close'][i-1]
				data['dif'][i] = actual
				max_positive_acum = max([actual, max_positive_acum])
	
	print(max_negative_acum)
	print(max_positive_acum)
	print(data)

df = pd.read_csv('../Data/SAN.csv')
acumtag(df[['Close']])

vector = [1,2,3,4,5]

vector2 = [f(x) for x in vector]


