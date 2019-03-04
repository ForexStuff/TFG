import pandas as pd


df = pd.read_csv('Data/SAN.csv')
df['sma2'] = (df['Close'].rolling(2).mean())

print(df)
