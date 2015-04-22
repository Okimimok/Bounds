import numpy as np
from ....Methods.network import readNetwork	
from ....Lower.compliance import buildDaskinTable, writeTable
from ....Components.arrivalStream import arrivalStream
from ....Components.serviceDistribution import serviceDistribution
from os.path import abspath, dirname, realpath, join

basePath    = dirname(realpath(__file__))
networkFile = "twelve.txt"
tableFile   = "daskinTable.txt"
tablePath   = abspath(join(basePath, tableFile))
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))

# Distribution: Uniformly distributed on {12, 13, ..., 24}
vals    = np.arange(12, 25, dtype = 'int64')
probs   = np.ones(13)/13
svcDist = serviceDistribution(vals, probs)

# Network properties
svcArea   = readNetwork(networkPath)
arrStream = arrivalStream(svcArea, 2)
prob      = 0.25
mu        = svcDist.mean
q         = prob*mu/(svcArea.A)
w         = [max(q, 0.7)**(i-1) for i in xrange(svcArea.A+1)]
arrStream.updateP(prob)

settings = {'OutputFlag': 1, 'MIPGap': 0.005}
table    = buildDaskinTable(svcArea, arrStream, svcDist, q, w, settings)
writeTable(table, tablePath)
