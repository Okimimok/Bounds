import numpy as np
from ...Networks.write  import bivariateNormalIntegral as bvni
from ...Networks.write  import heatmap, network

# Network file location
networkFile = "9x9//five.txt"
mapFile     = "9x9//fiveheat.pdf"

# Size of grid
nX = 9
nY = 9
nodes = [(i, j) for i in xrange(nX) for j in xrange(nY)]

# Dispersion of bases within grid
bases  = [(1, 1), (1, 7), (7, 1), (7, 7), (4, 4)]

# Dispersion of ambulances within bases
ambLocs = {}
ambLocs[(1, 1)]  = 1
ambLocs[(1, 7)]  = 1
ambLocs[(7, 1)]  = 1
ambLocs[(7, 7)]  = 1
ambLocs[(4, 4)]  = 0

# Response time threshold, distance between nodes
Tresp    = 4
nodeDist = 1

# Peaks
mu1 = (1, 4)
sg1 = (2, 2)
mu2 = (7, 4)
sg2 = (2, 2)

# Probability of call arriving within given node
P = np.zeros((nX, nY))

for i in xrange(nX):
    for j in xrange(nY):
        P[i][j] += bvni(mu1, sg1, (i, j))
        P[i][j] += bvni(mu2, sg2, (i, j))
        
network(networkFile, nX, nY, nodeDist, Tresp, P, bases, ambLocs)
heatmap(networkFile, mapFile)
