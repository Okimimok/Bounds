import numpy as np

class SvcArea():
	# Comment inserted here!
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> a1261b4... New home for eta and v
	def __init__(self, nodes, bases, Tunit, Tresp):
		# Tunit : Time needed (min.) to travel one unit in the network
		# Tresp : Response time threshold
		self.nodes = nodes
		self.bases = bases
		self.A     = sum([bases[j]['ambs'] for j in bases])
		self.Tunit = Tunit
		self.Tresp = Tresp
<<<<<<< HEAD
=======
	def __init__(self, nodes, bases, Tresp):
		self.nodes	  = nodes
		self.bases	  = bases
		self.A        = sum([bases[j]['ambs'] for j in bases])
		self.Tresp  = Tresp
>>>>>>> 286f77c... Continuous coordinates
=======
>>>>>>> a1261b4... New home for eta and v
		self.__buildDist()
		self.__buildB()
		self.__buildNBdist()
		self.__buildR()
				
	def __buildDist(self):
		# Build distance matrix between nodes (rows) and bases (columns)
		nodes = self.nodes
		bases = self.bases
		I     = len(nodes)
		J     = len(bases)
		self.dist = np.empty((I, J))
		for i in range(I):
			for j in range(J):
				self.dist[i][j] = self.distance(nodes[i]['loc'], bases[j]['loc'])

	def __buildB(self):
		 # B[i] : bases that can respond to call at i within threshold,
		 #			sorted in order of distance from i	  
		 # BA[i] : same for all bases, not just those within reach of i
		 self.__B  = {}
		 self.__BA = {}
		 for i in self.nodes:
			 temp = sorted([(self.dist[i][j], j) for j in self.bases]) 
			 self.__BA[i] = [k[1] for k in temp]
			 self.__B[i]  = [k[1] for k in temp if k[0] <= self.Tresp]
								 
	def __buildR(self):
		# R[j] = Set of demand nodes to which base j response possible
		self.__R = {}
		for j in self.bases:
			self.__R[j] = [i for i in self.nodes if j in self.__B[i]]

	def __buildNBdist(self):
		# distNBDist[i] = Distance from node i to nearest base
		# The bases in B have already been sorted in order of increasing
		#	distance from i, so just need to get first element of B[i]
		self.__NBdist = {}
		for i in self.nodes: 
			self.__NBdist[i] = self.dist[i][self.__BA[i][0]]

	def distance(self, x, y):
<<<<<<< HEAD
<<<<<<< HEAD
		# Outputs Manhattan travel time (min.) between two pts in the network 
		return (abs(x[0] - y[0]) + abs(x[1] - y[1]))*self.Tunit
=======
		# Outputs Manhattan distance between two points x and y in R^2
		return abs(x[0] - y[0]) + abs(x[1] - y[1])
>>>>>>> 286f77c... Continuous coordinates
=======
		# Outputs Manhattan travel time (min.) between two pts in the network 
		return (abs(x[0] - y[0]) + abs(x[1] - y[1]))*self.Tunit
>>>>>>> a1261b4... New home for eta and v
			
	def getNodes(self):
		return self.nodes
	
	def getBases(self):
		return self.bases
		
	def getMaxDist(self):
		return self.Tresp
			
	def getDist(self):
		return self.dist

	def getNBdist(self):
		return self.__NBdist
		
	def getB(self):
		return self.__B

	def getBA(self):
		return self.__BA
	
	def getR(self):
		return self.__R   
