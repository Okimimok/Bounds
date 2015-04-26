import numpy as np
from random import seed
from ....Methods.network import readNetwork	
from os.path import abspath, dirname, realpath, join
from ....Methods.sample import confInt
from ....Upper.maxwell import readEta, readV
from ....Components.serviceDistribution import serviceDistribution
from ....Components.arrivalStream import arrivalStream
from ....Components.samplePath import samplePath
from ....Simulation.upperMaxwell import simulate as simUB

basePath    = dirname(realpath(__file__))
networkFile = "four.txt"
etaFile     = "eta.txt"
vFile       = "v.txt"
etaPath     = abspath(join(basePath, "..//Inputs//",  etaFile))
vPath       = abspath(join(basePath, "..//Inputs//",  vFile))
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))

# Distribution: ceil(Y), where Y ~ Exponential(1/24)
T	    = 1440

# Network, arrival patterns
svcArea   = readNetwork(networkPath)
A         = svcArea.A
arrStream = arrivalStream(svcArea, T)
arrStream.updateP(0.07)

# Service distributions for Maxwell's bounding system 
svcDists = readEta(etaPath)
v        = readV(vPath) 

# Arrival probabilities to be tested
N     = 50
seed1 = 12345
obj   = np.zeros(N)
	
seed(seed1)
# Matt Maxwell's upper bound
for i in xrange(N):
	omega   = samplePath(svcArea, arrStream, mxwDist=svcDists)
	mxStats = simUB(svcDists, omega, A, v)
	obj[i]  = mxStats['obj']

print 'Maxwell Bound: %.3f +/- %.3f' % confInt(obj)
