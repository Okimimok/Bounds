import numpy as np
from ..write import bivariateNormalIntegral as bvni
from ...Networks.write	import heatmap, network

# Network file location
networkFile = "15x15//eight.txt"
mapFile		= "15x15//eightheat.pdf"

# Size of grid
nX = 15
nY = 15
nodes = [(i, j) for i in xrange(nX) for j in xrange(nY)]

# Dispersion of bases within grid
bases = [(1, 1), (7, 1), (13, 1), (4, 4), (10, 4), (1, 7), \
			(7, 7), (7, 13), (4, 10), (10, 10), (1, 13), \
			(13, 7), (13, 13)]

# Dispersion of ambulances within bases
ambLocs = {}
ambLocs[(7, 7)]  = 4
ambLocs[(1, 7)]  = 1
ambLocs[(7, 1)]  = 1
ambLocs[(7, 13)] = 1
ambLocs[(13, 7)] = 1

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
