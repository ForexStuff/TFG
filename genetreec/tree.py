import indicator
from random import randrange
import pandas as pd
from numpy import random
import math
import tagger
import copy


deepness = 10
indivector = indicator.indivector()

def entropy(v):           # v es la proporcion de la clase (frec/total)
	if v==0 or v==1:      #    Solo es valido para problemas binarios
		return 0
	return  (v*math.log(v,2)+(1-v)*math.log(1-v,2))




class Genetreec:
	root = None # Primer Node
	ind = 0   # Indice del árbol dentro de la población
	sellcount = 0 # Número de veces que ha vendido en el último backtest

	def __init__(self, ind):
		self.root = Leaf([True] * indicator.df.shape[0])
		self.ind = ind

	def warm(self):
		self.root = self.root.warm(deepness)
		self.root.setLeaveActions()

	def evaluate(self, date):
		return self.root.evaluate(date)

	def selectRandomBranch(self):
		r = randrange(5)
		lastBranch_side = None
		lastBranch_father = None
		if r == 0 or r == 2:
			lastBranch_side, lastBranch_father = self.root.left.selectRandomBranch()
			if isinstance(lastBranch_father, bool): # Si el elegido es el hijo
					lastBranch_side = "left"
					lastBranch_father = self.root
		elif r == 1 or r == 3:
			lastBranch_side, lastBranch_father = self.root.right.selectRandomBranch()
			if isinstance(lastBranch_father, bool): # Si el elegido es el hijo
					lastBranch_side = "right"
					lastBranch_father = self.root
		else:
			lastBranch_side = "root"
			lastBranch_father = self

		return lastBranch_side, lastBranch_father

	def getNumNodes(self):
		return self.root.getNumNodes()

	def mutate(self):
		self.root.mutate()
		return

	def getBuySell(self):
		return self.root.getBuySell()

class Node:
	func = None     # Indice que separa los datos
	pivot = None    # pivote que separa los datos

	right = None   # Node o Leaf positivo
	left = None    # Node o Leaf negativo

	def __init__(self, func, pivot, right, left):
		self.func = func
		self.pivot = pivot
		self.right = right
		self.left = left

	def setLeaveActions(self):
		self.right.setLeaveActions()
		self.left.setLeaveActions()

	def evaluate(self, date):
		if indicator.getValueByIndex(date, self.func) <= self.pivot:
			return self.left.evaluate(date)
		return self.right.evaluate(date)

	def plot(self):
		print('---- Function ' + self.func.name() + ' < ' + str(self.pivot) + ' ----')
		self.left.plot()
		print('\n')
		print('---- Function ' + self.func.name() + ' >= ' + str(self.pivot) + ' ----')
		self.right.plot()

	def selectRandomBranch(self):
		r = randrange(3)
		father = None
		if r == 0: # Elegida rama izq
			side, father = self.left.selectRandomBranch()
			if isinstance(father, bool):
				if father == True: 		# Si el elegido es el hijo
					return "left", self
				else:					# Si el hijo es una hoja
					return None, True
			return side, father				# Si el elegido es más profundo
		if r == 2: # Elegida rama der
			side, father = self.right.selectRandomBranch()
			if isinstance(father, bool):
				if father == True: 		# Si el elegido es el hijo
					return "right", self
				else:					# Si el hijo es una hoja
					return None, True
			return side, father				# Si el elegido es más profundo
		if r == 1:
			return None, True
	def getNumNodes(self):
		return self.left.getNumNodes() + self.right.getNumNodes() + 1

	def mutate(self):
		r = randrange(5)
		if r == 0:
			self.pivot = random.normal(self.pivot, abs(self.pivot/4))
		if r == 1:
			self.func.mutate()
		if r == 2:
			self.func = copy.deepcopy(indivector[randrange(13)])
			val = self.func.getValues(False)
			self.pivot = val['values'].mean()

		self.left.mutate()
		self.right.mutate()
		return

	def getBuySell(self):
		buy, sell = self.left.getBuySell()
		buy2, sell2 = self.right.getBuySell()
		return buy+buy2, sell+sell2

class Leaf:
	tag = None 			# La acción a tomar
	partition = None	# El vector booleano que representa a los datos (en la hoja) sobre df (datos en la raiz)

	def __init__(self, partition):
		self.partition = partition

 # Parte los datos de una hoja para hacer dos nuevas hojas. Se hace la partición con mejor partición
	def warm(self, levels):
		func = copy.deepcopy(indivector[randrange(13)])
		(criteria, pivot) = self.select_pivot(func.getValues())
		if isinstance(criteria, int): # El indicador no parte bien los datos
				if deepness == levels:    # Si es la primera hoja, toma otro indicador
					ret_node = self.warm(levels)
				else:
					ret_node = self
		else:		# Pivote correcto, devuelve el nuevo nodo
			right = Leaf(criteria & self.partition)
			left = Leaf(~criteria & self.partition)

			if levels>1 :
				right = right.warm(levels-1)
				left = left.warm(levels-1)
			ret_node = Node(func, pivot, right, left)
		return ret_node



# Dado un vector de datos, busca el pivote que mejor lo separa
# Tiene en cuenta la entropía
	def select_pivot(self, values):
		max_val = values['values'][self.partition].min()
		min_val = values['values'][self.partition].max()
		grill = [(max_val - min_val)*(x/10)+min_val for x in range(1,10)]   # Fabrica un parrilla
		grill_entropy = []

		total = sum(self.partition)

		total_inverse = 1 / total
		for x in grill:								# Para cada punto de la parrilla
			n_left  = sum(values['values'][self.partition] < x)		# Cuenta los datos de la partición
			n_right = sum(values['values'][self.partition] >= x)	# izquierda y derecha

			# Calcula la entropía de cada partición y la guarda
			if n_left < 3: # Pocos datos, no gastes tiempo calculando
				l_entropy = 1
				r_entropy = 1
			else:
				if n_right < 3:  # Pocos datos, no gastes tiempo calculando
					l_entropy = 1
					r_entropy = 1
				else:
					r_entropy = n_right* total_inverse * entropy( sum( (values['values'][self.partition]>=x) & (values['tag'][self.partition]<0)) / n_right )
					l_entropy  = n_left*total_inverse * entropy( sum( (values['values'][self.partition]<x)  & (values['tag'][self.partition]<0)) / n_left )

			grill_entropy.append(l_entropy + r_entropy)

		min_index = grill_entropy.index(min( grill_entropy ))
		pivot = grill[min_index]					# Coge el mejor pivote
		criteria = values['values'] < pivot			# hace el vector booleano
		indicator.df_count = sum(criteria & self.partition)
		if indicator.df_count < 3 or sum(self.partition)-indicator.df_count < 3: # Pocos datos para separar
			return (0,0)

		return (criteria, pivot)					# Devuelve el pivote y el vector.


# Selecciona una acción para la hoja (Solo se usa en el calentamiento)
#	Suma los datos de la hoja (-2, -1, 1 o 2)
#	Si la suma es
#		-2 <= x <= 2 entonces no se hace nada
#		x < -2       entonces se compra
#		2 < x		 entonces se vende
	def setLeaveActions(self):
		df = indicator.df[self.partition]
		sell_df = sum(df['tag'] > 0)
		buy_df = sum(df['tag'] < 0)
		double_sell_df = sum(df['tag'] == 2)
		double_buy_df = sum(df['tag'] == -2)
		action_sum = sell_df - buy_df + double_sell_df - double_buy_df / (sell_df + buy_df)

		if action_sum > 0:
			if action_sum <= 2:
				self.tag = 'Stop'
			else:
				self.tag = 'Sell'
		else:
			if action_sum >= -2:
				self.tag = 'Stop'
			else:
				self.tag = 'Buy'
		self.partition = None
		return

# Devuelve la acción de la hoja
	def evaluate(self, date):
		return self.tag

# Gráfico del arbol, por ahora es en terminal
	def plot(self):
		print(self.tag)
		return None

# La selección de rama ha entrado hasta una hoja, notifica el error
	def selectRandomBranch(self):
		return None, False


	def getNumNodes(self):
		return 0

	def mutate(self):
		r = randrange(7)
		if r == 0:
			self.tag = 'Buy'
		elif r == 1:
			self.tag = 'Stop'
		elif r == 2:
			self.tag = 'Sell'
		return

	def getBuySell(self):
		if self.tag == 'Buy':
			return 1,0
		if self.tag == 'Sell':
			return 0,1
		return 0,0
