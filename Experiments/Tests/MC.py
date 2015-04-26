import sys
import configparser
import numpy as np 
from random import seed
from os.path import abspath, dirname, realpath, join
from ...Methods.network import readNetwork	
from ...Methods.sample import confInt
from ...Methods.dists import readSvcDist
from ...Components.ArrStream import ArrStream
from ...Components.SamplePath import SamplePath
from ...Models import PIP2

def main():
	basePath   = dirname(realpath(__file__))
	# Jump back a directory from current file. 
	# Command line argument should be of the form ExpType/Config/<ini file>
	configPath = abspath(join(abspath(join(basePath, "..//")), sys.argv[1]))
	cp         = configparser.ConfigParser()
	cp.read(configPath)

	networkFile = cp['files']['networkFile']
	sdFile      = cp['files']['sdFile']
	networkPath = abspath(join(abspath(join(basePath, "..//")), networkFile))
	sdPath      = abspath(join(abspath(join(basePath, "..//")), sdFile))

	# Basic inputs
	randSeed = cp['inputs'].getint('seed1')
	T        = cp['inputs'].getint('T')
	N        = cp['inputs'].getint('N')
	prob     = cp['inputs'].getfloat('prob')
	gamma    = eval(cp['inputs']['gamma'])
	
	# Service distribution
	sdist = readSvcDist(sdPath)
	
	# System components: network, arrival patterns, penalty
	svca = readNetwork(networkPath)
	astr = ArrStream(svca, T)
	astr.updateP(prob)
	
	# Solver settings	 
	settings = {}
	for item in cp['settings']:
		settings[item] = eval(cp['settings'][item])
		
	# Displaying progress
	freq = cp['log'].getint('freq')
	if freq < 0: freq = N+1

	# Monte Carlo Simulation
	ubObj  = np.zeros(N)
	ubUtil = np.zeros(N)
	
	seed(randSeed)
	for k in range(N):
		if (k+1)% freq == 0: print('Iteration %i' % (k+1))
	
		omega	  = SamplePath(svca, astr, sdist)
		p		  = PIP2.ModelInstance(svca, astr, omega, gamma)
		p.solve(settings)
		ubObj[k]  = p.getObjective()
		ubUtil[k] = p.estimateUtilization()	
	
	print ('Objective   : %.3f +/- %.3f' % confInt(ubObj))
	print ('Utilization : %.3f +/- %.3f' % confInt(ubUtil))
	
if __name__ == '__main__':
	main()
