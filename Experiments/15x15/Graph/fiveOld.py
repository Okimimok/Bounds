import numpy as np
from os.path import dirname, realpath, join
from ....Methods.network import writeNetwork, heatmap, bivariateNormalIntegral as bvni	

# Network file location
basePath    = dirname(realpath(__file__))
networkFile = "five.txt"
heatFile	= "fiveheat.pdf"
networkPath = join(basePath, networkFile)
heatPath    = join(basePath, heatFile)

# Size of grid
nX = 15
nY = 15
nodes = [(i, j) for i in xrange(nX) for j in xrange(nY)]

# Dispersion of bases within grid
bases = {(1, 13): 0, (4, 13): 1,  (7, 13): 2, (10, 13): 3, (13, 13): 4,\
			 (1, 10): 5, (4, 10): 6, (7, 10): 7, (10, 10): 8, (13, 10): 9,\
			 (1, 7): 10, (4, 7): 11, (7, 7): 12, (10, 7): 13, (13, 7): 14,\
			 (1, 4): 15, (4, 4): 16, (7, 4): 17, (10, 4): 18, (13, 4): 19,\
			 (1, 1): 20, (4, 1): 21, (7, 1): 22, (10, 1): 23, (13, 1): 24}

# Dispersion of ambulances within bases
ambLocs = {}
ambLocs[(7, 7)]  = 1
ambLocs[(4, 4)]  = 1
ambLocs[(4, 10)]  = 1
ambLocs[(10, 4)] = 1
ambLocs[(10, 10)] = 1

# Response time threshold, distance between nodes
Tresp	 = 2 
nodeDist = 1

# Peaks
sz = [4, 1, 1, 1, 1]
mu = [(7, 7), (2.5, 2.5), (2.5, 11.5), (11.5, 2.5), (11.5, 11.5)]
sg = [(2.5, 2.5), (1.5, 1.5), (1.5, 1.5), (1.5, 1.5), (1.5, 1.5)]

# Axes marks
majorAx = 3
minorAx = 1

# Probability of call arriving within given node
P = np.zeros((nX, nY))

for i in xrange(nX):
	for j in xrange(nY):
		for k in xrange(len(mu)):
			P[i][j] += sz[k]*bvni(mu[k], sg[k], (i, j))

writeNetwork(networkPath, nX, nY, nodeDist, Tresp, P, bases, ambLocs)
heatmap(networkPath, heatPath, bases, majorAx, minorAx)
