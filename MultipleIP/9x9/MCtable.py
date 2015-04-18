import numpy as np 
import time
from random import seed
from math import exp
from ...Methods.readFiles import readNetworkFile
from ...Methods.sample import confInt
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
from ...Classes.PenaltyMultipliers import PenaltyMultipliers
from ...Classes.SamplePath import SamplePath
from ...Simulation.lowerBound import simulate as simLB
from ...Simulation.lowerBound2 import simulate as simLB2
from ...Simulation.tablePolicies import compliance

networkFile = "9x9//four.txt"
tableFile   = "/home/kenneth/Bounds/LowerIP/9x9/four.txt"
randomSeed	= 33768

T	    = 1440
vals    = np.arange(12, 25, dtype = 'int64')
probs   = np.ones(13)/13
svcDist = ServiceDistribution(vals, probs)

# Network, arrival patterns
svcArea   = readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
arrStream.updateP(0.07)

# Reading compliance table
with open(tableFile, 'r') as f:
	A     = int(f.readline())
	table = {}
	for a in xrange(1, A+1):
		line     = f.readline().split()
		table[a] = [int(tmp) for tmp in line]

# Generating sample paths
N	   = 100
lbObj  = np.zeros(N)
lbObj2 = np.zeros(N)
start  = time.clock()
seed(randomSeed)
for k in xrange(N):
	if (k+1)% 10 == 0:
		print 'Iteration %i' % (k+1)

	omega  = SamplePath(svcArea, arrStream, svcDist)
	
	# Simulated lower bound
	lbStats   = simLB(svcArea, omega, lambda simState, location, fel, svcArea:\
				compliance(simState, location, fel, svcArea, table))
	lbStats2  = simLB2(svcArea, omega, lambda simState, location, fel, svcArea:\
				compliance(simState, location, fel, svcArea, table))
	lbObj[k]  = lbStats['obj']
	lbObj2[k] = lbStats2['obj']

print 'Objective  : %.3f +/- %.3f' % confInt(lbObj)
print 'Objective 2: %.3f +/- %.3f' % confInt(lbObj2)

