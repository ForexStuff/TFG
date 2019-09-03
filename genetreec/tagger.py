import pandas as pd
import numpy as np
import talib
import math
from pandas_datareader import data as pdr

def acumtag(start_date, end_date, symbol):
	data = pdr.get_data_yahoo(symbol, start=start_date, end=end_date)
	data['dif'] = talib.MOM(data['Close'],1)  # Calcula la diferencia con el dia anterior
	data['dif'][0] = -0.01
	data_tag = [0] * data.shape[0]

	negative_acum = 0
	positive_acum = 0
	max_negative_acum = 0
	max_positive_acum = 0

	positive = True

	# Calcular la maxima subida y la maxima bajada consecutivas
	for dif in data['dif']:
		if positive: # Tendencia creciente
			if dif > 0: # Si todavia es creciente, suma la subida
				positive_acum += dif
			else:   #     Si comienza una bajada, cambia de contador
				max_positive_acum = max(positive_acum, max_positive_acum)
				negative_acum = dif
				positive = False

		else:      # Tendencia decreciente
			if dif < 0: # Si todavia es decreciente, suma la bajada
				negative_acum += dif
			else: #       Si comienza una subida, cambia de contador
				max_negative_acum = min(negative_acum, max_negative_acum)
				positive_acum = dif
				positive = True


	positive = False
	negative_acum = 0
	positive_acum = 0
	ichange = 0
	max_negative_acum = (max_negative_acum)/6		# Se considera una ruptura de tendencia si
	max_positive_acum = (max_positive_acum)/6		# si el cambio es mayor de 1/6 la maxima tendencia

	for dif,i in zip(data['dif'],list(range(0,data.shape[0]))):
		if positive:
			data_tag[i] = 1 #Tag 1 if crescent
			if dif < 0:
				if negative_acum == 0:    # Rectificacion
					ichange = i-1
				negative_acum += dif
				if negative_acum < max_negative_acum:  # Limite de rectificacion traspasado - TAG 2 para el ultimo positivo
					data_tag[ichange:i+1] = [-1]*(i-ichange+1) # Volver a etiquetar los anteriores - TAG -1
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
				if positive_acum == 0:  # Rectificacion
					ichange = i-1
				positive_acum += dif
				if positive_acum > max_positive_acum: # Limite de rectificacion traspasado - TAG -2 para el minimo
					data_tag[ichange:i+1] = [1]*(i-ichange+1) # Volver a etiquetar por la rectificacion - TAG -1
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
	data.to_csv("tagged_data/"+ symbol + ".csv")
