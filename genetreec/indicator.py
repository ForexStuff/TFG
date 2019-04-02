import pandas as pd
import talib 


def minimax(data):
	data = data.fillna(data.mean())
	return (data - min(data)) / (max(data) - min(data))

class _MACD:

	def __init__(self, df, lowday=5, highday=10):
		self.df = df
		self.lowday = lowday
		self.highday = highday	

	def name(self):
		return 'MACD_' + str(self.lowday) + '_' + str(self.highday) 

	def calculate(self):
		data = pd.DataFrame()
		data['values'] = minimax(talib.MACD(self.df['Close'], 
				self.lowday, 
				self.highday)[0])
		data['tag'] = self.df['tag']
		return data

class _ATR:

	def __init__(self, df, period=7):
		self.df = df
		self.period = period

	def name(self):
		return 'ATR_' + str(self.period)

	def calculate(self):
		data = pd.DataFrame()
		data['values'] = minimax(talib.ATR(self.df['High'],
							self.df['Low'], 
							self.df['Close'], 
							self.period))
		data['tag'] = self.df['tag']
		return data

def indivector(df):
	return [_MACD(df), 
			_ATR(df)]



