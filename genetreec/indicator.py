import pandas as pd
import talib 

class _MACD:

	def __init__(self, df, lowday=5, highday=10):
		self.df = df
		self.lowday = lowday
		self.highday = highday	

	def name(self):
		return 'MACD_' + str(self.lowday) + '_' + str(self.highday) 

	def calculate(self):
		return talib.MACD(self.df['Close'], 
				self.lowday, 
				self.highday)[0]

class _ATR:

	def __init__(self, df, period=7):
		self.df = df
		self.period = period

	def name(self):
		return 'ATR_' + str(self.period)

	def calculate(self):
		return talib.ATR(self.df['High'],
							self.df['Low'], 
							self.df['Close'], 
							self.period)

def indivector(df):
	return [_MACD(df), 
			_ATR(df)]



