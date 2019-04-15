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
							timeperiod=10)
		data['tag'] = df['tag']
		return data



def indivector(data):
	global df 
	df = data
	return [_MACD(), 
			_ATR(),
			_ROC()]



