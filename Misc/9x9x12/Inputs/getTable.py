import numpy as np
from ....Methods.network import readNetwork	
from ....Lower.compliance import buildTable, writeTable
from ....Components.arrivalStream import arrivalStream
from ....Components.serviceDistribution import serviceDistribution
from os.path import abspath, dirname, realpath, join

basePath    = dirname(realpath(__file__))
networkFile = "twelve.txt"
tableFile   = "table.txt"
tablePath   = abspath(join(basePath, tableFile))
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))

# Distribution: Uniformly distributed on {12, 13, ..., 24}
vals    = np.arange(12, 25, dtype = 'int64')
probs   = np.ones(13)/13
svcDist = serviceDistribution(vals, probs)

# Network properties
svcArea   = readNetwork(networkPath)
arrStream = arrivalStream(svcArea, 2)
w         = [0] + [1.5**(12-i) for i in xrange(12)]
arrStream.updateP(0.07)

table = buildTable(svcArea, arrStream, svcDist, w)
for a in xrange(1, 13):
	print a, table[a]
writeTable(table, tablePath)
