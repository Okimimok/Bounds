from matplotlib import pyplot as plt
from pylab import *
from scipy.stats import norm
import os.path
import numpy as np

def bivariateNormalIntegral(mu, sigma, x):
    term1 = norm.cdf(x[0]+0.5, mu[0], sigma[0])*norm.cdf(x[1]+0.5, mu[1], sigma[1])
    term2 = norm.cdf(x[0]+0.5, mu[0], sigma[0])*norm.cdf(x[1]-0.5, mu[1], sigma[1])
    term3 = norm.cdf(x[0]-0.5, mu[0], sigma[0])*norm.cdf(x[1]+0.5, mu[1], sigma[1])
    term4 = norm.cdf(x[0]-0.5, mu[0], sigma[0])*norm.cdf(x[1]-0.5, mu[1], sigma[1])
    
    return term1 - term2 - term3 + term4

def heatmap(networkFile, mapFile):
	basepath  = os.path.dirname(__file__)
	filepath  = os.path.abspath(os.path.join(basepath, "..//Networks//", networkFile))
	filepath2 = os.path.abspath(os.path.join(basepath, "..//Networks//", mapFile))

	with open(filepath, 'r') as f:
		line = f.readline().split()
		nX	 = int(line[0])
		nY	 = int(line[1])
		prob = np.zeros((nX, nY))
		for i in xrange(nX):
			for j in xrange(nY):
				line = f.readline().split()
				prob[i][j] = float(line[2])
	
	rows, cols = np.indices((nX+1, nY+1))
	ax = plt.subplot(111)
	plt.pcolormesh(rows, cols, prob, edgecolors = 'None')
	plt.savefig(filepath2)
	plt.close('all')


def network(networkFile, nX, nY, nodeDist, Tresp, P, bases, ambLocs):
	basepath = os.path.dirname(__file__)
	filepath = os.path.abspath(os.path.join(basepath, "..//Networks//", networkFile))

	with open(filepath, 'w') as f:
		f.write('%i %i %.2f %i\n' % (nX, nY, nodeDist, Tresp))
		for i in xrange(nX):
			for j in xrange(nY):
				if (i, j) in bases:
					if (i, j) in ambLocs:
						ambs = ambLocs[(i, j)]
					else:
						ambs = 0

					# Node location, arrival probability, is base?, # ambs deployed
					f.write('%i %i %.6f %i %i \n' % (i, j, P[i][j], 1, ambs))
					
				else:
				   f.write('%i %i %.6f %i %i \n' % (i, j, P[i][j], 0, 0))
