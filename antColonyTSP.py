from sets import Set
from collections import defaultdict
from random import randint
import random
import networkx as nx

import matplotlib.pyplot as plt
#exponent coeficients
ALPHA = 1
beta = 1
EVAPORATION_RATE = 0.1
MONEY_LIMIT = 1000
INITIAL_MONEY = 1000

def randomPick(some_list, probabilities):
    x = random.uniform(0, 1)
    cumulative_probability = 0.0
    for item, item_probability in zip(some_list, probabilities):
        cumulative_probability += probabilities[item_probability]
        if x < cumulative_probability: break
    return item

class Ant(object):
	def __init__(self,city):
		self.visitedCities = Set()
		self.visitedEdges = Set()
		self.path = []
		self.travelledDistance = 0.0
		self.money = INITIAL_MONEY
		self.visitCity(city)
		self.startingCity = city
		self.pheromoneAmmount = float(1)/random.randint(1,10)
		self.hasReturned = False
		self.stuck = False

	def visitCity(self,city):
		self.visitedCities.add(city)
		self.currentCity = city
		self.path.append(city)

	def isCityVisited(self,city):
		return city in self.visitedCities

	def edgesForCurrentCity(self,allEdges):
		edgesForCurrentCity = {}
		for edge in allEdges:
			if (edge[0]==self.currentCity and not self.isCityVisited(edge[1]) and self.canMoveToCity(allEdges,edge[1])):
				edgesForCurrentCity[edge]=allEdges[edge]
		return edgesForCurrentCity

	def moveToNextEdge(self,allEdges):
		edgeProbability = {}
		myEdgesForCurrentCity = self.edgesForCurrentCity(allEdges)
		for edge in myEdgesForCurrentCity:
			value = myEdgesForCurrentCity[edge]
			dividend =  pow(value['visibility'],ALPHA) * pow(value['pheromone'],beta)
			divisor = 0
			otherEdges = myEdgesForCurrentCity
			for otherEdge in otherEdges:
				otherValue = otherEdges[otherEdge]
				divisor+= pow(otherValue['visibility'],ALPHA) * pow(otherValue['pheromone'],beta)
			edgeProbability[edge]=float(dividend)/divisor
		if (len(edgeProbability)==0):
			self.stuck = True
			return
		chosenEdge = randomPick(myEdgesForCurrentCity,edgeProbability)
		self.walkToEdge(chosenEdge,allEdges)
		

	def walkToEdge(self,edge,allEdges):
		value = allEdges[edge]
		value['pheromone']+=self.pheromoneAmmount
		self.visitCity(edge[1])
		self.money+=value['effect']
		self.travelledDistance+= value['distance']
		self.visitedEdges.add(edge)

	def hasVisitedAllCities(self,allCities):
		if (self.stuck):
			return True
		for city in allCities:
			if city not in self.visitedCities:
				return False
		return True
	
	def getPath(self):
		return self.path

	def returnToStartingCity(self,allEdges):
		self.visitedCities.remove(self.startingCity)
		self.moveToNextEdge(allEdges)
		self.hasReturned = True

	def evaporatePheromones(self,allEdges,edge):	
		value = allEdges[edge]	
		value['pheromone']=value['pheromone']*(1-EVAPORATION_RATE)
		allEdges[edge] = value

	def hasReturnedHome(self):
		return self.hasReturned

	def canMoveToCity(self,allEdges,city):
		edge = (self.currentCity,city)
		value = allEdges[edge]
		newMoney = self.money+value['effect']
		if (newMoney>MONEY_LIMIT or newMoney<0):
			return False
		return True

	def isStuck(self):
		return self.stuck

	def getTravelledDistance(self):
		return self.travelledDistance


	def getMoney(self):
		return self.money

	def hasVisitedPath(self,path):
		return path in self.visitedEdges

def evaporatePheromones(allPaths,ants):
	for a in ants:
		for path in allPaths:
			if a.hasVisitedPath(path):
				a.evaporatePheromones(allPaths,path)


def initMatrixAtIndexes(matrix,a,b,value,cities):
	matrix[a,b] = {'distance':value,'pheromone':1, 'visibility':float(1)/value}
	matrix[b,a] = {'distance':value,'pheromone':1, 'visibility':float(1)/value}
	matrix[a,b] ['effect']=cities[b]
	matrix[b,a] ['effect']=cities[a]

def main():
	cities = {}
	paths = defaultdict(int)
	ants = []

	#init city data
	with open('cities.txt') as cityFile:
		for line in cityFile:
			line = line.split() # to deal with blank 
			if line:
				cities[ line[0] ] = int(line[1])

	numberOfAnts = int(len(cities)*1.5)

	numberOfIterations = 10
	optimalDistance = 1000000
	optimalPath = []
	money = 0
	

	for i in range(numberOfIterations):
			#init distance data
		with open('distances.txt') as distanceFile:
			for line in distanceFile:
				line = line.split()
				if line:
					initMatrixAtIndexes(paths,line[0],line[1],int(line[2]),cities)

		ALPHA = random.randint(1,1)
		BETA = random.randint(1,1)
		#EVAPORATION_RATE = random.random()
		ants = []
		for i in range(numberOfAnts):
			a = Ant('INITIAL')
			ants.append(a)

		for a in ants:
			#Tour until stuck or until visited all cities
			for i in range(len(cities)):
				if not a.hasVisitedAllCities(cities) and not a.isStuck():
					evaporatePheromones(paths,ants)
					a.moveToNextEdge(paths)
				elif not a.hasReturnedHome() and not a.isStuck():
					evaporatePheromones(paths,ants)
					a.returnToStartingCity(paths)
			if (a.getTravelledDistance()<optimalDistance and not a.isStuck()):
				optimalPath = a.getPath()
				optimalDistance = a.getTravelledDistance()
				money = a.getMoney()		
	g=nx.DiGraph()
		
	for i in range (len(optimalPath)-1):
		g.add_weighted_edges_from([(optimalPath[i],optimalPath[i+1],paths[(optimalPath[i],optimalPath[i+1])]['distance'])])
	nx.draw_spring(g)
	plt.savefig("file.png")
	nx.write_dot(g,'file.dot')
	print optimalDistance, optimalPath, money

main()