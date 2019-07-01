from tree import Genetreec as gentree
import tagger
import indicator
import pandas as pd
import backtrader as bt
import yfinance as yf
import time




#tagger.acumtag()   #Just needed one time, data tagged is saved between executions
data = pd.read_csv('tagged_data/SAN.csv')
population = []

for i in range(3):   # Train the first population
	tree = gentree()
	tree.train()
	population.append(tree)
	print('Tree ' + str(i) + ' trained.')

class TreeStrategy(bt.Strategy):
	params=(('tree', None),)

	def log(self, txt, dt=None):
		dt = dt or self.datas[0].datetime.date(0)
		print('%s, %s' % (dt.isoformat(), txt))

	def __init__(self):
		self.dataclose = self.datas[0].close
		self.tree = tree
		# Para mantener las ordenes no ejecutadas
		self.order = None

	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
			return

		if order.status in [order.Completed]:
			if order.isbuy():
				self.log('BUY EXECUTED, %.2f' % order.executed.price)
			elif order.issell():
				self.log('SELL EXECUTED, %.2f' % order.executed.price)

			self.bar_executed = len(self)

		elif order.status in [order.Canceled, order.Margin, order.Rejected]:
			self.log('Order Canceled/Margin/Rejected')

		self.order = None

	def next(self):
	# Si hay una compraventa pendiente no puedo hacer otra
		if self.order:
			return
		return

df = yf.download("SAN", start="2017-01-01", end="2017-04-30")  # Set data
df = bt.feeds.PandasData(dataname = df) ############################### ACEPTARÁ LOS DATOS TAGGEADOS ?????
indicator.setData(df)
treeScore = []

ts = time.time()
for tree in population:
	cerebro = bt.Cerebro(maxcpus=None)
	cerebro.optstrategy(TreeStrategy,tree=population)   # Set strategy

	cerebro.adddata(df)

	cerebro.broker.setcash(100000.0)	# Set money

	cerebro.run()   # EJECUTAR BACKTESTING
	treeScore.append(cerebro.broker.getvalue())

te = time.time()
print((te - ts))
print(treeScore)
