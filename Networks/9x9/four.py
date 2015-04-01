import numpy as np
from ..write import bivariateNormalIntegral as bvni
from ...Networks.write  import heatmap, network

# Network file location
networkFile = "9x9//four.txt"
mapFile     = "9x9//fourheat.pdf"

# Size of grid
nX = 9
nY = 9
nodes = [(i, j) for i in xrange(nX) for j in xrange(nY)]

# Dispersion of bases within grid
bases  = [(2, 2), (6, 6), (2, 6), (6, 2)]

# Dispersion of ambulances within bases
ambLocs = {}
ambLocs[(2, 2)]  = 1
ambLocs[(2, 6)]  = 1
ambLocs[(6, 2)]  = 1
ambLocs[(6, 6)]  = 1

# Response time threshold
Tresp  = 4
nBases = len(bases)

# Peaks
mu1 = (2, 2)
sg1 = (2, 2)
mu2 = (2, 6)
sg2 = (2, 2)
mu3 = (6, 2)
sg3 = (2, 2)
mu4 = (6, 6)
sg4 = (2, 2)

network(networkFile, nX, nY, nBases, Tresp, P, bases, ambLocs)
heatmap(networkFile, mapFile)