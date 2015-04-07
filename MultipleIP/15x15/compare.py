import numpy as np
import time
from math import exp
from random import seed
from ...Methods.graph import readNetworkFile
from ...Methods.sample import confInt
from ...Methods import makeXLS
from ...Methods.gradientSearch import solvePIPs, lineSearch
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
from ...Classes.SamplePath import SamplePath
from ...Classes.PenaltyMultipliers import PenaltyMultipliers
from ...Simulation import policies
from ...Simulation.lowerBound import simulate as simLB
from ...Simulation.boundingSystem import simulate as simUB
from ...MultipleIP import PIP2 
from ...PerfectIP import IP

networkFile = "15x15//five.txt"
etaFile     = "eta.txt"
outputFile	= "compare.txt"
xlsFile     = "compare.xlsx"

import os.path
basepath = os.path.dirname(__file__)
etaPath  = os.path.join(basepath, etaFile) 
outPath  = os.path.join(basepath, outputFile)
xlsPath  = os.path.join(basepath, xlsFile)

#####################################################
# Basic inputs
T		= 1440
# Distribution: ceil(Y), where Y ~ Exponential(1/34)
mu        = 24.0
numVals   = 120
vals      = np.arange(1, numVals+1)
probs     = [exp(-(vals[i]-1)/mu)*(1 - exp(-1/mu))\
					 for i in xrange(numVals)]
probs[-1] += 1 - sum(probs)
svcDist   = ServiceDistribution(vals, probs)

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
utils = [0.05]

#####################################################
# Estimate objective value and gradient at current point
# seed1 used for calibrating penalty multipliers
# seed2 used for comparing bounds 
simN     = 25 
gradN    = 25
lineN    = 25
iters	 = 1
seed1	 = 33768
seed2	 = 12345
settings = {'OutputFlag' : 0}

# Objective values
ubObj    = np.zeros((len(utils), simN))
piObj    = np.zeros((len(utils), simN))
mxObj    = np.zeros((len(utils), simN))
lbObj    = np.zeros((len(utils), simN))

# Utilizations
ubUtil   = np.zeros((len(utils), simN))
piUtil   = np.zeros((len(utils), simN))
mxUtil   = np.zeros((len(utils), simN))
lbUtil   = np.zeros((len(utils), simN))

start = time.clock()
for h in xrange(len(utils)):
	print 'Arrival probability =  %.3f' % (1 - exp(-utils[h]))
	arrStream.updateP(1 - exp(-utils[h]))
	# Gradient Search
	for i in xrange(iters):
		print 'Iteration %i' % (i + 1)
	
		# Sampling the gradient    
		print 'Estimating gradient...'
		gamma = penalty.getGamma()
		seed(seed1)
		obj, nabla = solvePIPs(svcArea, arrStream, svcDist, gamma, PIP2,\
									 settings, gradN, freq=20)
		penalty.setNabla(nabla)

		print 'Line Search...'
		seed(seed1)															
		vals = lineSearch(svcArea, arrStream, svcDist, penalty, PIP2,\
									 settings, lineN, freq=20) 
		bestStep = 0
		bestVal  = np.mean(obj[:lineN])
		count	 = 0
			
		#print 'Step Size 0, Mean Obj. %.4f' % bestVal
		for j in penalty.getStepSizes():
			#print 'Step Size %.3f, Mean Obj. %.4f' % (j, vals[count])
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
		if (i+1)% 20 == 0:
			print 'Iteration %i' % (i+1)

		omega = SamplePath(svcArea, arrStream, svcDist)

		# Matt Maxwell's upper bound
		mxStats      = simUB(svcDists, omega)
		mxObj[h][i]  = mxStats['obj']
		mxUtil[h][i] = mxStats['util']

		# Simulated lower bound
		lbStats      = simLB(svcArea, omega, policies.nearestEffEmpty)
		lbObj[h][i]  = lbStats['obj']
		lbUtil[h][i] = lbStats['util']

		# Perfect information upper bound
		m1 = PIP2.ModelInstance(svcArea, arrStream, omega)
		m1.updateObjective(gamma)
		m1.solve(settings)
		ubObj[h][i]  = m1.getObjective()
		ubUtil[h][i] = m1.estimateUtilization()	

		# Penalized upper bound
		m2 = IP.ModelInstance(svcArea, arrStream, omega)
		m2.solve(settings)
		piObj[h][i]  = m2.getObjective()	
		piUtil[h][i] = m2.estimateUtilization()
						 
	print 'Arrival Probability = %.3f' % utils[h]
	print 'Lower Bound         : %.3f +/- %.3f'   % confInt(lbObj[h])
	print 'Perfect Information : %.3f +/- %.3f'   % confInt(piObj[h])
	print 'Penalized Bound     : %.3f +/- %.3f'   % confInt(ubObj[h])
	print 'Maxwell Bound       : %.3f +/- %.3f\n' % confInt(mxObj[h])

finish   = time.clock() 
print 'Search took %.4f seconds' % (finish - start)

# Writing results to file
with open(outPath, 'w') as f:
	f.write('%i 4\n' % len(utils))
	f.write('LowerBd PerfectInfo PenaltyBd MaxwellBd\n')
	for h in xrange(len(utils)):
		f.write('%.3f\n' % utils[h])
		temp1 = confInt(lbObj[h])
		temp2 = confInt(piObj[h])
		temp3 = confInt(ubObj[h])
		temp4 = confInt(mxObj[h])
		f.write('%.3f %.3f %.3f\n' % (temp1[0], temp1[1], np.average(lbUtil[h])))
		f.write('%.3f %.3f %.3f\n' % (temp2[0], temp2[1], np.average(piUtil[h])))
		f.write('%.3f %.3f %.3f\n' % (temp3[0], temp3[1], np.average(ubUtil[h])))
		f.write('%.3f %.3f %.3f\n' % (temp4[0], temp4[1], np.average(mxUtil[h])))

makeXLS.build(outPath, xlsPath)
