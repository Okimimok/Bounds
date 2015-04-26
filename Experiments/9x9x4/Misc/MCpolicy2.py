import numpy as np 
from random import seed
from ....Methods.network import readNetwork	
from os.path import abspath, dirname, realpath, join
from ....Methods.sample import confInt
from ....Lower.compliance import readTable
from ....Components.serviceDistribution import serviceDistribution
from ....Components.arrivalStream import arrivalStream
from ....Components.samplePath import samplePath
from ....Models import MMIP2
from ....Simulation.lowerAll import simulate as simLB
from ....Simulation.policies import nearestEffEmpty

basePath    = dirname(realpath(__file__))
networkFile = "four.txt"
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))

T	    = 1440
vals    = np.arange(12, 25, dtype = 'int64')
probs   = np.ones(13)/13
svcDist = serviceDistribution(vals, probs)

# Network, arrival patterns
svcArea   = readNetwork(networkPath)
A         = svcArea.A
arrStream = arrivalStream(svcArea, T)
arrStream.updateP(0.07)

# Generating sample paths
N     = 50
seed1 = 12345
obj   = np.zeros(N)
seed(seed1)
for k in xrange(N):
	omega   = samplePath(svcArea, arrStream, svcDist)
	lbStats = simLB(svcArea, omega, lambda simState, location, fel, svcArea:\
				nearestEffEmpty(simState, location, fel, svcArea))
	obj[k]  = lbStats['obj']

print 'Objective  : %.3f +/- %.3f' % confInt(obj)

