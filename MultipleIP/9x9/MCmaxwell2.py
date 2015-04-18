import numpy as np
from random import seed
from ...Methods.sample import confInt
from ...Methods import readFiles
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
from ...Classes.SamplePath import SamplePath
from ...MaxwellIP import MMIP2

networkFile = "9x9//four.txt"
etaFile     = "eta.txt"
vFile       = "v.txt"

import os.path
basepath = os.path.dirname(__file__)
etaPath  = os.path.join(basepath, etaFile) 
vPath    = os.path.join(basepath, vFile)

# Distribution: ceil(Y), where Y ~ Exponential(1/24)
T = 1440

# Network, arrival patterns
svcArea   = readFiles.readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
arrStream.updateP(0.07)

# Service distributions for Maxwell's bounding system 
svcDists = readFiles.readEtaFile(etaPath)
v        = {}
with open(vPath, 'r') as f:
	A = int(f.readline())
	for a in xrange(1, A+1):
		line = f.readline().split()
		v[a] = float(line[1])

# Arrival probabilities to be tested
N        = 50
seed1    = 12345
obj      = np.zeros(N)
cas      = np.zeros(N)
settings = {'OutputFlag' : 0}
	
seed(seed1)
# Matt Maxwell's upper bound
for i in xrange(N):
	omega = SamplePath(svcArea, arrStream, svcDists)
	QM = omega.getQM()
	momo  = MMIP2.ModelInstance(svcArea, arrStream, omega, v)
	momo.solve(settings)
	obj[i] = momo.getObjective()

print 'Maxwell Bound: %.3f +/- %.3f' % confInt(obj)
