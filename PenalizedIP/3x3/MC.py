import sys
import numpy as np
from random import seed
from ...Methods.graph import readNetworkFile
from ...Methods.sample import confInt
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.PenaltyMultipliers import PenaltyMultipliers
from ...Classes.SamplePath import SamplePath
from ...PenalizedIP import PIP

networkFile = "3x3//two.txt"
randomSeed	= 33768

##################################################
# Basic inputs
T       = 1440
svcTime = {}
for i in xrange(12, 25):
    svcTime[i] = 1.0/13

##################################################
# Extract information from network file
svcArea = readNetworkFile(networkFile)

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
# Penalty Multipliers
gamma   = 0.05*np.ones(T+1)
penalty = PenaltyMultipliers(gamma)

##################################################
# Generating sample paths
N   = 1
obj = np.zeros(N)
seed(randomSeed)

for k in xrange(N):
	if (k+1)% 10 == 0:
		print 'Iteration %i' % (k+1)
	
	# Penalized IP
	omega  = SamplePath(svcArea, arrStream, svcDist)
	obj[k], _ = PIP.solve(svcArea, arrStream, omega, penalty)
	
print 'Penalized IP : %.3f +/- %.3f' % confInt(obj)
