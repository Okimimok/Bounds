from os.path import dirname, realpath, join
from ....Methods.network import writeNetwork, heatmap, bivariateNormalIntegral as bvni	

# Network file location
basePath    = dirname(realpath(__file__))
networkFile = "four.txt"
heatFile	 = "fourheat.pdf"
networkPath = join(basePath, networkFile)
heatPath    = join(basePath, heatFile)

# Size of grid, response time threshold
sizeX = 9 
sizeY = 9
Tresp = 4
<<<<<<< HEAD
<<<<<<< HEAD
Tunit = 1.0
=======
>>>>>>> 286f77c... Continuous coordinates
=======
Tunit = 1.0
>>>>>>> a1261b4... New home for eta and v
grid  = 1.0

# Nodes: center of each cell in 9x9 grid
nodes = {}
count = 0
for i in range(sizeX):
	for j in range(sizeY):
		nodes[count] = {'loc': (i + 0.5, j + 0.5), 'prob': 0.0}
		count += 1

# Base locations
bases    = {}
bases[0] = {'loc': (2.5, 2.5), 'ambs': 1}
bases[1] = {'loc': (2.5, 6.5), 'ambs': 1}
bases[2] = {'loc': (6.5, 2.5), 'ambs': 1}
bases[3] = {'loc': (6.5, 6.5), 'ambs': 1}

# Peaks
sz = [1, 1, 1, 1]
mu = [(2, 2), (2, 6), (6, 2), (6, 6)]
sg = [(2, 2), (2, 2), (2, 2), (2, 2)]

# Probability of call arriving within given node
for i in nodes:
	loc = nodes[i]['loc']
	for j in range(len(mu)):
		nodes[i]['prob'] += sz[j]*bvni(mu[j], sg[j], (loc[0], loc[1]), grid/2)

<<<<<<< HEAD
<<<<<<< HEAD
writeNetwork(networkPath, nodes, bases, Tunit, Tresp)
=======
writeNetwork(networkPath, nodes, bases, Tresp)
>>>>>>> 286f77c... Continuous coordinates
=======
writeNetwork(networkPath, nodes, bases, Tunit, Tresp)
>>>>>>> a1261b4... New home for eta and v
heatmap(heatPath, sizeX, sizeY, grid, nodes, bases, minorAx=1, majorAx=3)
