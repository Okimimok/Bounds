import numpy as np
from random import seed
from ...Methods.graph import readNetworkFile
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.PenaltyMultipliers import PenaltyMultipliers
from ...Classes.SamplePath import SamplePath
from ...ValidIP import PIPValid
from ...MultipleIP import PIP2

networkFile = "9x9//five.txt"
randomSeed  = 33767

#################################################
# Basic inputs
T       = 1440
svcDist = {}
for i in xrange(12, 25):
    svcDist[i] = 1.0/13

##################################################
# Network, arrival patterns
svcArea   = readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
arrStream.updateP(0.18)

##################################################
# Penalty Multipliers
gamma   = 0.2*np.ones(T+1)
#gamma   = np.zeros(T+1)
penalty = PenaltyMultipliers(gamma)

##################################################
# Generating sample paths
iters = 1
ub    = np.zeros(iters)
rt    = np.zeros(iters)

seed(randomSeed)
for k in xrange(iters):
    print 'Iteration %i' % (k+1)
    omega  = SamplePath(svcArea, arrStream, svcDist)
    
    # Penalized IP w/ valid inequalities and warm start
    ub[k], rt[k] = PIPValid.solve(svcArea, arrStream, omega, penalty, warm=True,\
			 flag=True, solver=lambda svcArea, arrStream, omega, penalty:\
				 PIP2.solve(svcArea, arrStream, omega, penalty, soln=True))
    
print 'Average Runtime: %.2f seconds' % np.average(rt)
