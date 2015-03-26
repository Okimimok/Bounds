import numpy as np
from random import seed

import sys
sys.path.append("Z:\\Redeployment Bounds Project\\Methods\\")
from graph import readNetworkFile
from sample import confInt

sys.path.append("Z:\\Redeployment Bounds Project\\Classes\\")
from StationaryArrivalStream import StationaryArrivalStream
from SamplePath import SamplePath
from PenaltyMultipliers import PenaltyMultipliers

sys.path.append("Z:\\Redeployment Bounds Project\\PenalizedIP")
import PIP

sys.path.append("Z:\\Redeployment Bounds Project\\PenalizedIPValid")
import PIPValid

#networkFile = "3by3Network.txt"
#DPobj = 88.6453
networkFile = "9by9Network.txt"
#DPobj       = 82.2092389004
randomSeed  = 66025

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

##################################################
# Penalty Multipliers
gamma   = 0.4*np.ones(T+1)
#gamma   = np.zeros(T+1)
penalty = PenaltyMultipliers(gamma)

##################################################
# Generating sample paths
iters   = 1
PIPobj  = np.zeros(iters)
PIPVobj = np.zeros(iters)

seed(randomSeed)
for k in xrange(iters):
    print 'Iteration %i' % (k+1)
    omega  = SamplePath(svcArea, arrStream, svcDist)
    
    # Perfect information relaxation
    #PIPobj[k], _ = PIP.solve(svcArea, arrStream, omega, penalty,\
    #                            flag=True)
    
    # Penalized IP
    PIPVobj[k], _ = PIPValid.solve(svcArea, arrStream, omega, penalty,\
                                flag=True)
    
print ''
#print 'Stochastic DP       : %.3f'          % DPobj
print 'Perfect Information : %.3f +/- %.3f' % confInt(PIPobj, 0.95)
print 'Penalized IP        : %.3f +/- %.3f' % confInt(PIPVobj, 0.95)