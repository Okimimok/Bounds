import numpy as np
from ....Methods.network import readNetwork	
from ....Lower.compliance import buildDaskinTable, writeTable
from ....Components.arrivalStream import arrivalStream
from ....Components.serviceDistribution import serviceDistribution
from os.path import abspath, dirname, realpath, join

basePath    = dirname(realpath(__file__))
networkFile = "four.txt"
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
w         = [0.0, 8.0, 4.0, 2.0, 1.0]
prob      = 0.07
mu        = svcDist.mean
q         = prob*mu/(svcArea.A)
arrStream.updateP(prob)

settings = {'OutputFlag': 1, 'MIPGap': 0.005}
table    = buildDaskinTable(svcArea, arrStream, svcDist, q, w, settings)
writeTable(table, tablePath)
