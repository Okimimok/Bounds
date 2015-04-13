import numpy as np
import time
from math import exp
from random import seed
from ...Methods.sample import confInt
from ...Methods import readFiles
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
from ...Classes.SamplePath import SamplePath
from ...Simulation.boundingSystem import simulate as simUB

networkFile = "15x15//five.txt"
etaFile     = "eta.txt"

import os.path
basepath = os.path.dirname(__file__)
etaPath  = os.path.join(basepath, etaFile) 

# Distribution: ceil(Y), where Y ~ Exponential(1/24)
T	      = 100
mu        = 24.0
numVals   = 120
vals      = np.arange(1, numVals+1)
probs     = [exp(-(vals[i]-1)/mu)*(1 - exp(-1/mu))\
					 for i in xrange(numVals)]
probs[-1] += 1 - sum(probs)
svcDist   = ServiceDistribution(vals, probs)

# Network, arrival patterns
svcArea   = readFiles.readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
arrStream.updateP(0.10)

# Service distributions for Maxwell's bounding system 
svcDists = readFiles.readEtaFile(etaPath)

# Arrival probabilities to be tested
N     = 1
seed1 = 12345
obj   = np.zeros(N)
	
seed(seed1)
# Matt Maxwell's upper bound
for i in xrange(N):
	omega   = SamplePath(svcArea, arrStream, svcDist)
	mxStats = simUB(svcDists, omega, debug=True)
	obj[i]  = mxStats['obj']

print 'Maxwell Bound: %.3f +/- %.3f' % confInt(obj)
