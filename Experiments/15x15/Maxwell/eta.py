import numpy as np
from math import exp
from os.path import abspath, dirname, realpath, join
from ....Upper.maxwell import buildEta, writeEta
from ....Methods.network import readNetwork	
from ....Components.ArrStream import ArrStream
from ....Components.SvcDist import SvcDist

basePath    = dirname(realpath(__file__))
etaFile     = "etaTenBall.txt"
networkFile = "tenBall.txt"
etaPath     = join(basePath, etaFile) 
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))


# Distribution: ceil(Y), where Y ~ Exponential(1/24)
T	      = 1440
mu        = 24.0
numVals   = 120
vals      = np.arange(1, numVals+1)
probs     = [exp(-(vals[i]-1)/mu)*(1 - exp(-1/mu))\
					 for i in range(numVals)]
probs[-1] += 1 - sum(probs)
sdist     = SvcDist(vals, probs)

# Network, arrival patterns
svca = readNetwork(networkPath)
astr = ArrStream(svca, T)
eta  = buildEta(svca, astr, sdist, etaPath, debug=True)
writeEta(eta, etaPath)
