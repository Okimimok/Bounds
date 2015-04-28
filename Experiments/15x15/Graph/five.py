from os.path import dirname, realpath, join
from ....Methods.network import writeNetwork, heatmap, bivariateNormalIntegral as bvni	

# Network file location
basePath    = dirname(realpath(__file__))
networkFile = "five.txt"
heatFile    = "fiveheat.pdf"
networkPath = join(basePath, networkFile)
heatPath    = join(basePath, heatFile)

# Size of grid, response time threshold
sizeX = 15
sizeY = 15
<<<<<<< HEAD
<<<<<<< HEAD
Tunit = 1.0
=======
>>>>>>> 286f77c... Continuous coordinates
=======
Tunit = 1.0
>>>>>>> a1261b4... New home for eta and v
Tresp = 2
grid  = 1.0

# Nodes: center of each cell in 15x15 grid
nodes = {}
count = 0
for i in range(sizeX):
	for j in range(sizeY):
		nodes[count] = {'loc': (i + 0.5, j + 0.5), 'prob': 0.0}
		count += 1

# Base locations		
bases = {}
bases[0]  = {'loc': ( 1.5, 13.5), 'ambs': 0}
bases[1]  = {'loc': ( 4.5, 13.5), 'ambs': 0}
bases[2]  = {'loc': ( 7.5, 13.5), 'ambs': 0}
bases[3]  = {'loc': (10.5, 13.5), 'ambs': 1}
bases[4]  = {'loc': (13.5, 13.5), 'ambs': 0}
bases[5]  = {'loc': ( 1.5, 10.5), 'ambs': 0}
bases[6]  = {'loc': ( 4.5, 10.5), 'ambs': 1}
bases[7]  = {'loc': ( 7.5, 10.5), 'ambs': 0}
bases[8]  = {'loc': (10.5, 10.5), 'ambs': 0}
bases[9]  = {'loc': (13.5, 10.5), 'ambs': 0}
bases[10] = {'loc': ( 1.5,  7.5), 'ambs': 0}
bases[11] = {'loc': ( 4.5,  7.5), 'ambs': 0}
bases[12] = {'loc': ( 7.5,  7.5), 'ambs': 1}
bases[13] = {'loc': (10.5,  7.5), 'ambs': 0}
bases[14] = {'loc': (13.5,  7.5), 'ambs': 0}
bases[15] = {'loc': ( 1.5,  4.5), 'ambs': 0}
bases[16] = {'loc': ( 4.5,  4.5), 'ambs': 1}
bases[17] = {'loc': ( 7.5,  4.5), 'ambs': 0}
bases[18] = {'loc': (10.5,  4.5), 'ambs': 1}
bases[19] = {'loc': (13.5,  4.5), 'ambs': 0}
bases[20] = {'loc': ( 1.5,  1.5), 'ambs': 0}
bases[21] = {'loc': ( 4.5,  1.5), 'ambs': 0}
bases[22] = {'loc': ( 7.5,  1.5), 'ambs': 0}
bases[23] = {'loc': (10.5,  1.5), 'ambs': 0}
bases[24] = {'loc': (13.5,  1.5), 'ambs': 0}

# Peaks
sz = [2.5, 1, 1, 1, 1]
mu = [(7, 7), (2.5, 2.5), (2.5, 11.5), (11.5, 2.5), (11.5, 11.5)]
sg = [(2.5, 2.5), (1.5, 1.5), (1.5, 1.5), (1.5, 1.5), (1.5, 1.5)]

# Axes marks
majorAx = 3
minorAx = 1

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
