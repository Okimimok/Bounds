from os.path import dirname, realpath, join
from ....Methods.network import writeNetwork, heatmap, bivariateNormalIntegral as bvni	

# Network file location
basePath    = dirname(realpath(__file__))
networkFile = "ten.txt"
heatFile	= "tenheat.pdf"
networkPath = join(basePath, networkFile)
heatPath    = join(basePath, heatFile)

# Size of grid, response time threshold
sizeX = 5 
sizeY = 5
Tresp = 9
Tunit = 4.5
grid  = 1 

# Nodes: center of each cell in 9x9 grid
nodes = {}
count = 0
for i in range(sizeX):
	for j in range(sizeY):
		nodes[count] = {'loc': (i + 0.5, j + 0.5), 'prob': 0.0}
		count += 1

# Base locations
bases    = {}
bases[0] = {'loc': (1.5, 3.5), 'ambs': 2}
bases[1] = {'loc': (3.5, 3.5), 'ambs': 2}
bases[2] = {'loc': (2.5, 2.5), 'ambs': 2}
bases[3] = {'loc': (1.5, 1.5), 'ambs': 2}
bases[4] = {'loc': (3.5, 1.5), 'ambs': 2}

# Peaks
sz = [1]
mu = [(2.5, 2.5)]
sg = [(2, 2)]

# Probability of call arriving within given node
for i in nodes:
	loc = nodes[i]['loc']
	for j in range(len(mu)):
		nodes[i]['prob'] += sz[j]*bvni(mu[j], sg[j], (loc[0], loc[1]), grid/2)


writeNetwork(networkPath, nodes, bases, Tunit, Tresp)
heatmap(heatPath, sizeX, sizeY, grid, nodes, bases, minorAx=1, majorAx=3)
