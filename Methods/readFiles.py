import numpy as np
import os.path
from ..Classes.ServiceArea import ServiceArea
from ..Classes.ServiceDistribution import ServiceDistribution

def readNetworkFile(networkFile):
	# Given data about a service area stored in a text file (containing info)
	#	about network structure (assumed rectangluar), base locations,
	#	one-step call probabilities, and ambulance deployment strategy,
	#	returns an object of type ServiceArea with
	#
	# bases : Dictionary, base locations, no. ambs stationed
	# nodes : Dictionary of nodes in the network. Keys are integers, values 
	#			are locations. A;so contains single-period arrival probs.
	# dist	: Array, dist[i][j] = Distance between node i and base j
	#	B	: Dictionary, B[i] = Bases that can respond to call at node i
	#	R	: Dictionary, R[j] = Demand nodes base j can cover
	#
	# nodeDist a parameter denoting the travel time between adjacent nodes

	bases = {}
	nodes = {}
	basepath = os.path.dirname(__file__)
	filepath = os.path.abspath(os.path.join(basepath, "..//Networks//", networkFile))
	
	with open(filepath, 'r') as f:
		line	 = f.readline().split()
		sizeX	 = int(line[0])
		sizeY	 = int(line[1])
		nodeDist = float(line[2])
		maxDist  = int(line[3])
		numNodes = 0
		
		for i in xrange(sizeX):
			for j in xrange(sizeY):
				line = f.readline().split()
				nodes[numNodes] = {'loc':(i, j), 'prob':float(line[2])}

				# Checking base number, if any						
				tmp = int(line[3])
				if tmp >= 0:
					bases[tmp]			= {}
					bases[tmp]['loc']	= (int(line[0]), int(line[1]))
					bases[tmp]['alloc'] = int(line[4])
					
				numNodes += 1

	return ServiceArea(nodes, bases, nodeDist, maxDist)


def readEtaFile(etaPath):
	with open(etaPath, 'r') as f:
		line  = f.readline().split()
		R     = int(line[0]) 
		M     = int(line[1])
		vals  = np.arange(1, R)
		cdfs  = np.empty((M, R))
	
		for r in xrange(R):
			line = f.readline().split()
			for m in xrange(M):
				cdfs[m][r] = float(line[m])

	svcDists = {}
	for m in xrange(M):
		pmf = cdfs[m][1:] - cdfs[m][:R-1]
		svcDists[m] = ServiceDistribution(vals, pmf)

	return svcDists

def readVFile(vPath):
	with open(vPath, 'r') as f:
		A = int(f.readline()) 
		v = {}
		for a in xrange(1, A+1):	
			line = f.readline().split()
			v[a] = float(line[1])

	return v

	svcDists = {}
	for m in xrange(M):
		pmf = cdfs[m][1:] - cdfs[m][:R-1]
		svcDists[m] = ServiceDistribution(vals, pmf)

	return svcDists
