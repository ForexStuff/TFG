from tree import Genetreec as gentree
import tagger
import indicator
import pandas as pd
import backtrader as bt
import fix_yahoo_finance as yf

#tagger.acumtag()   #Just needed one time, data tagged is saved between executions
data = pd.read_csv('tagged_data/SAN.csv')
population = []

for i in range(100):   # Train the first population
	tree = gentree()
	tree.train()
	population.append(tree)
	print('Tree ' + str(i) + ' trained.')

treeScore = []
for tree in population:
	cerebro = bt.Cerebro()
	cerebro.addstrategy(TreeStrategy(tree))   # Set strategy


	data = yf.download("BBVA", "2010-01-01", "2018-12-31")  # Set data
	df = bt.feeds.PandasData(dataname = data) ############################### ACEPTARÁ LOS DATOS TAGGEADOS ?????
	cerebro.adddata(data)
   
	cerebro.broker.setcash(100000.0)	# Set money

	cerebro.run()   # EJECUTAR BACKTESTING 
	treeScore.append(cerebro.broker.getvalue())





class TreeStrategy(bt.Strategy):
	def log(self, txt, dt=None):
		dt = dt or self.datas[0].datetime.date(0)
		print('%s, %s' % (dt.isoformat(), txt))

	def __init__(self, tree):
		self.dataclose = self.datas[0].close
		self.tree = tree
		# Para mantener las ordenes no ejecutadas
		self.order = None

	def next(self):
		self.log('Close, %.2f' % self.dataclose[0])
		
		if self.order:  # If an action is pending, wait
			return

		if not self.position: 	# We have no stocks
															# If the tree action is buy, then buy
		else:										# We have stocks
															# If the tree action is sell, then sell


