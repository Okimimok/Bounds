import numpy as np
import time
from math import exp
from random import seed
from ...Methods.graph import readNetworkFile
from ...Methods.gradientSearch import solvePIPs, lineSearch
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
from ...Classes.PenaltyMultipliers import PenaltyMultipliers
from ...MultipleIP import PIP2

networkFile  = "9x9//four.txt"

#################################################
# Basic inputs
T		= 1440
# Distribution: ceil(Y), where Y ~ Exponential(1/34)
mu        = 30.0
numVals   = 180
vals      = np.arange(1, numVals+1)
probs     = [exp(-(vals[i]-1)/mu)*(1 - exp(-1/mu))\
					 for i in xrange(numVals)]
probs[-1] += 1 - sum(probs)
svcDist   = ServiceDistribution(vals, probs)

##################################################
# Network, arrival patterns
svcArea   = readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
arrStream.updateP(1 - exp(-0.05))

##################################################
# Penalty Multipliers
gamma	= np.zeros(T+1)
penalty = PenaltyMultipliers(gamma)
penalty.setStepSizes([0.5, 1.0, 2.0, 4.0])

##################################################
# Estimate objective value and gradient at current point
gradN	  = 100 
lineN	  = 100 
iters	  = 5 
randSeed  = 33768
settings = {'OutputFlag' : 0}

for i in xrange(iters):
	print '\nIteration %i' % (i + 1)
	
	# Sampling the gradient    
	print 'Estimating gradient...'
	gamma = penalty.getGamma()
	seed(randSeed)
	obj, nabla = solvePIPs(svcArea, arrStream, svcDist, gamma, PIP2,\
									 settings, gradN, freq=10)
	penalty.setNabla(nabla)

	print 'Line Search...'
	seed(randSeed)															
	vals = lineSearch(svcArea, arrStream, svcDist, penalty, PIP2,\
									 settings, lineN, freq=5) 
	print 'Done!'
	
	# Find best step size
	bestStep = 0
	bestVal  = np.mean(obj[:lineN])
	count	 = 0
	
	print 'Step Size 0, Mean Obj. %.4f' % bestVal
	for j in penalty.getStepSizes():
		print 'Step Size %.3f, Mean Obj. %.4f' % (j, vals[count])
		if vals[count] < bestVal:
			bestStep = j
			bestVal  = vals[count]
		count += 1
	print 'Best objective value : %.4f \n' % bestVal	
		
	# If step size is zero, take smaller steps. O/w, update gradient.
	if bestStep == 0:
		penalty.scaleGamma(0.5)
	else:
		penalty.updateGamma(-bestStep*nabla)

# Upon termination, sample the objective value at the point selected
print 'Computing final objective value...'	
seed(12345) 
endVals, _ = solvePIPs(svcArea, arrStream, svcDist, gamma, PIP2,\
									 settings, gradN, freq=10)
print 'Final upper bound: %.4f' % np.mean(endVals)
