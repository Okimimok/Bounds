import numpy as np
import time
from random import seed
from ...Methods.sample import confInt
from ...Methods import makeXLS, readFiles
from ...Methods.gradientSearch import fullSearch
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
from ...Classes.SamplePath import SamplePath
from ...Classes.PenaltyMultipliers import PenaltyMultipliers
from ...Simulation import policies
from ...Simulation.lowerBound import simulate as simLB
from ...Simulation.boundingSystem import simulate as simUB
from ...MultipleIP import PIP2 

networkFile = "9x9//four.txt"
etaFile     = "eta.txt"
vFile       = "v.txt"
outputFile	= "compareTest.txt"
xlsFile     = "compareTest.xlsx"

import os.path
basepath = os.path.dirname(__file__)
etaPath  = os.path.join(basepath, etaFile) 
outPath  = os.path.join(basepath, outputFile)
xlsPath  = os.path.join(basepath, xlsFile)
vPath    = os.path.join(basepath, vFile)

# Basic inputs
T		= 1440
vals    = np.arange(12, 25, dtype = 'int64')
probs   = np.ones(13)/13
svcDist = ServiceDistribution(vals, probs)

# Network, arrival patterns
svcArea   = readFiles.readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)

# Penalty Multipliers
gamma	= np.zeros(T+1)
penalty = PenaltyMultipliers(gamma)
penalty.setStepSizes([0.5, 1.0, 2.0, 4.0])

# Service distributions for Maxwell's bounding system 
svcDists = readFiles.readEtaFile(etaPath)
v        = readFiles.readVFile(vPath)
# System utilizations tested (for comparing bounds)
#probs	= [0.04, 0.08, 0.12, 0.16, 0.20, 0.24, 0.28, 0.32]
probs = [0.10]
H     = len(probs)

# Estimate objective value and gradient at current point
# seed1 used for calibrating penalty multipliers
# seed2 used for comparing bounds 
N        = 500
iters	 = 4 
seed1	 = 33768
seed2	 = 12345
settings = {'OutputFlag' : 0}

# Objective values
ubObj = np.zeros((H, N))
piObj = np.zeros((H, N))
mxObj = np.zeros((H, N))
lbObj = np.zeros((H, N))

# Utilizations
ubUtil   = np.zeros((H, N))
piUtil   = np.zeros((H, N))
mxUtil   = np.zeros((H, N))
lbUtil   = np.zeros((H, N))

start = time.clock()
for h in xrange(H):
	print 'Arrival probability =  %.3f' % probs[h]
	arrStream.updateP(probs[h])
	# Gradient search
	fullSearch(svcArea, arrStream, svcDist, penalty, PIP2, settings, N, seed1, \
					iters, debug=True)

	# Computing upper and lower bounds on a separate set of sample paths
	print 'Debiasing...'
	seed(seed2)
	for i in xrange(N):
		if (i+1)% 20 == 0:
			print 'Iteration %i' % (i+1)

		omega = SamplePath(svcArea, arrStream, svcDist)

		# Matt Maxwell's upper bound
		mxStats      = simUB(svcDists, omega, v)
		mxObj[h][i]  = mxStats['obj']
		mxUtil[h][i] = mxStats['util']

		# Simulated lower bound
		lbStats      = simLB(svcArea, omega, policies.nearestEffEmpty)
		lbObj[h][i]  = lbStats['obj']
		lbUtil[h][i] = lbStats['util']

		# Perfect information upper bound
		m = PIP2.ModelInstance(svcArea, arrStream, omega)
		m.solve(settings)
		piObj[h][i]  = m.getObjective()	
		piUtil[h][i] = m.estimateUtilization()

		# Penalized upper bound
		m.updateObjective(gamma)
		m.solve(settings)
		ubObj[h][i]  = m.getObjective()
		ubUtil[h][i] = m.estimateUtilization()	

						 
	print 'Arrival Probability = %.3f' % probs[h]
	print 'Lower Bound         : %.3f +/- %.3f'   % confInt(lbObj[h])
	print 'Perfect Information : %.3f +/- %.3f'   % confInt(piObj[h])
	print 'Penalized Bound     : %.3f +/- %.3f'   % confInt(ubObj[h])
	print 'Maxwell Bound       : %.3f +/- %.3f\n' % confInt(mxObj[h])

finish   = time.clock() 
print 'Search took %.4f seconds' % (finish - start)

# Writing results to file
with open(outPath, 'w') as f:
	f.write('%i 4\n' % H)
	f.write('LowerBd PerfectInfo PenaltyBd MaxwellBd\n')
	for h in xrange(H):
		f.write('%.3f\n' % probs[h])
		temp1 = confInt(lbObj[h])
		temp2 = confInt(piObj[h])
		temp3 = confInt(ubObj[h])
		temp4 = confInt(mxObj[h])
		f.write('%.3f %.3f %.3f\n' % (temp1[0], temp1[1], np.average(lbUtil[h])))
		f.write('%.3f %.3f %.3f\n' % (temp2[0], temp2[1], np.average(piUtil[h])))
		f.write('%.3f %.3f %.3f\n' % (temp3[0], temp3[1], np.average(ubUtil[h])))
		f.write('%.3f %.3f %.3f\n' % (temp4[0], temp4[1], np.average(mxUtil[h])))

makeXLS.build(outPath, xlsPath)
