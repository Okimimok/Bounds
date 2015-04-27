import sys
import configparser
import numpy as np 
import time
from random import seed
from os.path import abspath, dirname, realpath, join
from ...Methods.network import readNetwork	
from ...Methods.sample import confInt
from ...Methods.dists import readSvcDist
from ...Components.ArrStream import ArrStream
from ...Components.CvgPenalty import CvgPenalty
from ...Upper.gradient import fullSearch, solvePIPs
from ...Models import PIP2

def main():
	basePath   = dirname(realpath(__file__))
	configPath = abspath(join(abspath(join(basePath, "..//")), sys.argv[1]))
	cp         = configparser.ConfigParser()
	cp.read(configPath)

	networkFile = cp['files']['networkFile']
	sdFile      = cp['files']['sdFile']
	gradFile    = cp['files']['gradFile']
	networkPath = abspath(join(abspath(join(basePath, "..//")), networkFile))
	sdPath      = abspath(join(abspath(join(basePath, "..//")), sdFile))
	gradPath    = abspath(join(abspath(join(basePath, "..//")), gradFile))

    # Basic inputs
	seed1 = cp['inputs'].getint('seed1')
	seed2 = cp['inputs'].getint('seed2')
	T     = cp['inputs'].getint('T')
	N     = cp['inputs'].getint('N')
	prob  = cp['inputs'].getfloat('prob')
	iters = cp['inputs'].getint('iters')
	gamma = eval(cp['inputs']['gamma'])
	steps = eval(cp['inputs']['steps'])
        
	# Service distribution    
	sdist = readSvcDist(sdPath)
 
	# System components: network, arrival patterns, penalty
	svca = readNetwork(networkPath)
	astr = ArrStream(svca, T)
	astr.updateP(prob)

	# Penalty Multipliers
	penalty = CvgPenalty(gamma)
	penalty.setStepSizes(steps)
	
	# Solver settings    
	settings = {}
	for item in cp['settings']:
		settings[item] = eval(cp['settings'][item])
		
	# Displaying progress
	debug = cp['log'].getboolean('debug')
	freq  = cp['log'].getint('freq')
	if freq < 0: freq = N+1

	start = time.clock()
	fullSearch(svca, astr, sdist, penalty, PIP2, settings, N, seed1, iters,\
							 freq=freq, debug=debug)
	print('Search took %.4f seconds' % (time.clock()-start))
	print('Debiasing...')
	seed(seed2) 
	obj, _ = solvePIPs(svca, astr, sdist, gamma, PIP2, settings, N, freq=freq)
	print('Final upper bound: %.4f +/- %.4f' % confInt(obj))

	'''
	# Writing gradient to file
	with open(gradPath, 'w') as f:
		f.write('%i\n' % T)
		gamma = penalty.getGamma()
		for t in range(T+1):
			f.write('%i %.6f\n' % (t, gamma[t]))
	'''
				
if __name__ == '__main__':
    main()
