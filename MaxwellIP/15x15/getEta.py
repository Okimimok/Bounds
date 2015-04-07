import numpy as np
from random import seed
from ...Methods.graph import readNetworkFile
from ...Methods.sample import confInt
from ...Classes.ServiceDistribution import ServiceDistribution
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...MaxwellIP import MMIP

networkFile = "15x15//five.txt"
outputFile	= "eta.txt"

import os.path
basepath  = os.path.dirname(__file__)
filepath  = os.path.abspath(os.path.join(basepath, outputFile))

#################################################
# Basic inputs
T		= 1440
vals    = np.arange(12, 25, dtype = 'int64')
probs   = np.ones(13)/13.0
svcDist = ServiceDistribution(vals, probs)

##################################################
# Network, arrival patterns
svcArea   = readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)

#################################################
# Maximum values r and m can take
maxM  = sum([svcArea.bases[j]['alloc'] for j in svcArea.bases])
maxR  = -1

for i in svcArea.nodes:
	for j in svcArea.bases:
		temp = int(svcArea.getDist()[i][j] + svcArea.getNBdist()[i])
		if temp > maxR:
			maxR = temp

maxR += max(vals)

##################################################
# Obtaining eta values
eta      = np.zeros((maxR+1, maxM+1))
settings = {'OutputFlag': 0, 'MIPGap': 0.005}

for r in xrange(maxR + 1):
	print '%i of %i' % (r, maxR)
	for m in xrange(1, maxM+1):
		p = MMIP.ModelInstance(svcArea, arrStream, svcDist, m, r)
		p.solve(settings)
		eta[r][m] = p.getObjective()
	eta[r][0] = eta[r][1]


# Writing results to file
with open(filepath, 'w') as f:
	f.write('%i %i\n' % (maxR+1, maxM+1))
	fmtString = '%.4f ' * (maxM) + '%.4f\n'

	for r in xrange(maxR + 1):
		f.write(fmtString  % tuple(abs(eta[r])))
