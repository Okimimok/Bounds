from os.path import dirname, realpath, join
from ....Methods.network import writeNetwork, heatmap, bivariateNormalIntegral as bvni	

# Network file location
basePath    = dirname(realpath(__file__))
networkFile = "eight.txt"
heatFile	= "eightheat.pdf"
networkPath = join(basePath, networkFile)
heatPath    = join(basePath, heatFile)

# Size of grid, response time threshold
sizeX = 9 
sizeY = 9
Tresp = 9 
Tunit = 2.25
grid  = 1.0

# Nodes: center of each cell in 9x9 grid
nodes = {}
count = 0
for i in range(sizeX):
	for j in range(sizeY):
		nodes[count] = {'loc': (i + 0.5, j + 0.5), 'prob': 0.0}
		count += 1

# Base locations
# "cluster" used in time-base penalty multipliers, when
#	we want to set the multipliers for bases in the same
#	cluster equal to one another
bases    = {}
bases[0] = {'loc': (2.5, 2.5), 'ambs': 2, 'clst': 0}
bases[1] = {'loc': (2.5, 6.5), 'ambs': 2, 'clst': 1}
bases[2] = {'loc': (6.5, 2.5), 'ambs': 2, 'clst': 1}
bases[3] = {'loc': (6.5, 6.5), 'ambs': 2, 'clst': 0}

# Peaks
sz = [1, 1, 1, 1]
mu = [(2, 2), (2, 6), (6, 2), (6, 6)]
sg = [(2, 2), (2, 2), (2, 2), (2, 2)]

# Probability of call arriving within given node
for i in nodes:
	loc = nodes[i]['loc']
	for j in range(len(mu)):
		nodes[i]['prob'] += sz[j]*bvni(mu[j], sg[j], (loc[0], loc[1]), grid/2)


writeNetwork(networkPath, nodes, bases, Tunit, Tresp)
heatmap(heatPath, sizeX, sizeY, grid, nodes, bases, minorAx=1, majorAx=3)
