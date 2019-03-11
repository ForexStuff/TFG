import pandas as pd
from ta import *
from functools import partial

class MACD:

	def __init__(self, df, lowday=5, highday=10):
		self.df = df
		self.lowday = lowday
		self.highday = highday	

	def name(self):
		return 'MACD_' + str(self.lowday) + '_' + str(self.highday) 

	def calculate(self):
		return macd(self.df['Close'], 
				self.lowday, 
				self.highday, 
				True)

class ATR:

	def __init__(self, df, period=7):
		self.df = df
		self.period = period

	def name(self):
		return 'ATR_' + str(self.period)

	def calculate(self):
		return average_true_range(self.df['High'],
							self.df['Low'], 
							self.df['Close'], 
							self.period, 
							True)

def indivector(df):
	return [MACD(df), 
			ATR(df)]



