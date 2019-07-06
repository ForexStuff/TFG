from tree import Genetreec as gentree
import tagger
import indicator
import pandas as pd
import backtrader as bt
import yfinance as yf
import math
import numpy as np
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





# Dados dos árboles, intercambia 'aleatoriamente' dos de sus ramas.
def Crossover(atree, btree):
	print("Crossover entre " + str(atree.ind) + " y " + str(btree.ind))
	return atree, btree





# Dada una población y sus puntuaciones, devuelve la población del
# algoritmo con sus probabilidades reproductivas.
def Reproductivity(population, score):
	pop_score = pd.DataFrame()
	pop_score['tree'] = [tree for tree in population]
	pop_score['score'] = score
	pop_score = pop_score.sort_values(by=['score'], ascending=False)

	# Escalado Min-max para sacar probabilidades (score al intervalo [0,1])
	pop_score['score'] -= pop_score['score'].min()
	pop_score['score'] /= pop_score['score'].sum()
	pop_score['score'] = pop_score['score'].cumsum()

	return pop_score






# Dada la población de una iteración, devuelve la de la siguiente.
def NextPopulation(population, score):
	saveLen = int(len(population)/2-1)
	nextpopulation = []
	popu_reprod = Reproductivity(population,score)
	print(popu_reprod)

	# El mejor lo guardo siempre
	nextpopulation.append(popu_reprod['tree'][0])
	nextpopulation.append(popu_reprod['tree'][1])
	auni = np.random.uniform(0,1,saveLen)
	buni = np.random.uniform(0,1,saveLen)
	print(auni)
	print(buni)

	for i in range(saveLen):
		atree = (popu_reprod['tree'][popu_reprod['score'] >= auni[i]]).iloc[0]
		btree = (popu_reprod['tree'][popu_reprod['score'] >= buni[i]]).iloc[0]
		atree, btree = Crossover(atree, btree)
		nextpopulation.append(atree)
		nextpopulation.append(btree)
	return nextpopulation







tagger.acumtag()   # Solo se ejecuta la primera vez, el etiquetado es lento
					# y mejor hacerlo solo una vez
data = pd.read_csv('tagged_data/SAN.csv')
population = []

for i in range(6):   # Calentamiento de la población 1
	tree = gentree(i)
	tree.warm()
	population.append(tree)
	print('Tree ' + str(i) + ' warmed.')



df = pdr.get_data_yahoo("SAN", start="2018-01-02", end="2018-05-31")
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


scores = pd.DataFrame({r[0].params.tree.ind: r[0].analyzers.endstats.get_analysis() for r in ret}
                      ).T.loc[:, ['end', 'growth', 'return']]

print(NextPopulation(population, scores['end']))
