from tree import Genetreec as gentree
import tagger
import indicator
import pandas as pd
import backtrader as bt
import yfinance as yf
import math
from pandas_datareader import data as pdr
import time


class TreeStrategy(bt.Strategy):
	params=(('tree', None),)
	end_val = 0

	def __init__(self):
		self.dataclose = self.datas[0].close
		# Para mantener las ordenes no ejecutadas
		self.order = None


	def next(self):
	# Si hay una compraventa pendiente no puedo hacer otra
		if self.order:
			return

		action = self.params.tree.evaluate(date=self.datas[0].datetime.date(0))
		if action == 'Buy':
			if not self.position:
				self.order = self.buy(size = math.floor(self.broker.get_cash()/(self.datas[0].close*1.01)) )
					## Como estamos usando una comisión del 1% las acciones son un 1% más caras.
					## La cantidad de acciones que podemos comprar es la parte entera de nuestro
					## dinero entre el valor de una acción mas su comisión.
				return
		if action == 'Sell':
			if self.position:
				self.order = self.sell(size=self.position.size)
				return
		if action == 'Stop':
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



tagger.acumtag()   # Solo se ejecuta la primera vez, el etiquetado es lento
					# y mejor hacerlo solo una vez
data = pd.read_csv('tagged_data/SAN.csv')
population = []

for i in range(8):   # Calentamiento de la población 1
	tree = gentree(i)
	tree.warm()
	population.append(tree)
	print('Tree ' + str(i) + ' warmed.')



df = pdr.get_data_yahoo("SAN", start="2017-01-02", end="2017-05-31")
# df = yf.download("SAN", start="2017-01-01", end="2017-04-30")  # Otra forma de coger los datos
df_cerebro = bt.feeds.PandasData(dataname = df)
indicator.setData(df)
treeScore = []

ts = time.time()

cerebro = bt.Cerebro(maxcpus=None)
cerebro.optstrategy(TreeStrategy,tree=list(population))   # Seleccionar estrategia
cerebro.addanalyzer(EndStats)						      # Seleccionar analizador
cerebro.adddata(df_cerebro)										  # Seleccionar datos
cerebro.broker.set_coc(True)
cerebro.broker.setcash(10000.0)	# Seleccionar dinero
cerebro.broker.setcommission(commission=0.01)
ret = cerebro.run()   # EJECUTAR BACKTESTING

te = time.time()
print("El tiempo de simulación es: ",(te - ts))


scores = pd.DataFrame({r[0].params.tree.index: r[0].analyzers.endstats.get_analysis() for r in ret}
                      ).T.loc[:, ['end', 'growth', 'return']]
print(scores)  #Ver puntuaciones de la poblacion
