import sys
import configparser
import numpy as np
from random import seed
from os.path import abspath, dirname, realpath, join
from ...Methods.network import readNetwork	
from ...Methods.sample import confInt
from ...Methods.dists import readSvcDist
from ...Lower.compliance import readTable
from ...Upper.maxwell import readEta, readV
from ...Components.ArrStream import ArrStream
from ...Components.SamplePath import SamplePath
from ...Simulation.lowerAll import simulate as simLB
from ...Simulation.tablePolicies import compliance
from ...Models import MMIP2

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
	networkPath = abspath(join(abspath(join(basePath, "..//")), networkFile))
	sdPath      = abspath(join(abspath(join(basePath, "..//")), sdFile))
	vPath       = abspath(join(abspath(join(basePath, "..//")), vFile))
	etaPath     = abspath(join(abspath(join(basePath, "..//")), etaFile))
	tablePath   = abspath(join(abspath(join(basePath, "..//")), tableFile))

	# Basic inputs
	seed1 = cp['inputs'].getint('seed1')
	T     = cp['inputs'].getint('T')
	N     = cp['inputs'].getint('N')
	prob  = cp['inputs'].getfloat('prob')

	# Service distribution
	sdist = readSvcDist(sdPath)

	# System components: network, arrival patterns, penalty
	svca = readNetwork(networkPath)
	astr = ArrStream(svca, T)
	astr.updateP(prob)

	# Service distributions for Maxwell's bounding system 
	svcDists = readEta(etaPath)
	v        = readV(vPath) 

	# Compliance table	
	table = readTable(tablePath)	
	
	# Solver settings    
	settings = {}
	for item in cp['settings']:
		settings[item] = eval(cp['settings'][item])
		
	# Displaying progress
	freq = cp['log'].getint('freq')
	if freq < 0: freq = N+1

	# Matt Maxwell's upper bound
	seed(seed1)
	objUB = np.zeros(N)
	objLB = np.zeros(N)
	
	for i in range(N):
		if (i+1)% freq == 0: print('Iteration %i' % (i+1))
			
		omega    = SamplePath(svca, astr, svcDist=sdist, mxwDist=svcDists)
		m        = MMIP2.ModelInstance(svca, astr, omega, v)
		m.solve(settings)
		objUB[i] = m.getObjective()
		lbStats  = simLB(svca, omega, lambda state, location, fel, svcea:\
						compliance(state, location, fel, svca, table))
		objLB[i] = lbStats['obj']
		

	print('Maxwell Bound: %.3f +/- %.3f' % confInt(objUB))
	print('Table Bound  : %.3f +/- %.3f' % confInt(objLB))

if __name__ == '__main__':
    main()