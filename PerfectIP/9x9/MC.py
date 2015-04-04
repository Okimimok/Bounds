import numpy as np
from random import seed
from ...Methods.graph import readNetworkFile
from ...Methods.sample import confInt
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
from ...Classes.PenaltyMultipliers import PenaltyMultipliers
from ...Classes.SamplePath import SamplePath
from ...PerfectIP import IP

networkFile = "9x9//four.txt"
randomSeed	= 33768

#################################################
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
# Generating sample paths
N	   = 3
piObj  = np.zeros(N)
piUtil = np.zeros(N)

seed(randomSeed)
for k in xrange(N):
	if (k+1)% 10 == 0:
		print 'Iteration %i' % (k+1)
	omega  = SamplePath(svcArea, arrStream, svcDist)
	
	# Solver settings
	settings = {'OutputFlag' : 0}	

	# Perfect Information  IP 
	p = IP.ModelInstance(svcArea, arrStream, omega)
	p.solve(settings)
	piObj[k]  = p.getObjective()	
	piUtil[k] = p.estimateUtilization()	

print 'Objective : %.3f +/- %.3f' % confInt(piObj)
print 'Utilization : %.3f +/- %.3f' % confInt(piUtil)
