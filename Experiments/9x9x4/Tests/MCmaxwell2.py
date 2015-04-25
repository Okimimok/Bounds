import sys
import configparser
import numpy as np
from random import seed
from ....Methods.network import readNetwork	
from os.path import abspath, dirname, realpath, join
from ....Methods.sample import confInt
from ....Upper.maxwell import readEta, readV
from ....Components.ArrStream import ArrStream
from ....Components.SamplePath import SamplePath
from ....Components.SvcDist import SvcDist
from ....Models import MMIP2

def main():
	basePath   = dirname(realpath(__file__))
	configPath = abspath(join(basePath, sys.argv[1]))
	cp         = configparser.ConfigParser()
	cp.read(configPath)
				
	networkFile = cp['files']['networkFile']
	etaFile     = cp['files']['etaFile']
	vFile       = cp['files']['vFile']
	networkPath = abspath(join(basePath, "..//Graph//",  networkFile))
	etaPath     = abspath(join(basePath, "..//Inputs//",  etaFile))
	vPath       = abspath(join(basePath, "..//Inputs//",  vFile))

	# Basic inputs
	seed1 = cp['inputs'].getint('seed1')
	T     = cp['inputs'].getint('T')
	N     = cp['inputs'].getint('N')
	prob  = cp['inputs'].getfloat('prob')

	# Service distribution
	vals  = np.arange(12, 25, dtype = 'int64')
	probs = np.ones(13)/13
	sdist = SvcDist(vals, probs)

	# System components: network, arrival patterns, penalty
	svca = readNetwork(networkPath)
	astr = ArrStream(svca, T)
	astr.updateP(prob)

	# Service distributions for Maxwell's bounding system 
	svcDists = readEta(etaPath)
	v        = readV(vPath) 
	
	# Solver settings    
	settings = {}
	for item in cp['settings']:
		settings[item] = eval(cp['settings'][item])
		
	# Displaying progress
	freq = cp['log'].getint('freq')
	if freq < 0: freq = N+1

	# Matt Maxwell's upper bound
	seed(seed1)
	obj = np.zeros(N)
	for i in range(N):
		if (i+1)% freq == 0: print('Iteration %i' % (i+1))
			
		omega = SamplePath(svca, astr, svcDist=sdist, mxwDist=svcDists)
		m     = MMIP2.ModelInstance(svca, astr, omega, v)
		m.solve(settings)
		obj[i] = m.getObjective()

	print('Maxwell Bound: %.3f +/- %.3f' % confInt(obj))

if __name__ == '__main__':
    main()
