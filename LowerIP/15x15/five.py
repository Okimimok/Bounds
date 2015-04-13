import numpy as np
from math import exp
from ...LowerIP import compliance
from ...Methods.readFiles import readNetworkFile
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
import os

networkFile = "15x15//five.txt"
tableFile   = "15x15//five.txt"

# Distribution: ceil(Y), where Y ~ Exponential(1/24)
mu        = 24.0
numVals   = 120
vals      = np.arange(1, numVals+1)
probs     = [exp(-(vals[i]-1)/mu)*(1 - exp(-1/mu))\
					 for i in xrange(numVals)]
probs[-1] += 1 - sum(probs)
svcDist   = ServiceDistribution(vals, probs)

# Network properties
T         = 2
prob      = 0.10
svcArea   = readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
arrStream.updateP(prob)

# Weights (don't have to be specified)
w = [16, 8, 4, 2, 1]

table = compliance.buildTable(svcArea, arrStream, svcDist, w)
'''
for a in table.keys():
	print '%i ambulances free------' % a
	for j in table[a]:
		print j, svcArea.bases[j]['loc']
'''
compliance.writeTable(tableFile)

