import numpy as np
from random import seed
from ...Methods.graph import readNetworkFile
from ...Methods.sample import confInt
from ...Classes.ServiceDistribution import ServiceDistribution
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.SamplePath import SamplePath
from ...Simulation.boundingSystem import simulate

networkFile = "9x9//four.txt"
outputFile	= "eta.txt"

import os.path
basepath  = os.path.dirname(__file__)
filepath  = os.path.abspath(os.path.join(basepath, outputFile))

#################################################
# Basic inputs
T = 500 

#################################################
# Read service distributions from file
with open(os.path.dirname(__file__)+ '/' +  outputFile, 'r') as f:
	line  = f.readline().split()
	R     = int(line[0]) 
	M     = int(line[1])
	vals  = np.arange(1, R)
	cdfs  = np.empty((M, R))
	
	for r in xrange(R):
		line = f.readline().split()
		for m in xrange(M):
			cdfs[m][r] = float(line[m])

svcDists = {}
for m in xrange(M):
	pmf = cdfs[m][1:] - cdfs[m][:R-1]
	svcDists[m] = ServiceDistribution(vals, pmf)


##################################################
# Network, arrival patterns
svcArea   = readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
arrStream.updateP(0.28)
rndSeed	= 12345 
iters   = 100
simObj	= np.zeros(iters)

# Computing upper and lower bounds on a separate set of sample paths
seed(rndSeed)
for i in xrange(iters):
	omega	  = SamplePath(svcArea, arrStream, flagQ = False)
	simStats  = simulate(svcDists, omega)
	simObj[i] = simStats['obj']

print 'Maxwell\'s Upper Bound: %.3f +/- %.3f' % confInt(simObj)
