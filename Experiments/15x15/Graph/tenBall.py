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
networkFile = "tenBall.txt"
heatFile	= "tenBallheat.pdf"
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
bases[0]  = {'loc': ( 4.50, 10.50), 'ambs': 0}
bases[1]  = {'loc': ( 7.50, 10.50), 'ambs': 0}
bases[2]  = {'loc': (10.50, 10.50), 'ambs': 2}
bases[3]  = {'loc': ( 6.00,  9.00), 'ambs': 0}
bases[4]  = {'loc': ( 7.50,  9.00), 'ambs': 0}
bases[5]  = {'loc': ( 9.00,  9.00), 'ambs': 0}
bases[6]  = {'loc': ( 6.75,  8.25), 'ambs': 0}
bases[7]  = {'loc': ( 7.50,  8.25), 'ambs': 0}
bases[8]  = {'loc': ( 8.25,  8.25), 'ambs': 0}
bases[9]  = {'loc': ( 4.50,  7.50), 'ambs': 0}
bases[10] = {'loc': ( 6.00,  7.50), 'ambs': 0}
bases[11] = {'loc': ( 6.75,  7.50), 'ambs': 0}
bases[12] = {'loc': ( 7.50,  7.50), 'ambs': 2}
bases[13] = {'loc': ( 8.25,  7.50), 'ambs': 0}
bases[14] = {'loc': ( 9.00,  7.50), 'ambs': 0}
bases[15] = {'loc': (10.50,  7.50), 'ambs': 0}
bases[16] = {'loc': ( 6.75,  6.75), 'ambs': 0}
bases[17] = {'loc': ( 7.50,  6.75), 'ambs': 0}
bases[18] = {'loc': ( 8.25,  6.75), 'ambs': 2}
bases[19] = {'loc': ( 6.00,  6.00), 'ambs': 0}
bases[20] = {'loc': ( 7.50,  6.00), 'ambs': 0}
bases[21] = {'loc': ( 9.00,  6.00), 'ambs': 0}
bases[22] = {'loc': ( 4.50,  4.50), 'ambs': 2}
bases[23] = {'loc': ( 7.50,  4.50), 'ambs': 0}
bases[24] = {'loc': (10.50,  4.50), 'ambs': 2}

# Peaks
sz = [1]
mu = [(7.5, 7.5)]
sg = [(2.5, 2.5)]

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
