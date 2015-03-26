import numpy as np
import os.path
from ..Classes.ServiceArea import ServiceArea

def distance(x, y):
    # Outputs Manhattan distance between two points x and y in R^2
    return abs(x[0] - y[0]) + abs(x[1] - y[1])

def readNetworkFile(networkFile):
    # Given data about a service area stored in a text file (containing info)
    #   about network structure (assumed rectangluar), base locations,
    #   one-step call probabilities, and ambulance deployment strategy,
    #   returns an object of type ServiceArea with
    #
    # bases : Dictionary, base locations, no. ambs stationed
    # nodes : Dictionary of nodes in the network. Keys are integers, values 
    #           are locations. A;so contains single-period arrival probs.
    # dist  : Array, dist[i][j] = Distance between node i and base j
    #   B   : Dictionary, B[i] = Bases that can respond to call at node i
    #   R   : Dictionary, R[j] = Demand nodes base j can cover

	bases = {}
	nodes = {}
	basepath = os.path.dirname(__file__)
	filepath = os.path.abspath(os.path.join(basepath, "..//Networks//", networkFile))
	
	with open(filepath, 'r') as f:
		line     = f.readline().split()
		sizeX    = int(line[0])
		sizeY    = int(line[1])
		maxDist  = int(line[3])
		numBases = 0
		numNodes = 0
        
		for i in xrange(sizeX):
			for j in xrange(sizeY):
				line = f.readline().split()
				nodes[numNodes] = {'loc':(i, j), 'prob':float(line[2])}
                                
				if int(line[3]) > 0:
					bases[numBases]          = {}
					bases[numBases]['loc']   = (int(line[0]), int(line[1]))
					bases[numBases]['alloc'] = int(line[4])
					numBases += 1
                    
				numNodes += 1

		dist = np.zeros((numNodes, numBases))
		for i in nodes:
			for j in bases:
				dist[i][j] = distance(nodes[i]['loc'], bases[j]['loc'])
                
	return ServiceArea(nodes, bases, dist, maxDist)
