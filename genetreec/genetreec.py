from tree import Genetreec as gentree
import tagger
import indicator
import pandas as pd
import backtrader as bt
import yfinance as yf
import time


#tagger.acumtag()   # Solo se ejecuta la primera vez, el etiquetado es lento
					# y mejor hacerlo solo una vez
data = pd.read_csv('tagged_data/SAN.csv')
population = []

for i in range(3):   # Calentamiento de la población 1
	tree = gentree(i)
	tree.train()
	population.append(tree)
	print('Tree ' + str(i) + ' trained.')




class TreeStrategy(bt.Strategy):
	params=(('tree', None),)
	end_val = 0

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





class EndStats(bt.Analyzer):
    # Analizador para poder tener en cuenta varias
	# estrategias de una sola ejecución (optstrategy)

    def __init__(self):
        self.start_val = self.strategy.broker.get_value()
        self.end_val = None

    def stop(self):
        self.end_val = self.strategy.broker.get_value()

    def get_analysis(self):
        return {"start": self.start_val, "end": self.end_val,
                "growth": self.end_val - self.start_val, "return": self.end_val / self.start_val}






df = yf.download("SAN", start="2017-01-01", end="2017-04-30")  # Set data
df = bt.feeds.PandasData(dataname = df) ############################### ACEPTARA LOS DATOS TAGGEADOS ?????
indicator.setData(df)
treeScore = []

ts = time.time()

cerebro = bt.Cerebro(maxcpus=None)
cerebro.optstrategy(TreeStrategy,tree=list(population))   # Seleccionar estrategia
cerebro.addanalyzer(EndStats)						      # Seleccionar analizador
cerebro.adddata(df)										  # Seleccionar datos
cerebro.broker.setcash(100000.0)	# Seleccionar dinero
ret = cerebro.run()   # EJECUTAR BACKTESTING

te = time.time()
print("El tiempo de simulación es: ",(te - ts))


scores = pd.DataFrame({r[0].params.tree.index: r[0].analyzers.endstats.get_analysis() for r in ret}
                      ).T.loc[:, ['end', 'growth', 'return']]
print(scores)  #Ver puntuaciones de la poblacion
