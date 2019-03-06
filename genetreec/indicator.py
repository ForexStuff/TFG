import pandas as pd
from ta import *
from functools import partial

def MACD(df, lowday=5, highday=10):
	return macd(df['Close'], 
				lowday, 
				highday, 
				True)

def ATR(df, period=7):
	return average_true_range(df['High'],
							df['Low'], 
							df['Close'], 
							period, 
							True)


df = pd.read_csv('../Data/SAN.csv')
list_of_foo = [partial(MACD,df), partial(ATR,df)]

print(list_of_foo[]())


