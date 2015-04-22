import numpy as np
from math import exp
from os.path import abspath, dirname, realpath, join
from ....Upper.maxwell import buildEta, writeEta
from ....Methods.network import readNetwork	
from ....Components.arrivalStream import arrivalStream
from ....Components.serviceDistribution import serviceDistribution

basePath    = dirname(realpath(__file__))
etaFile     = "eta.txt"
networkFile = "five.txt"
etaPath     = join(basePath, etaFile) 
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))


# Distribution: ceil(Y), where Y ~ Exponential(1/24)
T	      = 1440
mu        = 24.0
numVals   = 120
vals      = np.arange(1, numVals+1)
probs     = [exp(-(vals[i]-1)/mu)*(1 - exp(-1/mu))\
					 for i in xrange(numVals)]
probs[-1] += 1 - sum(probs)
svcDist   = serviceDistribution(vals, probs)

# Network, arrival patterns
svcArea   = readNetwork(networkPath)
arrStream = arrivalStream(svcArea, T)
eta       = buildEta(svcArea, arrStream, svcDist, etaPath, debug=True)
writeEta(eta, etaPath)
