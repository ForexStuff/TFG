import indicator
import random
import pandas as pd
import math
import tagger
import copy
from pandas_datareader import data as pdr

df = pdr.get_data_yahoo("SAN", start="2017-01-01", end="2019-03-30")
df = tagger.acumtag(df)
indivector = indicator.indivector(df)



def entropy(v):           # v is the class proportion (frec/total)
	if v==0 or v==1:      #    Just works with 2-classes problem
		return 0
	return -(v*math.log(v,2)+(1-v)*math.log(1-v,2))


class Genetreec:
	root = None #first Node
																																											
	def __init__(self,data):
		self.root = Leaf(data, [True] * data.shape[0])

	def train(self):
		self.root = self.root.train(5)
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

	def train(self, levels): # Take the actual partition and a new function indicator, calculate the entropic pivot and split into 2 leaves
		func = copy.deepcopy(indivector[random.randint(0,9)])
		(criteria, pivot) = self.select_pivot(func.calculate())
		if isinstance(criteria, int) :    # Fail recieved, pivot to split not found, return the leaf
			return self
		else:		# Pivot found, return the Node with two son leaves
			right = Leaf(df[criteria & self.partition], criteria & self.partition)
			left = Leaf(df[~criteria & self.partition], ~criteria & self.partition)
			
			if levels>1 :
				right = right.train(levels-1)
				left = left.train(levels-1)
			return Node(func, pivot, right, left)

	def select_pivot(self, values):
		max_val = values['values'].min()
		min_val = values['values'].max()
		grill = [(max_val - min_val)*(x/10)+min_val for x in range(1,10)]   # Make a grill to test pivots
		grill_entropy = []

		total = sum(self.partition)

		total_inverse = 1 / total
		for x in grill:								# For each point on grill
			n_left  = sum(values['values'][self.partition] < x)		# Calculate left and right data
			n_right = sum(values['values'][self.partition] >= x)	# Calculate the first class frecuency on both
													  				# Calculate the total entropy and save to take the best 
			if n_left == 0:
				l_entropy = 1
			else:
				l_entropy  = n_left*total_inverse * entropy( sum( (values['values'][self.partition]<x)  & (values['tag'][self.partition]<0)) / n_left )
			if n_right == 0:
				r_entropy = 1
			else:			
				r_entropy = n_right* total_inverse * entropy( sum( (values['values'][self.partition]>=x) & (values['tag'][self.partition]<0)) / n_right ) 
			grill_entropy.append(l_entropy + r_entropy)

		print(grill_entropy)

		min_index = grill_entropy.index(min( grill_entropy ))
		pivot = grill[min_index]
		criteria = values['values'] < pivot			# Take the best pivot and make the boolean vector of the left leaf
		data_count = sum(criteria & self.partition)
		if data_count < 3 or sum(self.partition)-data_count < 3: # To few data to split
			return (0,0)

		return (criteria, pivot)					# Return the pivot and vector.

	def plot(self):   # Future graphical plot. By now, print the data
		print(df[self.partition])
		return None


genetri = Genetreec(df)
genetri.train()

