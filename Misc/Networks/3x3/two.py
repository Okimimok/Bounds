import numpy as np
from ..write import bivariateNormalIntegral as bvni
from ...Networks.write  import heatmap, network

# Network file location
networkFile = "3x3//two.txt"
mapFile     = "3x3//twoheat.pdf"

# Size of grid
nX = 3
nY = 3
nodes = [(i, j) for i in xrange(nX) for j in xrange(nY)]

# Dispersion of bases within grid
bases  = [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)]

# Dispersion of ambulances within bases
ambLocs = {}
ambLocs[(1, 1)]  = 2

# Response time threshold
Tresp  = 2
nBases = len(bases)

# Probability of call arriving within given node
# We'll use sum of two bivariate normal RVs for the call distribution
mu1 = (0, 0)
sg1 = (1, 1)
mu2 = (2, 2)
sg2 = (1, 1)

P   = np.zeros((nX, nY))

for i in xrange(nX):
    for j in xrange(nY):
        P[i][j] += 0.11*bvni(mu1, sg1, (i, j))
        P[i][j] += 0.11*bvni(mu2, sg2, (i, j))
        

network(networkFile, nX, nY, nBases, Tresp, P, bases, ambLocs)
heatmap(networkFile, mapFile)
