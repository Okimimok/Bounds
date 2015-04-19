import numpy as np 
import time
from random import seed
from math import exp
from ...Methods.graph import readNetworkFile
from ...Methods.sample import confInt
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
from ...Classes.PenaltyMultipliers import PenaltyMultipliers
from ...Classes.SamplePath import SamplePath
from ...MultipleIP import PIP2

networkFile = "15x15//five.txt"
randomSeed	= 33768

#####################################################
# Basic inputs
T		= 1440
# Distribution: ceil(Y), where Y ~ Exponential(1/34)
mu        = 24.0
numVals   = 120
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
gamma   = 0*np.ones(T+1)
penalty = PenaltyMultipliers(gamma)

##################################################
# Generating sample paths
N	   = 50 
ubObj  = np.zeros(N)
ubUtil = np.zeros(N)

start = time.clock()
seed(randomSeed)
for k in xrange(N):
	if (k+1)% 10 == 0:
		print 'Iteration %i' % (k+1)

	omega  = SamplePath(svcArea, arrStream, svcDist)
	
	# Solver settings
	settings = {'OutputFlag' : 0}	

	# Penalized IP 
	p = PIP2.ModelInstance(svcArea, arrStream, omega)
	p.updateObjective(gamma)
	p.solve(settings)
	ubObj[k]  = p.getObjective()
	ubUtil[k] = p.estimateUtilization()	
finish = time.clock()

print 'Objective   : %.3f +/- %.3f' % confInt(ubObj)
print 'Utilization : %.3f +/- %.3f' % confInt(ubUtil)
print 'Took %.3f seconds' % (finish-start)
