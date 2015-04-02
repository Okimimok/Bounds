class ServiceArea():
	# Comment inserted here!
	def __init__(self, nodes, bases, dist, maxDist):
		self.nodes	 = nodes
		self.bases	 = bases
		self.maxDist = maxDist
		self.__dist  = dist
		self.__buildB()
		self.__buildNBdist()
		self.__buildR()
				
	def __buildB(self):
		 # B[i] : bases that can respond to call at i within threshold,
		 #			sorted in order of distance from i	  
		 self.__B = {}
		 for i in self.nodes:
			 temp = sorted([(self.__dist[i][j], j) for j in self.bases \
							 if self.__dist[i][j] <= self.maxDist])
			 self.__B[i] = [k[1] for k in temp]
								 
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
			self.__NBdist[i] = self.__dist[i][self.__B[i][0]]
			
	def getNodes(self):
		return self.nodes
	
	def getBases(self):
		return self.bases
		
	def getMaxDist(self):
		return self.maxDist
			
	def getDist(self):
		return self.__dist

	def getNBdist(self):
		return self.__NBdist
		
	def getB(self):
		return self.__B
	
	def getR(self):
		return self.__R   
