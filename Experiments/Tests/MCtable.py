import sys
import configparser
import numpy as np
from random import seed
from ...Methods.network import readNetwork	
from os.path import abspath, dirname, realpath, join
from ...Methods.sample import confInt
from ...Methods.dists import readSvcDist
from ...Lower.compliance import readTable
from ...Components.ArrStream import ArrStream
from ...Components.SamplePath import SamplePath
from ...Simulation.lowerAll import simulate as simLB
from ...Simulation.tablePolicies import compliance
#import pdb; pdb.set_trace()

def main():
	basePath    = dirname(realpath(__file__))
	configPath = abspath(join(abspath(join(basePath, "..//")), sys.argv[1]))
	cp         = configparser.ConfigParser()
	cp.read(configPath)

	networkFile = cp['files']['networkFile']
	sdFile      = cp['files']['sdFile']
	tableFile   = cp['files']['tableFile']
	networkPath = abspath(join(abspath(join(basePath, "..//")), networkFile))
	sdPath      = abspath(join(abspath(join(basePath, "..//")), sdFile))
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

	# Reading compliance table
	table = readTable(tablePath)
	obj   = np.zeros(N)
	
	# Displaying progress
	freq  = cp['log'].getint('freq')
	if freq < 0: freq = N+1
		
	# Computing bound
	seed(seed1)
	for i in range(N):
		if (i+1)% freq == 0: print('Iteration %i' % (i+1))
		omega   = SamplePath(svca, astr, svcDist=sdist)
		lbStats = simLB(svca, omega, lambda state, location, fel, svca:\
					compliance(state, location, fel, svca, table))
		obj[i]  = lbStats['obj']

	print('Objective  : %.3f +/- %.3f' % confInt(obj))

if __name__ == '__main__':
	main()