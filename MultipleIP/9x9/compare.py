import numpy as np
import time
from random import seed
from ...Methods.graph import readNetworkFile
from ...Methods.sample import confInt
from ...Methods.gradientSearch import solvePIPs, lineSearch
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
from ...Classes.SamplePath import SamplePath
from ...Classes.PenaltyMultipliers import PenaltyMultipliers
from ...Simulation import policies
from ...Simulation.simulation import simulate as simLB
from ...Simulation.boundingSystem import simulate as simUB
from ...MultipleIP import PIP2 
from ...PerfectIP import IP

networkFile = "9x9//four.txt"
etaFile     = "eta.txt"
outputFile	= "compare.txt"

import os.path
basepath = os.path.dirname(__file__)
etaPath  = os.path.abspath(os.path.join(basepath, etaFile)) 
outPath  = os.path.abspath(os.path.join(basepath, outputFile))

#####################################################
# Basic inputs
T		= 1440
vals    = np.arange(12, 25, dtype = 'int64')
probs   = np.ones(13)/13
svcDist = ServiceDistribution(vals, probs)

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
# Service distributions for Maxwell's bounding system 
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

#####################################################
# System utilizations tested (for comparing bounds)
#utils	= [0.04, 0.08, 0.12, 0.16, 0.20, 0.24, 0.28, 0.32]
utils = [0.15]

#####################################################
# Estimate objective value and gradient at current point
# seed1 used for calibrating penalty multipliers
# seed2 used for comparing bounds 
simN	 = 100 
gradN	 = 100
lineN	 = 100
iters	 = 5
seed1	 = 33768
seed2	 = 12345
ub		 = np.zeros((len(utils), simN))
pinfo    = np.zeros((len(utils), simN))
maxwell  = np.zeros((len(utils), simN))
nearEfEm = np.zeros((len(utils), simN))
settings = {'OutputFlag' : 0}

start = time.clock()
for h in xrange(len(utils)):
	print 'Arrival probability =  %.3f' % utils[h]
	arrStream.updateP(utils[h])
	# Gradient Search
	for i in xrange(iters):
		print 'Iteration %i' % (i + 1)
	
		# Sampling the gradient    
		print 'Estimating gradient...'
		gamma = penalty.getGamma()
		seed(seed1)
		obj, nabla = solvePIPs(svcArea, arrStream, svcDist, gamma, PIP2,\
									 settings, gradN, freq=10)
		penalty.setNabla(nabla)

		print 'Line Search...'
		seed(seed1)															
		vals = lineSearch(svcArea, arrStream, svcDist, penalty, PIP2,\
									 settings, lineN, freq=5) 
		bestStep = 0
		bestVal  = np.mean(obj[:lineN])
		count	 = 0
	
		print 'Step Size 0, Mean Obj. %.4f' % bestVal
		for j in penalty.getStepSizes():
			print 'Step Size %.3f, Mean Obj. %.4f' % (j, vals[count])
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
	print 'Debiasing...'
	seed(seed2)
	for i in xrange(simN):
		omega		   = SamplePath(svcArea, arrStream, svcDist)
		maxwell[h][i]  = simUB(svcDists, omega)
		nearEfEm[h][i] = simLB(svcArea, omega, policies.nearestEffEmpty)

		m1 = PIP2.ModelInstance(svcArea, arrStream, omega)
		m1.updateObjective(gamma)
		m1.solve(settings)
		ub[h][i] = m1.getModel().objVal	

		m2 = IP.ModelInstance(svcArea, arrStream, omega)
		m2.solve(settings)
		pinfo[h][i] = m2.getModel().objVal	
						 
finish = time.clock() 
print 'Search took %.4f seconds' % (finish - start)

for h in xrange(len(utils)):
	print 'Arrival Probability = %.3f' % utils[h]
	print 'Perfect Information : %.3f +/- %.3f'   % confInt(pinfo[h])
	print 'Upper Bound         : %.3f +/- %.3f'   % confInt(ub[h])
	print 'Maxwell Bound       : %.3f +/- %.3f'   % confInt(maxwell[h])
	print 'Nearest Eff. Empty  : %.3f +/- %.3f\n' % confInt(nearEfEm[h])

# Writing results to file
with open(outPath, 'w') as f:
	f.write('%i\n' % len(utils))
	for h in xrange(len(utils)):
		f.write('%.3f\n' % utils[h])
		f.write('%.3f %.3f\n' % confInt(pinfo[h]))
		f.write('%.3f %.3f\n' % confInt(ub[h]))
		f.write('%.3f %.3f\n' % confInt(maxwell[h]))
		f.write('%.3f %.3f\n' % confInt(nearEfEm[h]))
