import sys, time, configparser
import numpy as np
from random import seed
from os.path import abspath, dirname, realpath, join
from ...Methods.network import readNetwork	
from ...Methods.sample import confInt
from ...Methods.dists import readSvcDist
from ...Upper.maxwell import readEta, readV
from ...Lower.compliance import readTable
from ...Upper.gradient import fullSearch
from ...Components.ArrStream import ArrStream
from ...Components.CvgPenalty import CvgPenalty
from ...Components.SamplePath import SamplePath
from ...Simulation.lowerAll import simulate as simLB
from ...Simulation.tablePolicies import compliance
from ...Models import PIP2, MMIP2

def main():
	basePath   = dirname(realpath(__file__))
	configPath = abspath(join(abspath(join(basePath, "..//")), sys.argv[1]))
	cp         = configparser.ConfigParser()
	cp.read(configPath)
				
	networkFile = cp['files']['networkFile']
	etaFile     = cp['files']['etaFile']
	vFile       = cp['files']['vFile']
	sdFile      = cp['files']['sdFile']
	tableFile   = cp['files']['tableFile']
	outputFile  = cp['files']['outputFile']
	#gradFile    = cp['files']['gradFile']

	networkPath = abspath(join(abspath(join(basePath, "..//")), networkFile))
	sdPath      = abspath(join(abspath(join(basePath, "..//")), sdFile))
	vPath       = abspath(join(abspath(join(basePath, "..//")), vFile))
	etaPath     = abspath(join(abspath(join(basePath, "..//")), etaFile))
	tablePath   = abspath(join(abspath(join(basePath, "..//")), tableFile))
	outputPath  = abspath(join(abspath(join(basePath, "..//")), outputFile))
	#gradPath    = abspath(join(abspath(join(basePath, "..//")), gradFile))

	# Basic inputs
	seed1 = cp['inputs'].getint('seed1')
	seed2 = cp['inputs'].getint('seed2')
	T     = cp['inputs'].getint('T')
	N     = cp['inputs'].getint('N')
	iters = cp['inputs'].getint('iters')
	probs = eval(cp['inputs']['probs'])
	gamma = eval(cp['inputs']['gamma'])
	steps = eval(cp['inputs']['steps'])
	H     = len(probs)
	debug = cp['log'].getboolean('debug')

	# Service distribution
	sdist = readSvcDist(sdPath)

	# System components: network, arrival patterns, penalty
	svca = readNetwork(networkPath)
	astr = ArrStream(svca, T)

	# Penalty Multipliers
	penalty = CvgPenalty(gamma)
	penalty.setStepSizes(steps)

	# Service distributions for Maxwell's bounding system 
	mdists = readEta(etaPath)
	v      = readV(vPath) 

	# Compliance table	
	table = readTable(tablePath)	

	# Solver settings    
	settings = {}
	for item in cp['settings']:
		settings[item] = eval(cp['settings'][item])
		
	# Displaying progress
	freq = cp['log'].getint('freq')
	if freq < 0: freq = N+1

	# Summary statistics
	lb = {'obj': np.zeros((H,N)), 'util': np.zeros((H,N)),\
			 'miss': np.zeros((H,N)), 'late': np.zeros((H, N))}
	ub = {'obj': np.zeros((H,N)), 'util' : np.zeros((H,N))}
	pi = {'obj': np.zeros((H,N)), 'util' : np.zeros((H,N))}
	mx = {'obj': np.zeros((H,N))}

	start = time.clock()
	for h in range(H):
		print('Arrival probability = %.3f' % probs[h])
		astr.updateP(probs[h])
		fullSearch(svca, astr, sdist, penalty, PIP2, settings, N, seed1, iters,\
					debug=debug)

		# Computing upper and lower bounds on a separate set of sample paths
		print('Debiasing...')
		seed(seed2)
		for i in range(N):
			if (i+1)% freq == 0: print('Iteration %i' % (i+1))

			omega  = SamplePath(svca, astr, svcDist=sdist, mxwDist=mdists)
			m      = MMIP2.ModelInstance(svca, astr, omega, v)
			m.solve(settings)
			mx['obj'][h][i] = m.getObjective()

			lbStats  = simLB(svca, omega, lambda state, location, fel, svcea:\
						compliance(state, location, fel, svca, table))
			lb['obj'][h][i]  = lbStats['obj']
			lb['util'][h][i] = lbStats['util']
			lb['late'][h][i] = lbStats['late']
			lb['miss'][h][i] = lbStats['miss']

			m = PIP2.ModelInstance(svca, astr, omega)
			m.solve(settings)
			pi['obj'][h][i]  = m.getObjective()	
			pi['util'][h][i] = m.estimateUtilization()

			m.updateObjective(gamma)
			m.solve(settings)
			ub['obj'][h][i]  = m.getObjective()
			ub['util'][h][i] = m.estimateUtilization()	

		print('Lower Bound         : %.3f +/- %.3f'   % confInt(lb['obj'][h]))
		print('Perfect Information : %.3f +/- %.3f'   % confInt(pi['obj'][h]))
		print('Penalized Bound     : %.3f +/- %.3f'   % confInt(ub['obj'][h]))
		print('Maxwell Bound       : %.3f +/- %.3f\n' % confInt(mx['obj'][h]))

	print('Search took %.4f seconds' % (time.clock() - start))

	# Writing results to file
	with open(outputPath, 'w') as f:
		f.write('%i 4\n' % H)
		for h in range(H):
			f.write('%.3f\n' % probs[h])
			temp1 = confInt(lb['obj'][h])
			temp2 = confInt(pi['obj'][h])
			temp3 = confInt(ub['obj'][h])
			temp4 = confInt(mx['obj'][h])
			f.write('LowerBd %.3f %.3f %.3f %.3f %.3f\n' % (temp1[0], temp1[1],\
					np.average(lb['util'][h]), np.average(lb['late'][h]),\
					np.average(lb['miss'][h])))
			f.write('PerfectInfo %.3f %.3f %.3f\n' %\
					 (temp2[0], temp2[1], np.average(pi['util'][h])))
			f.write('PenaltyBd %.3f %.3f %.3f\n' %\
					 (temp3[0], temp3[1], np.average(ub['util'][h])))
			f.write('MaxwellBd %.3f %.3f\n' % (temp4[0], temp4[1]))

if __name__ == '__main__':
    main()
