import numpy as np
from os.path import abspath, dirname, realpath, join
from ....Upper.maxwell import buildEta, writeEta
from ....Methods.network import readNetwork	
from ....Components.arrivalStream import arrivalStream
from ....Components.serviceDistribution import serviceDistribution

basePath    = dirname(realpath(__file__))
etaFile     = "eta.txt"
networkFile = "four.txt"
etaPath     = join(basePath, etaFile) 
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))


# Distribution: ceil(Y), where Y ~ Exponential(1/24)
T	      = 2 
vals      = np.arange(12, 25, dtype='int64')
probs     = np.ones(13)/13.0
svcDist   = serviceDistribution(vals, probs)

# Network, arrival patterns
svcArea   = readNetwork(networkPath)
arrStream = arrivalStream(svcArea, T)
eta       = buildEta(svcArea, arrStream, svcDist, etaPath)
writeEta(eta, etaPath)
