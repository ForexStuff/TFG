# Here it will be developed the genetic algorithm with a population of 'trees' and a fitness function using backtrader
from tree import Genetreec as gentree
import tagger
import indicator
import pandas as pd

#tagger.acumtag()   #Just needed one time, data tagged is saved between executions
data = pd.read_csv('tagged_data/SAN.csv')


tree = gentree(data)
tree.train()
