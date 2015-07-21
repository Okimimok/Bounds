from os.path import dirname, realpath, join
from ...Methods.network import writeNetwork    

# Network file location
basePath    = dirname(realpath(__file__))
networkFile = "graph.txt"
networkPath = join(basePath, networkFile)

# Size of grid, response time threshold
sizeX = 3 
sizeY = 3
Tresp = 4
Tunit = 1.0
grid  = 1.0

# Nodes: center of each cell in 9x9 grid
nodes = {}
nodes[0] = {'loc': (0.0, 0.0), 'prob': 0.3}
nodes[1] = {'loc': (0.0, 3.0), 'prob': 0.2}
nodes[2] = {'loc': (3.0, 0.0), 'prob': 0.2}
nodes[3] = {'loc': (3.0, 3.0), 'prob': 0.3}

# Base locations
bases    = {}
bases[0] = {'loc': (0.0, 0.0), 'ambs': 1}
bases[1] = {'loc': (0.0, 3.0), 'ambs': 0}
bases[2] = {'loc': (3.0, 0.0), 'ambs': 0}
bases[3] = {'loc': (3.0, 3.0), 'ambs': 1}

writeNetwork(networkPath, nodes, bases, Tunit, Tresp)
