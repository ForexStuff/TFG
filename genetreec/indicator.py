import pandas as pd
import talib 

df = None

def minimax(data):
	data = data.fillna(data.mean())
	return (data - min(data)) / (max(data) - min(data))

class _MACD:

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
		data['tag'] = df['tag']
		return data

class _ATR:

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
		data['tag'] = df['tag']
		return data


class _ROC:

	def __init__(self, period=7):
		self.period = period

	def name(self):
		return 'ROC_' + str(self.period)

	def calculate(self):
		data = pd.DataFrame()
		data['values'] = talib.ROC(df['Close'],
							self.period)
		data['tag'] = df['tag']
		return data


class _EMA:

	def __init__(self, period=10):
		self.period = period

	def name(self):
		return 'EMA_' + str(self.period)

	def calculate(self):
		data = pd.DataFrame()
		data['values'] = talib.EMA(df['Close'],
							self.period)
		data['tag'] = df['tag']
		return data


class _SMA:

	def __init__(self, period=10):
		self.period = period

	def name(self):
		return 'SMA_' + str(self.period)

	def calculate(self):
		data = pd.DataFrame()
		data['values'] = talib.SMA(df['Close'],
							self.period)
		data['tag'] = df['tag']
		return data


class _OBV:

	def __init__(self):
		a = None		

	def name(self):
		return 'OBV'

	def calculate(self):
		data = pd.DataFrame()
		data['values'] = talib.OBV(df['Close'],
							df['Volume'])
		data['tag'] = df['tag']
		return data


class _AD:

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
		data['tag'] = df['tag']
		return data


class _TRANGE:

	def __init__(self):
		a = None

	def name(self):
		return 'TRANGE'

	def calculate(self):
		data = pd.DataFrame()
		data['values'] = talib.TRANGE(df['High'],
							df['Low'],
							df['Close'])
		data['tag'] = df['tag']
		return data


class _BBANDS_lambda_high	:

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
		data['tag'] = df['tag']
		return data


class _BBANDS_lambda_low	:

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
		data['tag'] = df['tag']
		return data

def indivector(data):
	global df 
	df = data
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
