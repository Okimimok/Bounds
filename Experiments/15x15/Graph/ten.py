<<<<<<< HEAD
<<<<<<< HEAD
=======
import numpy as np
>>>>>>> 286f77c... Continuous coordinates
=======
>>>>>>> a1261b4... New home for eta and v
from os.path import dirname, realpath, join
from ....Methods.network import writeNetwork, heatmap, bivariateNormalIntegral as bvni	

# Network file location
basePath    = dirname(realpath(__file__))
networkFile = "ten.txt"
<<<<<<< HEAD
<<<<<<< HEAD
heatFile    = "tenheat.pdf"
=======
heatFile	= "tenheat.pdf"
>>>>>>> 286f77c... Continuous coordinates
=======
heatFile    = "tenheat.pdf"
>>>>>>> a1261b4... New home for eta and v
networkPath = join(basePath, networkFile)
heatPath    = join(basePath, heatFile)

# Size of grid, response time threshold
sizeX = 15
sizeY = 15
<<<<<<< HEAD
<<<<<<< HEAD
Tunit = 2.5
Tresp = 9
=======
Tresp = 5
>>>>>>> 286f77c... Continuous coordinates
=======
Tunit = 2.5
Tresp = 9
>>>>>>> a1261b4... New home for eta and v
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
bases[0]  = {'loc': ( 4.5, 13.5), 'ambs': 0}
bases[1]  = {'loc': (10.5, 13.5), 'ambs': 0}
bases[2]  = {'loc': ( 3.0, 12.0), 'ambs': 2}
bases[3]  = {'loc': (12.0, 12.0), 'ambs': 2}
bases[4]  = {'loc': ( 1.5, 10.5), 'ambs': 0}
bases[5]  = {'loc': ( 4.5, 10.5), 'ambs': 0}
bases[6]  = {'loc': ( 7.5, 10.5), 'ambs': 0}
bases[7]  = {'loc': (10.5, 10.5), 'ambs': 0}
bases[8]  = {'loc': (13.5, 10.5), 'ambs': 0}
bases[9]  = {'loc': ( 6.0,  9.0), 'ambs': 0}
bases[10] = {'loc': ( 9.0,  9.0), 'ambs': 0}
bases[11] = {'loc': ( 4.5,  7.5), 'ambs': 0}
bases[12] = {'loc': ( 7.5,  7.5), 'ambs': 2}
bases[13] = {'loc': (10.5,  7.5), 'ambs': 0}
bases[14] = {'loc': ( 6.0,  6.0), 'ambs': 0}
bases[15] = {'loc': ( 9.0,  6.0), 'ambs': 0}
bases[16] = {'loc': ( 1.5,  4.5), 'ambs': 0}
bases[17] = {'loc': ( 4.5,  4.5), 'ambs': 0}
bases[18] = {'loc': ( 7.5,  4.5), 'ambs': 0}
bases[19] = {'loc': (10.5,  4.5), 'ambs': 0}
bases[20] = {'loc': (13.5,  4.5), 'ambs': 0}
bases[21] = {'loc': ( 3.0,  3.0), 'ambs': 2}
bases[22] = {'loc': (12.0,  3.0), 'ambs': 2}
bases[23] = {'loc': ( 4.5,  1.5), 'ambs': 0}
bases[24] = {'loc': (10.5,  1.5), 'ambs': 0}

# Peaks
sz = [2.5, 1, 1, 1, 1]
mu = [(7.5, 7.5), (3, 3), (12, 3), (3, 12), (12, 12)]
sg = [(2.5, 2.5), (1.5, 1.5), (1.5, 1.5), (1.5, 1.5), (1.5, 1.5)]

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
