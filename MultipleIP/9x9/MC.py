import numpy as np 
from random import seed
from ...Methods.graph import readNetworkFile
from ...Methods.sample import confInt
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
from ...Classes.PenaltyMultipliers import PenaltyMultipliers
from ...Classes.SamplePath import SamplePath
from ...MultipleIP import PIP2

networkFile = "9x9//four.txt"
randomSeed	= 33768

#####################################################
# Basic inputs
T		= 1440
vals    = np.arange(12, 25, dtype = 'int64')
probs   = np.ones(13)/13
svcDist = ServiceDistribution(vals, probs)

##################################################
# Network, arrival patterns
svcArea   = readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
arrStream.updateP(0.20)

##################################################
# Penalty Multipliers
gamma   = 0.05*np.ones(T+1)
penalty = PenaltyMultipliers(gamma)

##################################################
# Generating sample paths
N	   = 3 
ubObj  = np.zeros(N)
ubUtil = np.zeros(N)

seed(randomSeed)
for k in xrange(N):
	if (k+1)% 10 == 0:
		print 'Iteration %i' % (k+1)

	omega  = SamplePath(svcArea, arrStream, svcDist)
	
	# Solver settings
	settings = {'OutputFlag' : 0}	

	# Penalized IP 
	p = PIP2.ModelInstance(svcArea, arrStream, omega, gamma)
	p.solve(settings)
	ubObj[k]  = p.getObjective()
	ubUtil[k] = p.estimateUtilization()	

print 'Objective   : %.3f +/- %.3f' % confInt(ubObj)
print 'Utilization : %.3f +/- %.3f' % confInt(ubUtil)
