class Genetreec:
	root  #first Node

	def __init__(self,data):
		self.root = Leaf(data)
		
	def train(self, data):
		

	def test(self, data):
		


class Node:
	feature = None  #column to split the data
	pivot = None    #value to split the data

	right = None   #node or leaf positive
	left = None    #node or leaf negative

	def __init__(self, feature, pivot):
		self.feature = feature
		self.pivot = pivot

class Leaf:
	tag = None   #the final tag the data on the leaf will be classificated as (Used just when trained)
	data = None  #the partition of data which verifies the branch's nodes restrictions

	def __init__(self, data):


