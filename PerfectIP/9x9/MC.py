import numpy as np
from random import seed
from ...Methods.graph import readNetworkFile
from ...Methods.sample import confInt
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.PenaltyMultipliers import PenaltyMultipliers
from ...Classes.SamplePath import SamplePath
from ...PerfectIP import IP

networkFile = "9x9//four.txt"
randomSeed	= 33768

#################################################
# Basic inputs
T		= 1440
svcDist = {}
for i in xrange(12, 25):
	svcDist[i] = 1.0/13

##################################################
# Network, arrival patterns
svcArea   = readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
arrStream.updateP(0.20)

##################################################
# Generating sample paths
N	  = 100
piobj = np.zeros(N)


seed(randomSeed)
for k in xrange(N):
	if (k+1)% 10 == 0:
		print 'Iteration %i' % (k+1)

	omega  = SamplePath(svcArea, arrStream, svcDist)
	
	# Penalized IP w/ valid inequalities and warm start
	piobj[k], _ = IP.solve(svcArea, arrStream, omega)
	
print 'PI Relaxation : %.3f +/- %.3f' % confInt(piobj)
