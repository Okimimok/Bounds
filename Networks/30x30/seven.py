import numpy as np
from ..write import bivariateNormalIntegral as bvni
from ...Networks.write  import heatmap, network

# Network file location
networkFile = "30x30//seven.txt"
mapFile     = "30x30//sevenheat.pdf"

# Size of grid
nX = 30
nY = 30
nodes = [(i, j) for i in xrange(nX) for j in xrange(nY)]

# Dispersion of bases within grid
bases  = [(2, 2), (6, 6), (2, 6), (6, 2)]

# Dispersion of ambulances within bases
ambLocs = {}
ambLocs[(2, 2)]  = 1
ambLocs[(2, 6)]  = 1
ambLocs[(6, 2)]  = 1
ambLocs[(6, 6)]  = 1

# Response time threshold, distance between nodes
Tresp    = 18
nodeDist = 0.5

# Probability of call arriving within given node
P = np.zeros((nX, nY))

network(networkFile, nX, nY, nodeDist, Tresp, P, bases, ambLocs)
bases = []
heatmap(networkFile, mapFile, bases)
