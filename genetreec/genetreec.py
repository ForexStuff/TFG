import indicator
import random
import pandas as pd

df = pd.read_csv('../Data/SAN.csv')
indivector = indicator.indivector(df)

class Genetreec:
	root = None #first Node

	def __init__(self,data):
		self.root = Leaf(data)
		
	def train(self):
		self.root = self.root.train()

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


class Leaf:
	tag = None   #the final tag the data on the leaf will be classificated as (Used just when the tree is tagged)
	data = None  #the partition of data which verifies the branch's nodes restrictions

	def __init__(self, data):
		self.data = data

	def train(self):
		func = indivector[random.randint(0,1)]
		pivot = 0.5
		self.data[func.name()] = func.calculate()
		criteria = self.data[func.name()] < pivot

		right = Leaf(self.data[criteria])
		left = Leaf(self.data[~criteria])
		
		print(self.data[~criteria])
		print(self.data[criteria])
		return Node(func, pivot, right, left)



genetri = Genetreec(df)
genetri.train()

