import numpy as np

class SvcDist:
	# For all things related to the service time distribution. 
	#	Pmf, cdf, random variate generation. Initialized with two
	#	vectors: vals (which contains the support) and probs (the
	#	corresponding probabilities) 
	#
	# Assumed that support already sorted in increasing order. 

	def __init__(self, vals, probs):
		self.support = vals
		self.pmf	 = probs

		# Size of support, min and max values
		self.__N	  = len(vals)
		self.__minVal = vals[0]
		self.__maxVal = vals[-1]
		self.__buildCumul()
		self.__buildCDF()
		self.__computeMean()

	def __buildCumul(self):
		# Builds a vector containing the cdf evaulated only at
		#	the breakpoints
		self.__cumul = np.zeros(self.__N)
		self.__cumul[0] = self.pmf[0]

		for i in range(1, self.__N):
			self.__cumul[i] = self.__cumul[i-1] + self.pmf[i]
			
	def __buildCDF(self):
		# Builds a cdf, but defined only from zero to the
		#	maximum value in the support
		self.__cdf     = np.zeros(self.__maxVal+1)
		self.__cdf[-1] = 1
		for i in range(self.__N - 1):
			left  = self.support[i]
			right = self.support[i+1]
			self.__cdf[left:right] = self.__cumul[i]	

	def sample(self, r):
		# Given a number 0 <= r <= 1, returns Finv(r). Can
		# 	be used to generate a sample from this distribution	
		#   if r a sample from a Uniform(0, 1) RV.
		# Bisection search!
		left  = 0
		right = self.__N  - 1 
		
		while left < right:
			test = (left+right)/2
			if r > self.__cumul[test]:
				left = test + 1
			else:
				right = test

		return self.support[left]

	def getCDF(self):
		return self.__cdf
		  
	def getCumul(self):
		return self.__cumul

	def __computeMean(self):
		self.mean = sum([self.pmf[i]*self.support[i] for i in range(self.__N)])

	def evalCDF(self, x):
		# Given x, computes F(x)
		if x <= 0:
			val = 0
		elif x >= self.__maxVal:
			val = 1
		else:
			val = self.__cdf[int(x)]

		return val
  
