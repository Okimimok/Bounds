from os.path import dirname, realpath, join
from ....Methods.network import writeNetwork, heatmap, bivariateNormalIntegral as bvni	

# Network file location
basePath    = dirname(realpath(__file__))
networkFile = "two.txt"
networkPath = join(basePath, networkFile)

# Size of grid, response time threshold
sizeX = 2
sizeY = 1
Tresp = 0.5
Tunit = 1.0
grid  = 1.0

# Nodes: center of each cell in 9x9 grid
nodes = {}
nodes[0] = {'loc': (0, 0), 'prob': 0.5}
nodes[1] = {'loc': (1, 0), 'prob': 0.5}

# Base locations
bases    = {}
bases[0] = {'loc': (0, 0), 'ambs': 1}
bases[1] = {'loc': (1, 0), 'ambs': 1}


writeNetwork(networkPath, nodes, bases, Tunit, Tresp)
