import numpy as np
import time
from math import exp
from random import seed
from ...LowerIP import compliance
from ...Methods.sample import confInt
from ...Methods import makeXLS, readFiles
from ...Methods.gradientSearch import fullSearch
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
from ...Classes.SamplePath import SamplePath
from ...Classes.PenaltyMultipliers import PenaltyMultipliers
from ...Simulation.lowerBound import simulate as simLB
from ...Simulation.tablePolicies import compliance as simCT
from ...MultipleIP import PIP2 

networkFile = "15x15//fiveV2.txt"
etaFile     = "eta.txt"
outputFile	= "compareV2.txt"
xlsFile     = "compareV2.xlsx"

import os.path
basepath = os.path.dirname(__file__)
etaPath  = os.path.join(basepath, etaFile) 
outPath  = os.path.join(basepath, outputFile)
xlsPath  = os.path.join(basepath, xlsFile)

# Distribution: ceil(Y), where Y ~ Exponential(1/24)
T	      = 1440
mu        = 24.0
numVals   = 120
vals      = np.arange(1, numVals+1)
probs     = [exp(-(vals[i]-1)/mu)*(1 - exp(-1/mu))\
					 for i in xrange(numVals)]
probs[-1] += 1 - sum(probs)
svcDist   = ServiceDistribution(vals, probs)

# Network, arrival patterns
svcArea   = readFiles.readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)

# Penalty Multipliers
gamma	= np.zeros(T+1)
penalty = PenaltyMultipliers(gamma)
penalty.setStepSizes([0.5, 1.0, 2.0, 4.0])

# Service distributions for Maxwell's bounding system 
svcDists = readFiles.readEtaFile(etaPath)

# Arrival probabilities to be tested
probs = [0.10]
H     = len(probs)

# Compliance table from text file vs. compliance table from MECRP
tables = {1: {}, 2: {}}
fixed  = compliance.readTable("15x15//five.txt")
w      = [16, 8, 4, 2, 1]
for h in xrange(H):
	tables[1][h] = fixed
	tables[2][h] = compliance.buildTable(svcArea, arrStream, svcDist, w)

#####################################################
# Gradient search and bound comparison
# seed1 used for calibrating penalty multipliers
# seed2 used for comparing bounds 
N        = 500
iters	 = 3
seed1	 = 33768
seed2	 = 12345
settings = {'OutputFlag' : 0}

# Objective values
names = ['LowerBd', 'PerfectInfo', 'PenaltyBd']
obj   = {}
util  = {}
for name in names:
	obj[name]  = np.zeros((H, N))
	util[name] = np.zeros((H, N))
	
# The winning compliance tables
tBest = np.zeros(H, dtype = 'int64')
oBest = -1
start = time.clock()
for h in xrange(H):
	print 'Arrival probability =  %.3f' %  probs[h]
	arrStream.updateP(probs[h])
	
	# Gradient search
	fullSearch(svcArea, arrStream, svcDist, penalty, PIP2, settings, N, seed1, \
					iters, debug=True)

	# Computing upper and lower bounds on a separate set of sample paths
	print 'Debiasing...'
	seed(seed2)
	tmp = {}
	for k in tables:
		tmp[k] = {'obj': np.zeros(N), 'util': np.zeros(N)}

	for i in xrange(N):
		omega = SamplePath(svcArea, arrStream, svcDist)

		# Perfect information upper bound
		m = PIP2.ModelInstance(svcArea, arrStream, omega)
		m.solve(settings)
		obj['PerfectInfo'][h][i]  = m.getObjective()	
		util['PerfectInfo'][h][i] = m.estimateUtilization()

		# Penalized upper bound
		m.updateObjective(gamma)
		m.solve(settings)
		obj['PenaltyBd'][h][i]  = m.getObjective()
		util['PenaltyBd'][h][i] = m.estimateUtilization()	

		# Comparing lower bounds		
		for k in tables: 		
			stats = simLB(svcArea, omega, lambda simState, location, fel, svcArea:\
							simCT(simState, location, fel, svcArea, tables[k][h]))
			tmp[k]['obj'][i] = stats['obj']
			tmp[k]['util'][i] = stats['util']

	# Finding best compliance table policy
	for k in tables:
		if np.average(tmp[k]['obj']) > oBest:
			oBest    = np.average(tmp[k]['obj'])
			tBest[h] = k
    
	obj['LowerBd'][h]  = np.copy(tmp[tBest[h]]['obj'])
	util['LowerBd'][h] = np.copy(tmp[tBest[h]]['util'])	
		
	print 'Arrival Probability = %.3f' % probs[h]
	for name in names:	
		print name + ': %.3f +/- %.3f' % confInt(obj[name][h])


finish   = time.clock() 
print 'Search took %.4f seconds' % (finish - start)

# Writing results to file
with open(outPath, 'w') as f:
	f.write('%i %i\n' % (H, len(names)))
	for name in names: 
		f.write(name + ' ')
	f.write('\n')

	for h in xrange(H):
		f.write('%.3f %i \n' % (probs[h], tBest[h]))
		for name in names:
			tmp = confInt(obj[name][h])
			f.write('%.3f %.3f %.3f\n' % (tmp[0], tmp[1], np.average(util[name][h])))

makeXLS.build(outPath, xlsPath)
