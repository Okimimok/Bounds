import numpy as np 
from random import seed
from ...Methods.graph import readNetworkFile
from ...Methods.sample import confInt
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.PenaltyMultipliers import PenaltyMultipliers
from ...Classes.SamplePath import SamplePath
from ...MultipleIP import PIP2

networkFile = "9x9//four.txt"
randomSeed	= 33768

#################################################
# Basic inputs
T		= 1440
svcDist = {}
for i in xrange(12, 25):
	svcDist[i] = 1.0/13

##################################################
# Network, arrival patterns
svcArea   = readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
arrStream.updateP(0.20)

##################################################
# Penalty Multipliers
gamma   = 0.1*np.ones(T+1)
penalty = PenaltyMultipliers(gamma)

##################################################
# Generating sample paths
N	  = 25 
piobj = np.zeros(N)

seed(randomSeed)
for k in xrange(N):
	if (k+1)% 10 == 0:
		print 'Iteration %i' % (k+1)

	omega  = SamplePath(svcArea, arrStream, svcDist)
	
	# Solver settings
	settings = {'OutputFlag' : 0}	

	# Penalized IP 
	p = PIP2.ModelInstance(svcArea, arrStream, omega)
	p.updateObjective(gamma)
	p.solve(settings)
	piobj[k] = p.getModel().objVal	

print 'PI Relaxation : %.3f +/- %.3f' % confInt(piobj)
