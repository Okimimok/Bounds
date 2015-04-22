import numpy as np 
from random import seed
from os.path import abspath, dirname, realpath, join
from ....Methods.network import readNetwork	
from ....Methods.sample import confInt
from ....Components.serviceDistribution import serviceDistribution
from ....Components.coveragePenalty import coveragePenalty
from ....Components.arrivalStream import arrivalStream
from ....Components.samplePath import samplePath
from ....Models import PIP2

basePath    = dirname(realpath(__file__))
networkFile = "twelve.txt"
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))
randomSeed	= 12345

# Basic inputs
T		= 1440
vals    = np.arange(12, 25, dtype = 'int64')
probs   = np.ones(13)/13
svcDist = serviceDistribution(vals, probs)

# Network, arrival patterns
svcArea   = readNetwork(networkPath)
arrStream = arrivalStream(svcArea, T)
arrStream.updateP(0.25)

# Penalty 
gamma   = np.zeros(T+1)
penalty = coveragePenalty(gamma)

##################################################
# Generating sample paths
N	   = 50 
ubObj  = np.zeros(N)
ubUtil = np.zeros(N)

seed(randomSeed)
for k in xrange(N):
	if (k+1)% 10 == 0:
		print 'Iteration %i' % (k+1)

	omega     = samplePath(svcArea, arrStream, svcDist)
	settings  = {'OutputFlag' : 0}	
	p         = PIP2.ModelInstance(svcArea, arrStream, omega, gamma)
	p.solve(settings)
	ubObj[k]  = p.getObjective()
	ubUtil[k] = p.estimateUtilization()	

print 'Objective   : %.3f +/- %.3f' % confInt(ubObj)
print 'Utilization : %.3f +/- %.3f' % confInt(ubUtil)
