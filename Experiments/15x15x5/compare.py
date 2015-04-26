import numpy as np
import time
from random import seed
from os.path import abspath, dirname, realpath, join
from ...Methods.network import readNetwork	
from ...Methods.sample import confInt
from ...Lower.compliance import readTable
from ...Upper.maxwell import readEta, readV
from ...Upper.gradient import fastFullSearch, solvePIPs
from ...Components.serviceDistribution import serviceDistribution
from ...Components.coveragePenalty import coveragePenalty
from ...Components.arrivalStream import arrivalStream
from ...Components.samplePath import samplePath
from ...Simulation.lowerAll import simulate as simLB
from ...Simulation.tablePolicies import compliance
from ...Models import PIP2, MMIP2

basePath	= dirname(realpath(__file__))
networkFile = "five.txt"
etaFile		= "eta.txt"
vFile		= "v.txt"
outputFile	= "compare.txt"
tableFile   = "daskinTable.txt"
etaPath		= join(basePath, "Inputs",  etaFile)
vPath		= join(basePath, "Inputs",  vFile)
networkPath = join(basePath, "Graph",  networkFile)
outputPath	= join(basePath, "Results", outputFile)
tablePath   = join(basePath, "Inputs", tableFile)

# Basic inputs
T		= 1440
vals	= np.arange(12, 25, dtype = 'int64')
probs	= np.ones(13)/13
svcDist = serviceDistribution(vals, probs)

# Network, arrival patterns
svcArea   = readNetwork(networkPath)
arrStream = arrivalStream(svcArea, T)

# Penalty Multipliers
gamma	= np.zeros(T+1)
penalty = coveragePenalty(gamma)
penalty.setStepSizes([0.5, 1.0, 2.0, 4.0])

# Service distributions for Maxwell's bounding system 
mxwDists = readEta(etaPath)
v		 = readV(vPath)

# Compliance table
table = readTable(tablePath)

# Arrival probabilities tested (for comparing bounds)
probs = [0.01, 0.02, 0.03]
H	  = len(probs)

# seed1 used for calibrating penalty
# seed2 used for comparing bounds 
N		  = 1000
iters	  = 5 
seed1	  = 33768
seed2	  = 12345
settings  = {'OutputFlag' : 0}
settings2 = {'OutputFlag' : 0, 'TimeLimit' : 120}

# Summary statistics
lb = {'obj': np.zeros((H,N)), 'util': np.zeros((H,N)),\
			 'miss': np.zeros((H,N)), 'late': np.zeros((H, N))}
ub = {'obj': np.zeros((H,N)), 'util' : np.zeros((H,N))}
pi = {'obj': np.zeros((H,N)), 'util' : np.zeros((H,N))}
mx = {'obj': np.zeros((H,N))}

start = time.clock()
for h in xrange(H):
	print 'Arrival probability =  %.3f' % probs[h]
	arrStream.updateP(probs[h])
	# Gradient search
	fastFullSearch(svcArea, arrStream, svcDist, penalty, PIP2, settings, N,
							 seed1, iters, freq = 50)

	# Computing upper and lower bounds on a separate set of sample paths
	print 'Debiasing...'
	seed(seed2)
	for i in xrange(N):
		omega  = samplePath(svcArea, arrStream, svcDist, mxwDists)

		m = MMIP2.ModelInstance(svcArea, arrStream, omega, v)
		m.solve(settings2)
		mx['obj'][h][i] = m.getObjective()
		if m.getModel().Status == 9:
			print 'Time limit reached, gap %.4f' % (100*m.getModel().MIPGap)

		lbStats = simLB(svcArea, omega, lambda simState, location, fel, svcArea:\
				compliance(simState, location, fel, svcArea, table))
		lb['obj'][h][i]  = lbStats['obj']
		lb['util'][h][i] = lbStats['util']
		lb['late'][h][i] = lbStats['late']
		lb['miss'][h][i] = lbStats['miss']

		m = PIP2.ModelInstance(svcArea, arrStream, omega)
		m.solve(settings)
		pi['obj'][h][i]  = m.getObjective()	
		pi['util'][h][i] = m.estimateUtilization()

		m.updateObjective(gamma)
		m.solve(settings)
		ub['obj'][h][i]  = m.getObjective()
		ub['util'][h][i] = m.estimateUtilization()	

	print 'Lower Bound         : %.3f +/- %.3f'   % confInt(lb['obj'][h])
	print 'Perfect Information : %.3f +/- %.3f'   % confInt(pi['obj'][h])
	print 'Penalized Bound     : %.3f +/- %.3f'   % confInt(ub['obj'][h])
	print 'Maxwell Bound       : %.3f +/- %.3f\n' % confInt(mx['obj'][h])

finish	 = time.clock() 
print 'Search took %.4f seconds' % (finish - start)

# Writing results to file
with open(outputPath, 'w') as f:
	f.write('%i 4\n' % H)
	for h in xrange(H):
		f.write('%.3f\n' % probs[h])
		temp1 = confInt(lb['obj'][h])
		temp2 = confInt(pi['obj'][h])
		temp3 = confInt(ub['obj'][h])
		temp4 = confInt(mx['obj'][h])
		f.write('Lower Bound %.3f %.3f %.3f %.3f %.3f\n' % (temp1[0], temp1[1],\
					np.average(lb['util'][h]), np.average(lb['late'][h]),\
					np.average(lb['miss'][h])))
		f.write('PerfectInfo %.3f %.3f %.3f\n' % (temp2[0], temp2[1],\
						 np.average(pi['util'][h])))
		f.write('PenaltyBd   %.3f %.3f %.3f\n' % (temp3[0], temp3[1],\
						 np.average(ub['util'][h])))
		f.write('MaxwellBd   %.3f %.3f\n' % (temp4[0], temp4[1]))