from matplotlib import pyplot as plt
from ..Components.SvcArea import SvcArea
from scipy.stats import norm
import numpy as np

def writeNetwork(networkPath, nX, nY, nodeDist, Tresp, P, bases, ambLocs):
	with open(networkPath, 'w') as f:
		f.write('%i %i %.2f %i\n' % (nX, nY, nodeDist, Tresp))
		for i in range(nX):
			for j in range(nY):
				if (i, j) in bases:
					if (i, j) in ambLocs:
						ambs = ambLocs[(i, j)]
					else:
						ambs = 0

					# Node location, arrival probability, is base?, # ambs deployed
					f.write('%i %i %.6f %i %i \n' % (i, j, P[i][j], bases[(i,j)], ambs))
					
				else:
				   f.write('%i %i %.6f %i %i \n' % (i, j, P[i][j], -1, 0))

def readNetwork(networkPath):
	# Given data about a service area stored in a text file (containing info)
	#	about network structure (assumed rectangluar), base locations,
	#	one-step call probabilities, and ambulance deployment strategy,
	#	returns an object of type ServiceArea with
	#
	# nodeDist a parameter denoting the travel time between adjacent nodes
	bases = {}
	nodes = {}
	
	with open(networkPath, 'r') as f:
		line	 = f.readline().split()
		sizeX	 = int(line[0])
		sizeY	 = int(line[1])
		nodeDist = float(line[2])
		maxDist  = int(line[3])
		numNodes = 0
		
		for i in range(sizeX):
			for j in range(sizeY):
				line = f.readline().split()
				nodes[numNodes] = {'loc':(i, j), 'prob':float(line[2])}

				# Checking base number, if any						
				tmp = int(line[3])
				if tmp >= 0:
					bases[tmp]			= {}
					bases[tmp]['loc']	= (int(line[0]), int(line[1]))
					bases[tmp]['alloc'] = int(line[4])
					
				numNodes += 1

	return SvcArea(nodes, bases, nodeDist, maxDist)

def heatmap(networkPath, mapPath, bases, majorAx=-1, minorAx=-1):
	with open(networkPath, 'r') as f:
		line = f.readline().split()
		nX	 = int(line[0])
		nY	 = int(line[1])
		prob = np.zeros((nX, nY))
		for i in range(nX):
			for j in range(nY):
				line = f.readline().split()
				prob[i][j] = float(line[2])
	
	rows, cols = np.indices((nX+1, nY+1))
	ax         = plt.subplot(111)
	plt.pcolormesh(rows, cols, prob, cmap = 'Greys')

	if minorAx > 0:
		ax.xaxis.set_minor_locator(plt.MultipleLocator(minorAx))
		ax.yaxis.set_minor_locator(plt.MultipleLocator(minorAx))

	if majorAx > 0:
		ax.xaxis.set_major_locator(plt.MultipleLocator(majorAx))
		ax.yaxis.set_major_locator(plt.MultipleLocator(majorAx))

	ax.xaxis.grid(True,'minor', linewidth = 0.5, linestyle = '-')
	ax.yaxis.grid(True,'minor', linewidth = 0.5, linestyle = '-')
	ax.xaxis.grid(True,'major',linewidth=1.5, linestyle = '-')
	ax.yaxis.grid(True,'major',linewidth=1.5, linestyle = '-')

	for j in bases:
		ax.plot(j[0]+0.5, j[1]+0.5, marker = 'o', color='g')
	
	plt.xlim([0, nX])
	plt.ylim([0, nY])
	plt.savefig(mapPath)
	plt.close('all')

def bivariateNormalIntegral(mu, sigma, x):
	term1 = norm.cdf(x[0]+0.5, mu[0], sigma[0])*norm.cdf(x[1]+0.5, mu[1], sigma[1])
	term2 = norm.cdf(x[0]+0.5, mu[0], sigma[0])*norm.cdf(x[1]-0.5, mu[1], sigma[1])
	term3 = norm.cdf(x[0]-0.5, mu[0], sigma[0])*norm.cdf(x[1]+0.5, mu[1], sigma[1])
	term4 = norm.cdf(x[0]-0.5, mu[0], sigma[0])*norm.cdf(x[1]-0.5, mu[1], sigma[1])
	
	return term1 - term2 - term3 + term4
