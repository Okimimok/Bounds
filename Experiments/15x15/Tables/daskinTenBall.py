import numpy as np
from math import exp
from ....Methods.network import readNetwork	
from ....Methods.dists import readSvcDist
from ....Lower.compliance import buildDaskinTable, writeTable
from ....Components.ArrStream import ArrStream
from ....Components.SvcDist import SvcDist
from os.path import abspath, dirname, realpath, join

basePath    = dirname(realpath(__file__))
networkFile = "tenBall.txt"
tableFile   = "daskinTenBall.txt"
sdFile      = "exponential.txt"
tablePath   = abspath(join(basePath, tableFile))
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))
sdPath      = abspath(join(basePath, "..//Dists//",  sdFile))

# Distribution: Uniformly distributed on {12, 13, ..., 24}
sdist = readSvcDist(sdPath)

# Network properties
svca = readNetwork(networkPath)
astr = ArrStream(svca, 2)
prob = 0.10
mu   = sdist.mean
q    = prob*mu/(svca.A)
w    = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0] 
#w    = [max(q, 0.5)**(i-1) for i in range(svca.A+1)]
astr.updateP(prob)

settings = {'OutputFlag': 1, 'MIPGap': 0.005}
table    = buildDaskinTable(svca, astr, sdist, q, w, settings)
writeTable(table, tablePath)
