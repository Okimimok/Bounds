import sys, time, configparser
import numpy as np 
from random import seed
from os.path import abspath, dirname, realpath, join
from ...Methods.network import readNetwork	
from ...Methods.sample import confInt
from ...Components.ArrStream import ArrStream
from ...Components.SamplePath import SamplePath
from ...Components.SvcDist import SvcDist
from ...Models import PIP, LPIP

# For studying the integrality gap of the penalized IP with the Big-M constraint

def main():
	basePath   = dirname(realpath(__file__))
	# Jump back a directory from current file. 
	# Command line argument should be of the form ExpType/Config/<ini file>
	configPath = abspath(join(abspath(join(basePath, "..//")), sys.argv[1]))
	cp		   = configparser.ConfigParser()
	cp.read(configPath)

	networkFile = cp['files']['networkFile']
	sdFile		= cp['files']['sdFile']
	networkPath = abspath(join(abspath(join(basePath, "..//")), networkFile))
	sdPath		= abspath(join(abspath(join(basePath, "..//")), sdFile))

	# Basic inputs
	randSeed = cp['inputs'].getint('seed1')
	T		 = cp['inputs'].getint('T')
	N		 = cp['inputs'].getint('N')
	prob	 = cp['inputs'].getfloat('prob')
	LPrelax  = cp['inputs'].getboolean('LPrelax')
	gamma	 = eval(cp['inputs']['gamma'])
	
	# Service distribution
	sdist = SvcDist(sdPath=sdPath)
	
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
	LPobj = np.zeros(N)
	IPobj = np.zeros(N)
	
	seed(randSeed)
	start = time.clock()
	for k in range(N):
		if (k+1)% freq == 0: print('Iteration %i' % (k+1))
	
		omega = SamplePath(svca, astr, sdist)
		'''
		p1 = LPIP.ModelInstance(svca, astr, omega, gamma)
		p2 = PIP.ModelInstance(svca, astr, omega, gamma)

		p1.solve(settings)
		p2.solve(settings)
		LPobj[k] = p1.getObjective()
		IPobj[k] = p2.getObjective()
		'''
		p = LPIP.ModelInstance(svca, astr, omega, gamma)
		p.solve(settings)
		LPobj[k] = p.getObjective()
		p.flipVars()
		p.solve()		
		IPobj[k] = p.getObjective()

	LPavg = np.average(LPobj)
	IPavg = np.average(IPobj)
	gap   = abs((LPavg - IPavg)/IPavg)

	print('LP Relaxation : %.3f' % LPavg)
	print('IP Objective  : %.3f' % IPavg)
	print('Gap           : %.3f' % gap)
				
if __name__ == '__main__':
	main()
