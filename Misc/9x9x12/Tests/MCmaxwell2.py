import numpy as np
from random import seed
from ....Methods.network import readNetwork	
from os.path import abspath, dirname, realpath, join
from ....Methods.sample import confInt
from ....Upper.maxwell import readEta, readV
from ....Components.serviceDistribution import serviceDistribution
from ....Components.arrivalStream import arrivalStream
from ....Components.samplePath import samplePath
from ....Models import MMIP2

basePath    = dirname(realpath(__file__))
networkFile = "twelve.txt"
etaFile     = "eta.txt"
vFile       = "v.txt"
etaPath     = abspath(join(basePath, "..//Inputs//",  etaFile))
vPath       = abspath(join(basePath, "..//Inputs//",  vFile))
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))

# Distribution: ceil(Y), where Y ~ Exponential(1/24)
T = 1440

# Network, arrival patterns
svcArea   = readNetwork(networkPath)
A         = svcArea.A
arrStream = arrivalStream(svcArea, T)
arrStream.updateP(0.35)

# Service distributions for Maxwell's bounding system 
svcDists = readEta(etaPath)
v        = readV(vPath) 

# Arrival probabilities to be tested
N        = 1
seed1    = 67890
obj      = np.zeros(N)
settings = {'OutputFlag' : 1, 'MIPGap': 0.001, 'TimeLimit': 1}
	
seed(seed1)
# Matt Maxwell's upper bound
for i in xrange(N):
	omega  = samplePath(svcArea, arrStream, mxwDist=svcDists)
	QM     = omega.getQM()
	momo   = MMIP2.ModelInstance(svcArea, arrStream, omega, v)
	momo.solve(settings)
	obj[i] = momo.getObjective()
	print momo.getModel().Status, momo.getModel().MIPGap

print 'Maxwell Bound: %.3f +/- %.3f' % confInt(obj)
