import sys
import configparser
import numpy as np
from random import seed
from ....Methods.network import readNetwork	
from os.path import abspath, dirname, realpath, join
from ....Methods.sample import confInt
from ....Lower.compliance import readTable
from ....Components.SvcDist import SvcDist
from ....Components.ArrStream import ArrStream
from ....Components.SamplePath import SamplePath
from ....Simulation.lowerAll import simulate as simLB
from ....Simulation.tablePolicies import compliance
#import pdb; pdb.set_trace()

def main():
	basePath    = dirname(realpath(__file__))
	configPath  = abspath(join(basePath, sys.argv[1]))
	cp          = configparser.ConfigParser()

	cp.read(configPath)
	networkFile = cp['files']['networkFile']
	tableFile   = cp['files']['tableFile']
	networkPath = abspath(join(basePath, "..//Graph//",  networkFile))
	tablePath   = abspath(join(basePath, "..//Inputs//",  tableFile))

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

	# Reading compliance table
	table  = readTable(tablePath)
	obj   = np.zeros(N)
	seed(seed1)
	for i in range(N):
		omega   = SamplePath(svca, astr, svcDist=sdist)
		lbStats = simLB(svca, omega, lambda state, location, fel, svcArea:\
					compliance(simState, location, fel, svcArea, table))
		obj[k]  = lbStats['obj']

	print('Objective  : %.3f +/- %.3f' % confInt(obj))

if __name__ == '__main__':
	main()
