import numpy as np
from random import seed
from ....Methods.network import readNetwork	
from os.path import abspath, dirname, realpath, join
from ....Methods.sample import confInt
from ....Lower.compliance import readTable
from ....Upper.maxwell import readEta, readV
from ....Components.serviceDistribution import serviceDistribution
from ....Components.arrivalStream import arrivalStream
from ....Components.samplePath import samplePath
from ....Simulation.lowerAll import simulate as simLB
from ....Simulation.tablePolicies import compliance
from ....Models import MMIP2

basePath    = dirname(realpath(__file__))
networkFile = "twelve.txt"
etaFile     = "eta.txt"
vFile       = "v.txt"
tableFile   = "table.txt"
etaPath     = abspath(join(basePath, "..//Inputs//",  etaFile))
vPath       = abspath(join(basePath, "..//Inputs//",  vFile))
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))
tablePath   = abspath(join(basePath, "..//Inputs//",  tableFile))

# Distribution: ceil(Y), where Y ~ Exponential(1/24)
T = 1440

# Network, arrival patterns
svcArea   = readNetwork(networkPath)
A         = svcArea.A
arrStream = arrivalStream(svcArea, T)
arrStream.updateP(0.25)

# Service distribution for original system
vals    = np.arange(12, 25, dtype = 'int64')
probs   = np.ones(13)/13
svcDist = serviceDistribution(vals, probs)

# Service distributions for Maxwell's bounding system 
svcDists = readEta(etaPath)
v        = readV(vPath) 
table    = readTable(tablePath)

# Arrival probabilities to be tested
N        = 50
seed1    = 12345
objLB    = np.zeros(N)
objUB    = np.zeros(N)
settings = {'OutputFlag' : 0}
	
seed(seed1)
# Matt Maxwell's upper bound
for i in xrange(N):
	omega    = samplePath(svcArea, arrStream, svcDist, mxwDist=svcDists)
	m        = MMIP2.ModelInstance(svcArea, arrStream, omega, v)
	m.solve(settings)
	objUB[i] = m.getObjective()
	lbStats  = simLB(svcArea, omega, lambda simState, location, fel, svcArea:\
				compliance(simState, location, fel, svcArea, table))
	objLB[i] = lbStats['obj']

print 'Maxwell Bound: %.3f +/- %.3f' % confInt(objUB)
print 'Table Bound  : %.3f +/- %.3f' % confInt(objLB) 
