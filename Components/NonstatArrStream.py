import numpy as np

# Nonstationary arrival stream.
# Takes as input
#
# 1) Horizon length T
# 2) svcArea
# 3) Vector of C changepoints (first entry 1, as no arrivals at time 0, 
#      last entry the last change point before end of horizon)
# 4) C x |N| array probs, where probs[c][i] = P(Arrival to i during phase c)
#
# Otherwise functions identically to ArrStream

class NonstatArrStream():
	def __init__(self, svcArea, T, chgPts, probs):
		self.T	        = T
		self.C         = len(chgPts)
		self.__chgPts  = chgPts
		np.append(self.__chgpts, T+1)
		self.probs     = probs
		self.__svcArea = svcArea
		self.__buildP()
		self.__buildPN()
		self.__buildRP()
		self.__buildRPN()
		self.__arrProb = 1.0
				
	def __buildP(self):
		# P[t][i] = Probability of call arrival to node i at time t
		# By default, no arrivals at time zero. Start-up period.
		self.__P = np.zeros((self.T + 1, len(self.__svcArea.nodes)))
		for c in range(self.C):
			for t in range(self.__chgPts[c], self.__chgPts[c+1]):
				for i in self.__svcArea.nodes:
					self.__P[t][i] = self.probs[c][i]
			
	def __buildPN(self):
		# PN[t][i] = Probability of call arrival to node i at time t,
		# conditional on a call arriving. (E.g., the matrix P, normalized)
		self.__PN  = np.zeros((self.T + 1, len(self.__svcArea.nodes)))
		for t in range(1, self.T + 1):
			temp = sum(self.__P[t])
			for i in self.__svcArea.nodes:
				self.__PN[t][i] = self.__P[t][i]/temp
			
	def __buildRP(self):
		# RP[t][j] = Probability that ambulance at base j can respond to
		#	call arrival at time t
		R = self.__svcArea.getR()
		
		self.__RP = np.zeros((self.T + 1, len(self.__svcArea.bases)))
		for t in range(self.T + 1):
			for j in self.__svcArea.bases:
				self.__RP[t][j] = sum(self.__P[t][i] for i in R[j])

	def __buildRPN(self):
		# RPN[t][j] = Similar to RP above, but with the sum taken over 
		#	elements of PN rather than P.
		R = self.__svcArea.getR()
		
		self.__RPN = np.zeros((self.T + 1, len(self.__svcArea.bases)))
		for t in range(self.T + 1):
			for j in self.__svcArea.bases:
				self.__RPN[t][j] = sum(self.__PN[t][i] for i in R[j])
		
	def updateP(self, p):
		# Update the arrival probability matrix P by scaling the normalized
		#	matrix PN by a constant factor (requires updating RP)
		self.__P = p*self.__PN	
		self.__buildRP()
		self.__arrProb = p

	def getP(self):
		return self.__P

	def getPN(self):
		return self.__PN
	
	def getRP(self):
		return self.__RP
		
	def getRPN(self):
		return self.__RPN

	def getArrProb(self):
		return self.__arrProb
