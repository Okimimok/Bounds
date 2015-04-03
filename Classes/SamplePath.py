from ..Methods.sample import discreteN
from random import random

class SamplePath():
	def __init__(self, svcArea, arrStream, svcDist = None, flagQ = True):
		self.T = arrStream.T		
		self.svcDist = svcDist
		self.__buildCalls(arrStream, svcDist)
		if flagQ:
			self.__buildQ(svcArea)
	
	def __buildCalls(self, arrStream, svcDist):
		# Generate sample path of calls
		self.__calls = {}
		P = arrStream.getP()
	
		for t in xrange(self.T + 1):
			# Call pmf at time t
			callLoc = discreteN(P[t])
		
			if callLoc != 'null':
				r = random()
				self.__calls[t]		   = {}
				self.__calls[t]['loc'] = callLoc
				self.__calls[t]['rnd'] = r
				if svcDist:
					self.__calls[t]['svc'] = svcDist.sample(r)
		
	def __buildQ(self, svcArea):
		# Q[t][j] : Set of dispatch-redeploy decisions (s, k), such that
		#	  a dispatch from k to time s results in amb becoming free
		#	  before time t at node j
		self.__Q = {}
		B = svcArea.getB()
		dist = svcArea.getDist()

		for t in xrange(self.T + 1):
			self.__Q[t] = {}
			for j in svcArea.bases:
				self.__Q[t][j] = []

		for c in self.__calls:
			arr = self.__calls[c]['loc']
			svc = self.__calls[c]['svc']
		
			for j in B[arr]:
				for k in svcArea.bases:
					busy  = svc + dist[arr][j] + dist[arr][k]
					ready = c + busy
					if ready <= self.T:
						self.__Q[ready][k].append((c, j))
		
	def getCalls(self):
		return self.__calls
	
	def getQ(self):
		return self.__Q
		
