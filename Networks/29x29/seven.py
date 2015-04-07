import numpy as np
from ..write import bivariateNormalIntegral as bvni
from ...Networks.write	import heatmap, network

# Network file location
networkFile = "29x29//seven.txt"
mapFile		= "29x29//sevenheat.pdf"

# Size of grid
nX = 29
nY = 29
nodes = [(i, j) for i in xrange(nX) for j in xrange(nY)]

# Dispersion of bases within grid
bases  = [(5,5), (8,2), (2,8), (8, 8), (2,20), (5,23), (8,26), (8,20),\
			(20,20), (23,23), (26,20), (20,26), (20,2), (20,8),\
			(23,5), (26,8), (11,11), (14,14), (17,17), (14,8),\
			(17,11), (20,14), (8,14), (11,17), (14,20), (2,2),\
			(2,26), (26,2), (26, 26), (2,14), (14,2), (14,26), (26,14)]

# Dispersion of ambulances within bases
ambLocs = {}
ambLocs[(5, 23)]  = 1
ambLocs[(5, 5)]   = 1
ambLocs[(23, 23)] = 1
ambLocs[(23, 5)]  = 1
ambLocs[(14, 17)] = 1
ambLocs[(14, 14)] = 1
ambLocs[(14, 11)] = 1

# Response time threshold, distance between nodes
Tresp	 = 9 
nodeDist = 1.25

# Peaks
sz = [5, 1, 1, 1, 1]
mu = [(14, 14), (6.5, 6.5), (6.5, 21.5), (21.5, 6.5), (21.5, 21.5)]
sg = [(4, 4), (2, 2), (2, 2), (2, 2), (2, 2)]

# Probability of call arriving within given node
P = np.zeros((nX, nY))

for i in xrange(nX):
	for j in xrange(nY):
		for k in xrange(len(mu)):
			P[i][j] += sz[k]*bvni(mu[k], sg[k], (i, j))

network(networkFile, nX, nY, nodeDist, Tresp, P, bases, ambLocs)
heatmap(networkFile, mapFile, bases)
