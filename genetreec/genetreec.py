import indicator
import random
import pandas as pd
import math
import tagger

df = pd.read_csv('../Data/SAN.csv')
df = tagger.acumtag(df)
indivector = indicator.indivector(df)



def entropy(v):
	if v==0 or v==1:
		return 0
	return -(v*math.log(v,2)+(1-v)*math.log(1-v,2))


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
	data = None  #PROBABLY NOT USEFUL #the partition of data which verifies the branch's nodes restrictions
	partition = None   #the boolean vector that represent data (data at branch) over df (data at root)

	def __init__(self, data, partition):
		self.data = data
		self.partition = partition

	def train(self):
		func = indivector[random.randint(0,1)]
		(criteria, pivot) = self.select_pivot(func.calculate())

		right = Leaf(df[criteria & self.partition], criteria & self.partition)
		left = Leaf(df[~criteria & self.partition], ~criteria & self.partition)

		return Node(func, pivot, right, left)

	def select_pivot(self, values):
		grill = [x/10 for x in range(1,10)]
		grill_entropy = []

		for x in grill:
			n_left  = sum(values['values'] < x)
			n_right = sum(values['values'] >= x)
			total_inverse = 1 / (n_left + n_right)
			if n_left == 0:
				l_entropy = 0
			else:
				l_entropy  = n_left*total_inverse   * entropy( sum( (values['values']<x)  & (values['tag']<0)) / n_left )
			if n_right == 0:
				r_entropy = 0
			else:			
				r_entropy = n_right* total_inverse * entropy( sum( (values['values']>=x) & (values['tag']<0)) / n_right ) 
			grill_entropy.append(l_entropy + r_entropy)

		#grill_entropy = [entropy(sum(values['values'] < x and values['tag'] < 0)/sum(values['values'] < x)) for x in grill]
		max_index = grill_entropy.index(min( grill_entropy ))

		pivot = grill[max_index]
		print(grill_entropy)
		criteria = values['values'] < pivot
		return (criteria, pivot)

	def plot(self):
		print(df[self.partition])
		return None


genetri = Genetreec(df)
genetri.train()

