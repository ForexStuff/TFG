import pandas as pd
from ta import *

df = pd.read_csv('Data/SAN.csv')
df['macd'] = macd(df['Close'])

print(df)

