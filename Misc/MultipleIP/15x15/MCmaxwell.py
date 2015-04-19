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
vFile       = "v.txt"

import os.path
basepath = os.path.dirname(__file__)
etaPath  = os.path.join(basepath, etaFile) 
vPath    = os.path.join(basepath, vFile)

# Network, arrival patterns
T         = 1440
svcArea   = readFiles.readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
arrStream.updateP(0.10)

# Service distributions for Maxwell's bounding system 
svcDists = readFiles.readEtaFile(etaPath)
v        = {}
with open(vPath, 'r') as f:
	A = int(f.readline())
	for a in xrange(1, A+1):
		line = f.readline().split()
		v[a] = float(line[1])

# Arrival probabilities to be tested
N     = 100
seed1 = 12345
obj   = np.zeros(N)
	
seed(seed1)
# Matt Maxwell's upper bound
for i in xrange(N):
	omega   = SamplePath(svcArea, arrStream, svcDists)
	mxStats = simUB(svcDists, omega, A, v)
	obj[i]  = mxStats['obj']

print 'Maxwell Bound: %.3f +/- %.3f' % confInt(obj)
