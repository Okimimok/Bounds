import numpy as np
from math import exp
from ...Methods import  readFiles
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
from ...MultipleIP import PIP2 
from ...MaxwellIP import getEta

etaFile     = "eta.txt"
networkFile = "15x15//five.txt"
import os.path
basepath = os.path.dirname(__file__)
etaPath  = os.path.join(basepath, etaFile) 
print etaPath

# Distribution: ceil(Y), where Y ~ Exponential(1/24)
T	      = 1440
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
getEta.solveIPs(svcArea, arrStream, svcDist, etaPath)

