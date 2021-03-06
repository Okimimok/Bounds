import numpy as np
from ..write import bivariateNormalIntegral as bvni
from ...Networks.write	import heatmap, network

# Network file location
networkFile = "9x9//four.txt"
mapFile		= "9x9//fourheat.pdf"

# Size of grid
nX = 9
nY = 9
nodes = [(i, j) for i in xrange(nX) for j in xrange(nY)]

# Dispersion of bases within grid
bases = {(6, 2): 0, (6, 6): 1, (2, 2): 2, (2, 6): 3}

# Dispersion of ambulances within bases
ambLocs = {}
ambLocs[(2, 2)]  = 1
ambLocs[(2, 6)]  = 1
ambLocs[(6, 2)]  = 1
ambLocs[(6, 6)]  = 1

# Response time threshold, distance between nodes
Tresp	 = 4
nodeDist = 1

# Peaks
sz = [1, 1, 1, 1]
mu = [(2, 2), (2, 6), (6, 2), (6, 6)]
sg = [(2, 2), (2, 2), (2, 2), (2, 2)]

# Axes marks
majorAx = 3
minorAx = 1

# Probability of call arriving within given node
P = np.zeros((nX, nY))

for i in xrange(nX):
	for j in xrange(nY):
		for k in xrange(len(sz)):
			P[i][j] += 0.10*bvni(mu[k], sg[k], (i, j))

network(networkFile, nX, nY, nodeDist, Tresp, P, bases, ambLocs)
heatmap(networkFile, mapFile, bases, majorAx, minorAx)
