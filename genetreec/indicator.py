import pandas as pd
import talib

# Datos iniciales
df = pd.read_csv('tagged_data/SAN.csv')

# Instanciar datos sobres los que calcular los indicadores
def setData(data):
	global df
	df = data

# Seleccionar valor de un indicador en una fecha concreta
def getValueByIndex(index, func):
	return func.getValues()[df['Date']==index]


# Interfaz sobre la que se van a construir los indicadores
#   getValues(): devuelve el valor del indicador en los datos seleccionados
#					Si los valores ya fueron calculados, no los calcula de nuevo,
#					los coge de df
#   name():      devuelve el nombre del indicador
#	calculate(): devuelve el valor del indicador en los datos seleccionados
# 					Añade los valores a los df
class _indicator:
	def getValues(self):
		if self.name() in df.columns.values:
			data = pd.DataFrame()
			data['values'] = df[self.name()]
			data['tag'] = df['tag']
			return data

		else:
			return self.calculate()

	def name(self):
		raise NotImplementedError

	def calculate(self):
		raise NotImplementedError





class _MACD(_indicator):

	def __init__(self, lowday=5, highday=10):
		self.lowday = lowday
		self.highday = highday

	def name(self):
		return 'MACD_' + str(self.lowday) + '_' + str(self.highday)

	def calculate(self):
		data = pd.DataFrame()
		data['values'] = talib.MACD(df['Close'],
				self.lowday,
				self.highday)[0]
		df[self.name()] = data['values']
		data['tag'] = df['tag']
		return data

class _ATR(_indicator):

	def __init__(self, period=7):
		self.period = period

	def name(self):
		return 'ATR_' + str(self.period)

	def calculate(self):
		data = pd.DataFrame()
		data['values'] = talib.ATR(df['High'],
							df['Low'],
							df['Close'],
							self.period)
		df[self.name()] = data['values']
		data['tag'] = df['tag']
		return data


class _ROC(_indicator):

	def __init__(self, period=7):
		self.period = period

	def name(self):
		return 'ROC_' + str(self.period)

	def calculate(self):
		data = pd.DataFrame()
		data['values'] = talib.ROC(df['Close'],
							self.period)
		df[self.name()] = data['values']
		data['tag'] = df['tag']
		return data


class _EMA(_indicator):

	def __init__(self, period=10):
		self.period = period

	def name(self):
		return 'EMA_' + str(self.period)

	def calculate(self):
		data = pd.DataFrame()
		data['values'] = talib.EMA(df['Close'],
							self.period)
		df[self.name()] = data['values']
		data['tag'] = df['tag']
		return data


class _SMA(_indicator):

	def __init__(self, period=10):
		self.period = period

	def name(self):
		return 'SMA_' + str(self.period)

	def calculate(self):
		data = pd.DataFrame()
		data['values'] = talib.SMA(df['Close'],
							self.period)
		df[self.name()] = data['values']
		data['tag'] = df['tag']
		return data


class _OBV(_indicator):

	def __init__(self):
		a = None

	def name(self):
		return 'OBV'

	def calculate(self):
		data = pd.DataFrame()
		data['values'] = talib.OBV(df['Close'],
							df['Volume'])
		df[self.name()] = data['values']
		data['tag'] = df['tag']
		return data


class _AD(_indicator):

	def __init__(self):
		a = None

	def name(self):
		return 'AD'

	def calculate(self):
		data = pd.DataFrame()
		data['values'] = talib.AD(df['High'],
							df['Low'],
							df['Close'],
							df['Volume'])
		df[self.name()] = data['values']
		data['tag'] = df['tag']
		return data


class _TRANGE(_indicator):

	def __init__(self):
		a = None

	def name(self):
		return 'TRANGE'

	def calculate(self):
		data = pd.DataFrame()
		data['values'] = talib.TRANGE(df['High'],
							df['Low'],
							df['Close'])
		df[self.name()] = data['values']
		data['tag'] = df['tag']
		return data


class _BBANDS_lambda_high(_indicator):

	def __init__(self, period=5, nbdevup=2, nbdevdn=2):
		self.period = period
		self.nbdevup = nbdevup
		self.nbdevdn = nbdevdn

	def name(self):
		return 'BBANDS_lambda_high_' + str(self.period) + '_' + str(self.nbdevup) + '_' + str(self.nbdevdn)

	def calculate(self):
		data = pd.DataFrame()
		(data['upperband'],data['middleband'],data['lowerband']) = talib.BBANDS(df['Close'],
									self.period,
									self.nbdevup,
									self.nbdevdn)
		data['values'] = (df['High'] - data['upperband']) / (data['lowerband'] - data['upperband'])
		data = data.drop(columns=['upperband','lowerband', 'middleband'])
		df[self.name()] = data['values']
		data['tag'] = df['tag']
		return data


class _BBANDS_lambda_low(_indicator):

	def __init__(self, period=5, nbdevup=2, nbdevdn=2):
		self.period = period
		self.nbdevup = nbdevup
		self.nbdevdn = nbdevdn

	def name(self):
		return 'BBANDS_lambda_low_' + str(self.period) + '_' + str(self.nbdevup) + '_' + str(self.nbdevdn)

	def calculate(self):
		data = pd.DataFrame()
		(data['upperband'],data['middleband'],data['lowerband']) = talib.BBANDS(df['Close'],
									self.period,
									self.nbdevup,
									self.nbdevdn)
		data['values'] = (df['Low'] - data['upperband']) / (data['lowerband'] - data['upperband'])
		data = data.drop(columns=['upperband','lowerband', 'middleband'])
		df[self.name()] = data['values']
		data['tag'] = df['tag']
		return data


# Función que devuelve una lista con todos los indicadores
def indivector():
	return [_MACD(),
			_ATR(),
			_ROC(),
			_EMA(),
			_SMA(),
			_OBV(),
			_AD(),
			_TRANGE(),
			_BBANDS_lambda_high(),
			_BBANDS_lambda_low()]
