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
from ...Simulation.tablePolicies import compliance

networkFile = "15x15//five.txt"
#tableFile   = "/home/kenneth/Bounds/LowerIP/15x15/five.txt"
tableFile   = "/home/kenneth/Bounds/LowerIP/15x15/fiveV2.txt"
randomSeed	= 12345

# Basic inputs
T	      = 1440
# Distribution: ceil(Y), where Y ~ Exponential(1/34)
mu        = 24.0
numVals   = 120
vals      = np.arange(1, numVals+1)
probs     = [exp(-(vals[i]-1)/mu)*(1 - exp(-1/mu))\
					 for i in xrange(numVals)]
probs[-1] += 1 - sum(probs)
svcDist   = ServiceDistribution(vals, probs)

# Network, arrival patterns
svcArea   = readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
arrStream.updateP(0.10)

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

start = time.clock()
seed(randomSeed)
for k in xrange(N):
	omega  = SamplePath(svcArea, arrStream, svcDist)
	
	# Simulated lower bound
	lbStats  = simLB(svcArea, omega, lambda simState, location, fel, svcArea:\
				compliance(simState, location, fel, svcArea, table))
	lbObj[k] = lbStats['obj']

print 'Objective : %.3f +/- %.3f' % confInt(lbObj)
