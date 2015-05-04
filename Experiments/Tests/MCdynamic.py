import sys, time, configparser
import numpy as np
from random import seed
from ...Methods.network import readNetwork	
from os.path import abspath, dirname, realpath, join
from ...Methods.sample import confInt
from ...Lower.compliance import readTable
from ...Components.SvcDist import SvcDist
from ...Components.ArrStream import ArrStream
from ...Components.SamplePath import SamplePath
from ...Simulation.lowerAll import simulate as simLB
from ...Simulation.dynamicPolicies import daskinRedeploy
#import pdb; pdb.set_trace()

def main():
	basePath   = dirname(realpath(__file__))
	configPath = abspath(join(abspath(join(basePath, "..//")), sys.argv[1]))
	cp         = configparser.ConfigParser()
	cp.read(configPath)

	networkFile = cp['files']['networkFile']
	sdFile      = cp['files']['sdFile']
	networkPath = abspath(join(abspath(join(basePath, "..//")), networkFile))
	sdPath      = abspath(join(abspath(join(basePath, "..//")), sdFile))

	# Basic inputs
	seed1 = cp['inputs'].getint('seed1')
	T     = cp['inputs'].getint('T')
	N     = cp['inputs'].getint('N')
	prob  = cp['inputs'].getfloat('prob')

	# Service distribution
	sdist = SvcDist(sdPath=sdPath)

	# Params for MEXCLP-based redeployment policy
	q       = cp['mexclp'].getfloat('q')
	etaVals = eval(cp['mexclp']['etaVals'])
	J       = len(etaVals)

	# System components: network, arrival patterns, penalty
	svca = readNetwork(networkPath)
	astr = ArrStream(svca, T)
	astr.updateP(prob)

	# Reading compliance table
	obj   = np.zeros((J, N))
	util  = np.zeros((J, N))
	late  = np.zeros((J, N))
	miss  = np.zeros((J, N))
	
	# Displaying progress
	freq  = cp['log'].getint('freq')
	debug = cp['log'].getboolean('simDebug')
	if freq < 0: freq = N+1
		
	# Computing bound
	seed(seed1)
	start = time.clock()
	for i in range(N):
		if (i+1)% freq == 0: print('Iteration %i' % (i+1))
		omega   = SamplePath(svca, astr, svcDist=sdist)
		for j in range(J):
			lbStats = simLB(svca, omega, lambda state, location, fel, svca:\
						daskinRedeploy(state, location, fel, svca), debug=debug,\
							q=q, eta=etaVals[j]) 

			obj[j][i]  = lbStats['obj']
			util[j][i] = lbStats['util']
			late[j][i] = lbStats['late']
			miss[j][i] = lbStats['miss']


	rt  = time.clock() - start
	for j in range(J):
		print('Distance parameter eta = %.3f' % etaVals[j])
		print('Objective    : %.3f +/- %.3f' % confInt(obj[j]))
		print('Utilization  : %.3f +/- %.3f' % confInt(util[j]))
		print('Late Calls   : %.3f +/- %.3f' % confInt(late[j]))
		print('Missed Calls : %.3f +/- %.3f' % confInt(miss[j]))

	print('Runtime      : %.3f sec (%.3f per iter)' % (rt, rt/(J*N)))

if __name__ == '__main__':
	main()
