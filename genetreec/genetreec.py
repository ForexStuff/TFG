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


class TreeStrategy(bt.Strategy):
	params=(('tree', None),)
	sellcount = 0

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
				self.sellcount += 1


	def stop(self):
		self.params.tree.sellcount = self.sellcount
		return



#############################################
#### COPY OF TreeStrategy   --- Made for plot
#############################################
class plotTreeStrategy(bt.Strategy):
	params=(('tree', None),)

	def __init__(self):
		self.dataclose = self.datas[0].close
		# Para mantener las ordenes no ejecutadas
		self.order = None
		self.tree = self.params.tree

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
		self.sells=0

	def stop(self):
		self.end_val = self.strategy.broker.get_value()
		self.sells = self.strategy.params.tree.sellcount

	def get_analysis(self):
		return {"start": self.start_val, "end": self.end_val,
				"growth": self.end_val - self.start_val, "return": self.end_val / self.start_val}




class Simulate:
	data = None
	population = None
	nextpopulation = None
	forest = []
	numbertree = 60
	numberiter = 150
	start_date_train = "2010-09-22"  ## "20XX-03-20" "20XX-09-21"
	end_date_train   = "2011-03-19"  ## "20XX-09-22" "20XX-03-19"
	start_date_test  = "2011-03-20"
	end_date_test    = "2011-09-21"
	symbol = "WPRT"


	# Dados dos árboles, intercambia 'aleatoriamente' dos de sus ramas.
	def Crossover(self, atree, btree):
		aside, abranch = atree.selectRandomBranch()
		bside, bbranch = btree.selectRandomBranch()

		auxbranch = None
		if aside == "left":
			auxbranch = abranch.left
			if bside == "left":
				abranch.left = bbranch.left
				bbranch.left = auxbranch
			elif bside == "right":
				abranch.left = bbranch.right
				bbranch.right = auxbranch
			else:
				abranch.left = bbranch.root
				bbranch.root = auxbranch
		elif aside == "right":
			auxbranch = abranch.right
			if bside == "left":
				abranch.right = bbranch.left
				bbranch.left = auxbranch
			elif bside == "right":
				abranch.right = bbranch.right
				bbranch.right = auxbranch
			else:
				abranch.right = bbranch.root
				bbranch.root = auxbranch
		else:
			auxbranch = abranch.root
			if bside == "left":
				abranch.root = bbranch.left
				bbranch.left = auxbranch
			elif bside == "right":
				abranch.root = bbranch.right
				bbranch.right = auxbranch
			else:
				abranch.root = bbranch.root
				bbranch.root = auxbranch

		return atree, btree


	# Dada una población y sus puntuaciones, devuelve la población del
	# algoritmo con sus probabilidades reproductivas.
	def Reproductivity(self, score):
		pop_score = pd.DataFrame()
		pop_score['tree'] = [tree for tree in self.population]
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

		return pop_score



	# Dada la población de una iteración, devuelve la de la siguiente.
	def NextPopulation(self, score):
		self.nextpopulation = []
		popu_reprod = self.Reproductivity(score)

		# Los 2 mejores los guardo siempre
		buy, sell = popu_reprod.iloc[0]['tree'].getBuySell()
		print('buy=' + str(buy) + ', sell=' + str(sell))

		self.nextpopulation.append(deepcopy(popu_reprod.iloc[0]['tree']))
		self.nextpopulation.append(deepcopy(popu_reprod.iloc[1]['tree']))
		popu_reprod.iloc[0]['tree'].mutate()
		popu_reprod.iloc[1]['tree'].mutate()
		popu_reprod.iloc[2]['tree'].mutate()
		popu_reprod.iloc[3]['tree'].mutate()
		self.nextpopulation.append(popu_reprod.iloc[0]['tree'])
		self.nextpopulation.append(popu_reprod.iloc[1]['tree'])
		self.nextpopulation.append(popu_reprod.iloc[2]['tree'])
		self.nextpopulation.append(popu_reprod.iloc[3]['tree'])


		i=0
		while self.numbertree > len(self.nextpopulation):
			auni = np.random.uniform(0,1,2)
			atree = (popu_reprod['tree'][popu_reprod['score'] >= auni[0]]).iloc[0]
			btree = (popu_reprod['tree'][popu_reprod['score'] >= auni[1]]).iloc[0]
			atree, btree = self.Crossover(deepcopy(atree), deepcopy(btree))
			aux = atree.getNumNodes()
			if aux < 65 and aux > 18:
				if i == 2:
					atree.mutate() #Mutación
					i = 0
				self.nextpopulation.append(atree)
			aux = btree.getNumNodes()
			if aux < 65 and aux > 18:
				if i == 2:
					btree.mutate() #Mutación
					i = 0
				self.nextpopulation.append(btree)
			i += 1

		i=0
		for tree in self.nextpopulation:
			tree.ind = i
			i += 1
		self.population = self.nextpopulation
		return None


	def prepare(self):
		tagger.acumtag(self.start_date_train, self.end_date_train, self.symbol)   # Solo se ejecuta la primera vez, el etiquetado es lento
							# y mejor hacerlo solo una vez
		self.data = pd.read_csv('tagged_data/' + self.symbol + '.csv')
		indicator.setData(self.data)
		self.population = []

		for i in range(self.numbertree):   # Calentamiento de la población 1
			tree = gentree(i)
			tree.warm()
			self.population.append(tree)
			print('Tree ' + str(i) + ' warmed.')

	def execute(self):
		simudatos = pdr.get_data_yahoo(self.symbol, start=self.start_date_train, end=self.end_date_train)
		# df = yf.download(self.symbol, start="2017-01-01", end="2017-04-30")  # Otra forma de coger los datos
		df_cerebro = bt.feeds.PandasData(dataname = simudatos)
		indicator.setData(simudatos)



		cerebro = bt.Cerebro(maxcpus=None)
		cerebro.optstrategy(TreeStrategy,tree=list(self.population))   # Seleccionar estrategia
		cerebro.addanalyzer(EndStats)						      # Seleccionar analizador
		cerebro.adddata(df_cerebro)										  # Seleccionar datos
		cerebro.broker.set_coc(True)
		cerebro.broker.setcash(10000.0)	# Seleccionar dinero
		cerebro.broker.setcommission(commission=0.005)

		for i in range(self.numberiter):
			ts = time.time()
			ret = cerebro.run()   # EJECUTAR BACKTESTING

			scores = pd.DataFrame({r[0].params.tree.ind: r[0].analyzers.endstats.get_analysis() for r in ret}
			                      ).T.loc[:, ['end', 'growth', 'return']]

			#print(scores)
			self.NextPopulation(scores['growth'])
			te = time.time()
			print("-- ITERACION " + str(i) + " --")
			print("El tiempo de simulación es: ",(te - ts))
			#if i > self.halfiter:
			#	self.forest.append(deepcopy(self.population[6]))

			indicator.setData(simudatos)
			cerebro = bt.Cerebro(maxcpus=None)
			cerebro.optstrategy(TreeStrategy,tree=list(self.population))   # Seleccionar estrategia
			cerebro.addanalyzer(EndStats)						      # Seleccionar analizador
			cerebro.adddata(df_cerebro)										  # Seleccionar datos
			cerebro.broker.set_coc(True)
			cerebro.broker.setcash(10000.0)	# Seleccionar dinero
			cerebro.broker.setcommission(commission=0.005)

			tot = 0
			for tree in self.population:
				tot+=tree.getNumNodes()
			print('La media de nodos es ' + str(tot/len(self.population)))


		ret = cerebro.run()
		scores = pd.DataFrame({r[0].params.tree.ind: r[0].analyzers.endstats.get_analysis() for r in ret}
		                      ).T.loc[:, ['end', 'growth', 'return']]

		pop_score = pd.DataFrame()
		pop_score['tree'] = [tree for tree in self.population]
		pop_score['score'] = scores['growth']
		pop_score = pop_score.sort_values(by=['score'], ascending=False)
		model = pop_score.iloc[0]['tree']

		indicator.setData(simudatos)
		cerebro = bt.Cerebro(maxcpus=1)
		cerebro.addstrategy(plotTreeStrategy, tree=model)   # Seleccionar estrategia
		cerebro.adddata(df_cerebro)										  # Seleccionar datos
		cerebro.broker.set_coc(True)
		cerebro.broker.setcash(10000.0)	# Seleccionar dinero
		cerebro.broker.setcommission(commission=0.00)
		cerebro.run()
		cerebro.plot()



		simudatos = pdr.get_data_yahoo(self.symbol, start=self.start_date_test, end=self.end_date_test)
		df_cerebro = bt.feeds.PandasData(dataname = simudatos)
		indicator.setData(simudatos)
		cerebro = bt.Cerebro(maxcpus=1)
		cerebro.addstrategy(plotTreeStrategy, tree=model)   # Seleccionar estrategia
		cerebro.adddata(df_cerebro)										  # Seleccionar datos
		cerebro.broker.set_coc(True)
		cerebro.broker.setcash(10000.0)	# Seleccionar dinero
		cerebro.broker.setcommission(commission=0.00)
		cerebro.run()
		model.root.plot()
		indicator.printa()
		cerebro.plot()



sim = Simulate()
sim.prepare()
sim.execute()
