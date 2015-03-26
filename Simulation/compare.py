import numpy as np
from simulation import simulate
from random import seed
from ..Methods.graph import readNetworkFile
from ..Methods.sample import confInt
from ..Classes.StationaryArrivalStream import StationaryArrivalStream
from ..Classes.SamplePath import SamplePath
import policies
networkFile  = "9x9//four.txt"


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
arrStream.updateP(0.16)

##################################################
# Estimate objective value and gradient at current point
numPaths = 100
randSeed = 12345
naive    = np.zeros(numPaths)
near     = np.zeros(numPaths)
nearEm   = np.zeros(numPaths)
nearEfEm = np.zeros(numPaths)

seed(randSeed)
for i in xrange(numPaths):    
    omega       = SamplePath(svcArea, arrStream, svcDist)
    naive[i]    = simulate(svcArea, omega, policies.naive)
    near[i]     = simulate(svcArea, omega, policies.nearest)
    nearEm[i]   = simulate(svcArea, omega, policies.nearestEmpty)
    nearEfEm[i] = simulate(svcArea, omega, policies.nearestEffEmpty)

print 'Naive Policy       : %.3f +/- %.3f' % confInt(naive)
print 'Nearest Policy     : %.3f +/- %.3f' % confInt(near)
print 'Nearest Empty      : %.3f +/- %.3f' % confInt(nearEm)
print 'Nearest Eff. Empty : %.3f +/- %.3f' % confInt(nearEfEm)
