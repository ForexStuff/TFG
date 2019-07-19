from tree import Genetreec as gentree
from copy import deepcopy
import tagger
import indicator
import pandas as pd
import backtrader as bt
import yfinance as yf
import math
import numpy as np
from pandas_datareader import data as pdr
import time
import warnings
#warnings.simplefilter(action='ignore', category=FutureWarning)


from profilehooks import profile

class TreeStrategy(bt.Strategy):
	params=(('tree', None),)
	end_val = 0

	def __init__(self):
		self.dataclose = self.datas[0].close
		# Para mantener las ordenes no ejecutadas
		self.order = None



	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
			return

		self.order = None
		return


	def next(self):
	# Si hay una compraventa pendiente no puedo hacer otra
		if self.order:
			return
		action = self.params.tree.evaluate(date=self.datas[0].datetime.date(0))
		if action == 'Buy':
			if self.position.size == 0:
				self.order = self.buy(size = math.floor(self.broker.get_cash()/(self.datas[0].close*1.01)) )
					## Como estamos usando una comisión del 1% las acciones son un 1% más caras.
					## La cantidad de acciones que podemos comprar es la parte entera de nuestro
					## dinero entre el valor de una acción mas su comisión.
		if action == 'Sell':
			if self.position.size > 0:
				self.order = self.sell(size=self.position.size)




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
	aside, abranch = atree.selectRandomBranch()
	bside, bbranch = btree.selectRandomBranch()

	auxbranch = None
	if aside == "left":
		auxbranch = abranch.left
		if bside == "left":
			abranch.left = bbranch.left
			bbranch.left = auxbranch
		else:
			abranch.left = bbranch.right
			bbranch.right = auxbranch
	else:
		auxbranch = abranch.right
		if bside == "left":
			abranch.right = bbranch.left
			bbranch.left = auxbranch
		else:
			abranch.right = bbranch.right
			bbranch.right = auxbranch

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
	aux = pop_score['score'].sum()
	if aux == 0:
		aux = 1/pop_score.shape[0]
		pop_score['score'] = [num*aux for num in range(1,pop_score.shape[0]+1)]
	else:
		aux = 1/aux
		pop_score['score'] *= aux
		pop_score['score'] = pop_score['score'].cumsum()

	print(pop_score)
	return pop_score






# Dada la población de una iteración, devuelve la de la siguiente.
def NextPopulation(population, score):
	saveLen = int(len(population)/2-1)
	nextpopulation = []
	popu_reprod = Reproductivity(population,score)

	# Los 2 mejores los guardo siempre
	buy, sell = popu_reprod.iloc[0]['tree'].getBuySell()
	print('buy=' + str(buy) + ', sell=' + str(sell))
	popu_reprod.iloc[1]['tree'].mutate()
	nextpopulation.append(popu_reprod.iloc[0]['tree'])
	nextpopulation.append(popu_reprod.iloc[1]['tree'])
	auni = np.random.uniform(0,1,2*saveLen)

	for i in range(saveLen):
		atree = (popu_reprod['tree'][popu_reprod['score'] >= auni[i]]).iloc[0]
		btree = (popu_reprod['tree'][popu_reprod['score'] >= auni[i+saveLen]]).iloc[0]
		atree, btree = Crossover(deepcopy(atree), deepcopy(btree))
		atree.mutate() #Mutación
		btree.mutate() #Mutación
		nextpopulation.append(atree)
		nextpopulation.append(btree)
	i=0
	for tree in nextpopulation:
		tree.ind = i
		i += 1
	return nextpopulation






start_date_train = "2013-08-01"
end_date_train   = "2014-02-26"
start_date_test  = "2014-02-26"
end_date_test    = "2014-08-01"
tagger.acumtag(start_date_train, end_date_train)   # Solo se ejecuta la primera vez, el etiquetado es lento
					# y mejor hacerlo solo una vez
data = pd.read_csv('tagged_data/SAN.csv')
population = []

for i in range(30):   # Calentamiento de la población 1
	tree = gentree(i)
	tree.warm()
	population.append(tree)
	print('Tree ' + str(i) + ' warmed.')



simudatos = pdr.get_data_yahoo("SAN", start=start_date_train, end=end_date_train)
# df = yf.download("SAN", start="2017-01-01", end="2017-04-30")  # Otra forma de coger los datos
df_cerebro = bt.feeds.PandasData(dataname = simudatos)
indicator.setData(simudatos)
treeScore = []



cerebro = bt.Cerebro(maxcpus=1)
cerebro.optstrategy(TreeStrategy,tree=list(population))   # Seleccionar estrategia
cerebro.addanalyzer(EndStats)						      # Seleccionar analizador
cerebro.adddata(df_cerebro)										  # Seleccionar datos
cerebro.broker.set_coc(True)
cerebro.broker.setcash(10000.0)	# Seleccionar dinero
cerebro.broker.setcommission(commission=0.00)

for i in range(20):
	ts = time.time()
	ret = cerebro.run()   # EJECUTAR BACKTESTING

	scores = pd.DataFrame({r[0].params.tree.ind: r[0].analyzers.endstats.get_analysis() for r in ret}
	                      ).T.loc[:, ['end', 'growth', 'return']]

	print(scores)
	population = NextPopulation(population, scores['end'])
	# Aquí debería ir la mutación
	# Por motivos de eficiencia se hace dentro de NextPopulation

	te = time.time()
	print("El tiempo de simulación es: ",(te - ts))

	indicator.setData(simudatos)
	cerebro = bt.Cerebro(maxcpus=None)
	cerebro.optstrategy(TreeStrategy,tree=list(population))   # Seleccionar estrategia
	cerebro.addanalyzer(EndStats)						      # Seleccionar analizador
	cerebro.adddata(df_cerebro)										  # Seleccionar datos
	cerebro.broker.set_coc(True)
	cerebro.broker.setcash(10000.0)	# Seleccionar dinero
	cerebro.broker.setcommission(commission=0.0)

	tot = 0
	for tree in population:
		tot+=tree.getNumNodes()
	print(tot/len(population))


ret = cerebro.run()
scores = pd.DataFrame({r[0].params.tree.ind: r[0].analyzers.endstats.get_analysis() for r in ret}
                      ).T.loc[:, ['end', 'growth', 'return']]

pop_score = pd.DataFrame()
pop_score['tree'] = [tree for tree in population]
pop_score['score'] = scores['end']
pop_score = pop_score.sort_values(by=['score'], ascending=False)
modelTree = pop_score.iloc[0]['tree']

simudatos = pdr.get_data_yahoo("SAN", start=start_date_test, end=end_date_test)
df_cerebro = bt.feeds.PandasData(dataname = simudatos)
indicator.setData(simudatos)
cerebro = bt.Cerebro(maxcpus=1)
cerebro.optstrategy(TreeStrategy,tree=modelTree)   # Seleccionar estrategia
cerebro.addanalyzer(EndStats)						      # Seleccionar analizador
cerebro.adddata(df_cerebro)										  # Seleccionar datos
cerebro.broker.set_coc(True)
cerebro.broker.setcash(10000.0)	# Seleccionar dinero
cerebro.broker.setcommission(commission=0.0)
ret = cerebro.run()
score = pd.DataFrame({r[0].params.tree.ind: r[0].analyzers.endstats.get_analysis() for r in ret}
                      ).T.loc[:, ['end', 'growth', 'return']]

print('Score on test:')
print(score)
