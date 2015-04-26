import numpy as np
from ....Methods.network import readNetwork	
from ....Lower.compliance import buildDaskinTable, writeTable
from ....Components.ArrStream import ArrStream
from ....Components.SvcDist import SvcDist
from os.path import abspath, dirname, realpath, join

basePath    = dirname(realpath(__file__))
networkFile = "four.txt"
tableFile   = "daskinTable.txt"
tablePath   = abspath(join(basePath, tableFile))
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))

# Distribution: Uniformly distributed on {12, 13, ..., 24}
vals  = np.arange(12, 25, dtype = 'int64')
probs = np.ones(13)/13
sdist = SvcDist(vals, probs)

# Network properties
svca = readNetwork(networkPath)
astr = ArrStream(svca, 2)
w    = [0.0, 8.0, 4.0, 2.0, 1.0]
prob = 0.07
mu   = sdist.mean
q    = prob*mu/(svca.A)
astr.updateP(prob)

settings = {'OutputFlag': 1, 'MIPGap': 0.005}
table    = buildDaskinTable(svca, astr, sdist, q, w, settings)
writeTable(table, tablePath)
