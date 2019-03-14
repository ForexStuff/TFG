import indicator
import random
import pandas as pd

df = pd.read_csv('../Data/SAN.csv')
indivector = indicator.indivector(df)

class Genetreec:
	root = None #first Node

	def __init__(self,data):
		self.root = Leaf(data, [True] * data.shape[0])
		
	def train(self):
		self.root = self.root.train()
		self.root.plot()

	def test(self, data):
		return None


class Node:
	func = None  #func to evaluate to split the data
	pivot = None    #value to split the data

	right = None   #node or leaf positive
	left = None    #node or leaf negative

	def __init__(self, func, pivot, right, left):
		self.func = func
		self.pivot = pivot
		self.right = right
		self.left = left

	def plot(self):
		print('---- Function ' + self.func.name() + ' < ' + str(self.pivot) + ' ----')
		self.left.plot()
		print('\n')		
		print('---- Function ' + self.func.name() + ' >= ' + str(self.pivot) + ' ----')
		self.right.plot()

class Leaf:
	tag = None   #the final tag the data on the leaf will be classificated as (Used just when the tree is tagged)
	data = None  #the partition of data which verifies the branch's nodes restrictions
	partition = None   #the boolean vector that represent data (data at branch) over df (data at root)

	def __init__(self, data, partition):
		self.data = data
		self.partition = partition

	def train(self):
		func = indivector[random.randint(0,1)]
		pivot = 0.5
		criteria = func.calculate() < pivot

		right = Leaf(df[criteria & self.partition], criteria & self.partition)
		left = Leaf(df[~criteria & self.partition], ~criteria & self.partition)

		return Node(func, pivot, right, left)

	def plot(self):
		print(df[self.partition])
		return None


genetri = Genetreec(df)
genetri.train()

