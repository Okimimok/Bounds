from matplotlib import pyplot as plt
from ..Components.SvcArea import SvcArea
from scipy.stats import norm
import numpy as np

<<<<<<< HEAD
def writeNetwork(networkPath, nodes, bases, Tunit, Tresp):
	nNodes = len(nodes)
	nBases = len(bases)
	with open(networkPath, 'w') as f:
		f.write('#NumNodes NumBases UnitTravelTime RespThreshold\n')
		f.write('%i %i %.6f %.2f\n' % (nNodes, nBases, Tunit, Tresp))

		f.write('#DemandNodes: x y\n')
=======
def writeNetwork(networkPath, nodes, bases, Tresp):
	nNodes = len(nodes)
	nBases = len(bases)
	with open(networkPath, 'w') as f:
		f.write('#NumNodes NumBases RespThreshold\n')
		f.write('%i %i %.2f\n' % (nNodes, nBases, Tresp))

		f.write('#DemandNodes\n')
>>>>>>> 286f77c... Continuous coordinates
		for i in range(nNodes):
			loc = nodes[i]['loc']
			f.write('%i %.2f %.2f %.6f\n' % (i, loc[0], loc[1], nodes[i]['prob']))

<<<<<<< HEAD
		f.write('#Bases: x y NumAmbs\n')
=======
		f.write('#Bases\n')
>>>>>>> 286f77c... Continuous coordinates
		for j in range(nBases):
			loc = bases[j]['loc']
			f.write('%i %.2f %.2f %i\n' % (j, loc[0], loc[1], bases[j]['ambs']))

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
		tmp    = f.readline()
		line   = f.readline().split()
		nNodes = int(line[0])
		nBases = int(line[1])
<<<<<<< HEAD
		Tunit  = float(line[2])
		Tresp  = float(line[3])
=======
		Tresp  = float(line[2])
>>>>>>> 286f77c... Continuous coordinates

		# Reading nodes
		tmp = f.readline()
		for i in range(nNodes):
			line = f.readline().split()
			nodes[i] = {}
			nodes[i]['loc']  = (float(line[1]), float(line[2]))
			nodes[i]['prob'] = float(line[3])

		# Reading bases
		tmp = f.readline()
		for j in range(nBases):
			line = f.readline().split()
			bases[j]         = {}
			bases[j]['loc']  = (float(line[1]), float(line[2]))
			bases[j]['ambs'] = int(line[3])

<<<<<<< HEAD
	return SvcArea(nodes, bases, Tunit, Tresp)
=======
	return SvcArea(nodes, bases, Tresp)
>>>>>>> 286f77c... Continuous coordinates

def heatmap(mapPath, sizeX, sizeY, grid, nodes, bases, minorAx=-1, majorAx=-1):
	nX   = sizeX // grid
	nY   = sizeY // grid
	prob = np.zeros((nX, nY))

	for i in nodes:
		loc = nodes[i]['loc']
		# Find what grid cell loc falls into, and update accordingly
		indX = loc[0] // grid
		indY = loc[1] // grid
		prob[indX][indY] += nodes[i]['prob']

	ax         = plt.subplot(111)
	rows, cols = np.indices((nX+1, nY+1))

	if minorAx > 0:
		ax.xaxis.set_minor_locator(plt.MultipleLocator(minorAx))
		ax.yaxis.set_minor_locator(plt.MultipleLocator(minorAx))

	if majorAx > 0:
		ax.xaxis.set_major_locator(plt.MultipleLocator(majorAx))
		ax.yaxis.set_major_locator(plt.MultipleLocator(majorAx))

	plt.pcolormesh(rows, cols, prob, cmap='Greys')
	ax.xaxis.grid(True, 'minor', linewidth=0.5, linestyle='-')
	ax.yaxis.grid(True, 'minor', linewidth=0.5, linestyle='-')
	ax.xaxis.grid(True, 'major', linewidth=1.5, linestyle='-')
	ax.yaxis.grid(True, 'major', linewidth=1.5, linestyle='-')

	for j in bases:
		loc = bases[j]['loc'] 
		ax.plot(loc[0], loc[1], marker = 'o', color='g', zorder=4)

	plt.xlim([0, sizeX])
	plt.ylim([0, sizeY])
	plt.savefig(mapPath)
	plt.close('all')

def bivariateNormalIntegral(mu, sigma, x, dt):
	term1 = norm.cdf(x[0]+dt, mu[0], sigma[0])*norm.cdf(x[1]+dt, mu[1], sigma[1])
	term2 = norm.cdf(x[0]+dt, mu[0], sigma[0])*norm.cdf(x[1]-dt, mu[1], sigma[1])
	term3 = norm.cdf(x[0]-dt, mu[0], sigma[0])*norm.cdf(x[1]+dt, mu[1], sigma[1])
	term4 = norm.cdf(x[0]-dt, mu[0], sigma[0])*norm.cdf(x[1]-dt, mu[1], sigma[1])
	return term1 - term2 - term3 + term4
