import numpy as np
from ..write import bivariateNormalIntegral as bvni
from ...Networks.write	import heatmap, network

# Network file location
networkFile = "15x15//fiveV2.txt"
mapFile		= "15x15//fiveheatV2.pdf"

# Size of grid
nX = 15
nY = 15
nodes = [(i, j) for i in xrange(nX) for j in xrange(nY)]

# Dispersion of bases within grid
bases = {(1, 13): 0, (7, 13): 1, (13, 13): 2, (4, 10): 3, (10, 10): 4,\
			(1, 7): 5, (7, 7): 6, (13, 7): 7, (4, 4): 8, (10, 4): 9,\
			(1, 1): 10, (7, 1): 11, (13, 1): 12}

# Dispersion of ambulances within bases
ambLocs = {}
ambLocs[(7, 7)]  = 1
ambLocs[(4, 4)]  = 1
ambLocs[(4, 10)]  = 1
ambLocs[(10, 4)] = 1
ambLocs[(10, 10)] = 1

# Response time threshold, distance between nodes
Tresp	 = 4 
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

network(networkFile, nX, nY, nodeDist, Tresp, P, bases, ambLocs)
heatmap(networkFile, mapFile, bases, majorAx, minorAx)
