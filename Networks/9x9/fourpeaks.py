import numpy as np
from ..write import bivariateNormalIntegral as bvni
from ...Networks.write  import heatmap, network

# Network file location
networkFile = "9x9//fourpeaks.txt"
mapFile     = "9x9//fourpeaksheat.pdf"

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
Tresp    = 4
nodeDist = 1

# Peaks
mu1 = (2, 2)
sg1 = (1, 1)
mu2 = (2, 6)
sg2 = (1, 1)
mu3 = (6, 2)
sg3 = (1, 1)
mu4 = (6, 6)
sg4 = (1, 1)

# Probability of call arriving within given node
P = np.zeros((nX, nY))

for i in xrange(nX):
    for j in xrange(nY):
        P[i][j] += 0.10*bvni(mu1, sg1, (i, j))
        P[i][j] += 0.10*bvni(mu2, sg2, (i, j))
        P[i][j] += 0.10*bvni(mu3, sg3, (i, j))
        P[i][j] += 0.10*bvni(mu4, sg4, (i, j))
        

network(networkFile, nX, nY, nodeDist, Tresp, P, bases, ambLocs)
heatmap(networkFile, mapFile)
