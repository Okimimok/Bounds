import numpy as np

class StationaryArrivalStream():
	def __init__(self, svcArea, T):
		self.T	   = T
		self.__svcArea = svcArea
		self.__buildP()
		self.__buildPN()
		self.__buildRP()
		self.__buildRPN()
				
	def __buildP(self):
		# P[t][i] = Probability of call arrival to node i at time t
		# By default, no arrivals at time zero. Start-up period.
		self.__P = np.zeros((self.T + 1, len(self.__svcArea.nodes)))
		for t in xrange(1, self.T + 1):
			for i in self.__svcArea.nodes:
				self.__P[t][i] = self.__svcArea.nodes[i]['prob']

	def __buildPN(self):
		# PN[t][i] = Probability of call arrival to node i at time t,
		# conditional on a call arriving. (E.g., the matrix P, normalized)
		self.__PN  = np.zeros((self.T + 1, len(self.__svcArea.nodes)))
		for t in xrange(1, self.T + 1):
			temp = sum(self.__P[t])
			for i in self.__svcArea.nodes:
				self.__PN[t][i] = self.__P[t][i]/temp
			
	def __buildRP(self):
		# RP[t][j] = Probability that ambulance at base j can respond to
		#	call arrival at time t
		R = self.__svcArea.getR()
		
		self.__RP = np.zeros((self.T + 1, len(self.__svcArea.bases)))
		for t in xrange(self.T + 1):
			for j in self.__svcArea.bases:
				self.__RP[t][j] = sum(self.__P[t][i] for i in R[j])

	def __buildRPN(self):
		# RPN[t][j] = Similar to RP above, but with the sum taken over 
		#	elements of PN rather than P.
		R = self.__svcArea.getR()
		
		self.__RPN = np.zeros((self.T + 1, len(self.__svcArea.bases)))
		for t in xrange(self.T + 1):
			for j in self.__svcArea.bases:
				self.__RPN[t][j] = sum(self.__PN[t][i] for i in R[j])
		
	def updateP(self, factor):
		# Update the arrival probability matrix P by scaling the normalized
		#	matrix PN by a constant factor (requires updating RP)
		self.__P = factor*self.__PN	
		self.__buildRP()

	def getP(self):
		return self.__P

	def getPN(self):
		return self.__PN
	
	def getRP(self):
		return self.__RP
		
	def getRPN(self):
		return self.__RPN
