import numpy as np
import time
from math import exp
from random import seed
from ...Methods.readFiles import readNetworkFile
from ...Methods.gradientSearch import fullSearch, solvePIPs
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
from ...Classes.PenaltyMultipliers import PenaltyMultipliers
from ...MultipleIP import PIP2

networkFile  = "15x15//five.txt"

#################################################
# Basic inputs
T	      = 1440
# Distribution: ceil(Y), where Y ~ Exponential(1/34)
mu        = 24.0
numVals   = 120
vals      = np.arange(1, numVals+1)
probs     = [exp(-(vals[i]-1)/mu)*(1 - exp(-1/mu))\
					 for i in xrange(numVals)]
probs[-1] += 1 - sum(probs)
svcDist   = ServiceDistribution(vals, probs)

# Network, arrival patterns
svcArea   = readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
arrStream.updateP(1 - exp(-0.05))

# Penalty Multipliers
gamma	= np.zeros(T+1)
penalty = PenaltyMultipliers(gamma)
penalty.setStepSizes([0.5, 1.0, 2.0, 4.0])

# Estimate objective value and gradient at current point
N        = 50 
iters	 = 1 
seed1    = 33768
seed2    = 12345
settings = {'OutputFlag' : 0}

# Gradient search, then sample the objective value for the penalty selected
fullSearch(svcArea, arrStream, svcDist, penalty, PIP2, settings, N,	seed1,\
					 iters, debug=True)
print 'Computing final objective value...'	
seed(seed2)
endVals, _ = solvePIPs(svcArea, arrStream, svcDist, gamma, PIP2, settings, N)
print 'Final upper bound: %.4f' % np.mean(endVals)
