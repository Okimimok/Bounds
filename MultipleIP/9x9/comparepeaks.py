import numpy as np
import time
from random import seed
from ...Methods.graph import readNetworkFile
from ...Methods.sample import confInt
from ...Methods.gradientSearch import solvePIPs, lineSearch
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.SamplePath import SamplePath
from ...Classes.PenaltyMultipliers import PenaltyMultipliers
from ...Simulation import policies
from ...Simulation.simulation import simulate
from ...MultipleIP import PIP2, PIP2Search
from ...PerfectIP import IP
networkFile = "9x9//fourpeaks.txt"
outputFile	= "comparepeaks.txt"

import os.path
import numpy as np


basepath  = os.path.dirname(__file__)
filepath  = os.path.abspath(os.path.join(basepath, outputFile))

#####################################################
# Basic inputs
T		= 1440
svcDist = {}
for i in xrange(12, 25):
	svcDist[i] = 1.0/13

#####################################################
# Network, arrival patterns
svcArea   = readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)

#####################################################
# Penalty Multipliers
gamma	= np.zeros(T+1)
penalty = PenaltyMultipliers(gamma)
penalty.setStepSizes([0.5, 1.0, 2.0, 4.0])

#####################################################
# System utilizations tested (for comparing bounds)
utils	= [0.04, 0.08, 0.12, 0.16, 0.20, 0.24, 0.28, 0.32]

#####################################################
# Estimate objective value and gradient at current point
# seed1 used for calibrating penalty multipliers
# seed2 used for comparing bounds 
simN	 = 100 
gradN	 = 100
lineN	 = 50
iters	 = 8
seed1	 = 33768
seed2	 = 12345
ub		 = np.zeros((len(utils), simN))
pinfo    = np.zeros((len(utils), simN))
naive	 = np.zeros((len(utils), simN))
near	 = np.zeros((len(utils), simN))
nearEm	 = np.zeros((len(utils), simN))
nearEfEm = np.zeros((len(utils), simN))


start = time.clock()
for h in xrange(len(utils)):
	print 'Arrival probability =  %.3f' % utils[h]
	arrStream.updateP(utils[h])
	# Gradient Search
	for i in xrange(iters):
		print 'Iteration %i' % (i + 1)
	
		# Sampling the gradient    
		print 'Estimating gradient...'
		seed(seed1)
		obj, nabla = solvePIPs(svcArea, arrStream, svcDist, penalty,\
								 gradN, PIP2.solve, flag=False, freq=gradN+1)
		penalty.setNabla(nabla)
															  
		# Determining how far to move along the gradient 
		print 'Finding step size...'
		seed(seed1)															 
		vals = lineSearch(svcArea, arrStream, svcDist, penalty, lineN,\
							 PIP2Search.solve, freq=lineN+1) 
		bestStep = 0
		bestVal  = np.mean(obj[:lineN])
		count	 = 0
	
		for j in penalty.getStepSizes():
			if vals[count] < bestVal:
				bestStep = j
				bestVal  = vals[count]
			count += 1
		
		# If step size is zero, take smaller steps. O/w, update gradient.
		if bestStep == 0:
			penalty.scaleGamma(0.5)
		else:
			penalty.updateGamma(-bestStep*nabla)

	# Computing upper and lower bounds on a separate set of sample paths
	seed(seed2)
	for i in xrange(simN):
		omega		   = SamplePath(svcArea, arrStream, svcDist)
		pinfo[h][i],_  = IP.solve(svcArea, arrStream, omega)
		ub[h][i], _	   = PIP2.solve(svcArea, arrStream, omega, penalty)
		naive[h][i]    = simulate(svcArea, omega, policies.naive)
		near[h][i]	   = simulate(svcArea, omega, policies.nearest)
		nearEm[h][i]   = simulate(svcArea, omega, policies.nearestEmpty)
		nearEfEm[h][i] = simulate(svcArea, omega, policies.nearestEffEmpty)
						 
finish = time.clock() 
print 'Search took %.4f seconds' % (finish - start)

for h in xrange(len(utils)):
	print 'Arrival Probability = %.3f' % utils[h]
	print 'Perfect Information :  %.3f +/- %.3f'  % confInt(pinfo[h])
	print 'Upper Bound         : %.3f +/- %.3f'   % confInt(ub[h])
	print 'Naive Policy        : %.3f +/- %.3f'   % confInt(naive[h])
	print 'Nearest Policy      : %.3f +/- %.3f'   % confInt(near[h])
	print 'Nearest Empty       : %.3f +/- %.3f'   % confInt(nearEm[h])
	print 'Nearest Eff. Empty  : %.3f +/- %.3f\n' % confInt(nearEfEm[h])

# Writing results to file
with open(filepath, 'w') as f:
	f.write('%i\n' % len(utils))
	for h in xrange(len(utils)):
		f.write('%.3f\n' % utils[h])
		f.write('%.3f %.3f\n' % confInt(pinfo[h])
		f.write('%.3f %.3f\n' % confInt(ub[h])
		f.write('%.3f %.3f\n' % confInt(naive[h])
		f.write('%.3f %.3f\n' % confInt(near[h])
		f.write('%.3f %.3f\n' % confInt(nearEm[h])
		f.write('%.3f %.3f\n' % confInt(nearEfEm[h])
