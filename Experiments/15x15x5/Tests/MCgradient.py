import numpy as np
import time
from random import seed
from ....Methods.network import readNetwork	
from os.path import abspath, dirname, realpath, join
from ....Methods.sample import confInt
from ....Upper.maxwell import readEta, readV
from ....Components.serviceDistribution import serviceDistribution
from ....Components.coveragePenalty import coveragePenalty
from ....Components.arrivalStream import arrivalStream
from ....Components.samplePath import samplePath
from ....Upper.gradient import fastFullSearch, fastSearch, fullSearch, solvePIPs
from ....Models import PIP2
#import pdb; pdb.set_trace()

basePath    = dirname(realpath(__file__))
networkFile = "five.txt"
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))

# Basic inputs
T	    = 1440
vals    = np.arange(12, 25, dtype = 'int64')
probs   = np.ones(13)/13
svcDist = serviceDistribution(vals, probs)

# Network, arrival patterns
svcArea   = readNetwork(networkPath)
arrStream = arrivalStream(svcArea, T)
arrStream.updateP(0.08)

# Penalty Multipliers
gamma	= np.zeros(T+1)
penalty = coveragePenalty(gamma)
penalty.setStepSizes([0.5, 1.0, 2.0, 4.0])

# Estimate objective value and gradient at current point
N     = 50
N2    = 50
iters = 1
seed1 = 33768
seed2 = 12345
settings = {'OutputFlag' : 0}

start = time.clock()
fastFullSearch(svcArea, arrStream, svcDist, penalty, PIP2, settings, N,\
							seed1, iters, freq=-1, debug=True)
print 'Search took %.3f seconds' % (time.clock()-start)
print penalty.getGamma()
# Upon termination, sample the objective value at the point selected
print 'Debiasing...'	
seed(seed2) 
obj, _ = solvePIPs(svcArea, arrStream, svcDist, gamma, PIP2, settings, N2)
print 'Final upper bound: %.4f +/- %.4f' % confInt(obj)
