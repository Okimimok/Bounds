import sys, time, configparser
import numpy as np 
from random import seed
from os.path import abspath, dirname, realpath, join
from ...Methods.network import readNetwork	
from ...Methods.sample import confInt
from ...Methods.nonstat import readProbs
from ...Components.SvcDist import SvcDist
from ...Components.ArrStream import ArrStream
from ...Components.CvgPenalty import CvgPenalty
from ...Upper.gradient import fullSearch, solvePIPs
from ...Models import PIP2

def main():
	basePath   = dirname(realpath(__file__))
	configPath = abspath(join(abspath(join(basePath, "..//")), sys.argv[1]))
	cp         = configparser.ConfigParser()
	cp.read(configPath)

	networkFile  = cp['files']['networkFile']
	sdFile       = cp['files']['sdFile']
	outGammaFile = cp['files']['outGammaFile']
	nonstatFile  = cp['files']['nonstatFile']
	networkPath  = abspath(join(abspath(join(basePath, "..//")), networkFile))
	sdPath       = abspath(join(abspath(join(basePath, "..//")), sdFile))
	outGammaPath = abspath(join(abspath(join(basePath, "..//")), outGammaFile))
	nonstatFile  = cp['files']['nonstatFile']
	
    # Basic inputs
	seed1 = cp['inputs'].getint('seed1')
	seed2 = cp['inputs'].getint('seed2')
	seed3 = cp['inputs'].getint('seed3')
	T     = cp['inputs'].getint('T')
	N     = cp['inputs'].getint('N')
	prob  = cp['inputs'].getfloat('prob')
	iters = cp['inputs'].getint('iters')
	
	# Warm-starting the gradient search?
	try:
		warm = cp['inputs'].getboolean('warm')
	except:
		warm = False
	
	if warm:
		inGammaFile = cp['files']['inGammaFile']
		inGammaPath = abspath(join(abspath(join(basePath, "..//")), inGammaFile))
		penalty     = CvgPenalty(gammaPath=inGammaPath)
		sd          = seed3
	else:
		penalty = CvgPenalty(np.zeros(T+1))
		sd      = seed1

	# Step sizes used for gradient search		
	steps = eval(cp['inputs']['steps'])
	penalty.setStepSizes(steps)

	# Service distribution    
	sdist = SvcDist(sdPath=sdPath)
 
	# System components: network, arrival patterns, penalty
	svca          = readNetwork(networkPath)
	chgPts, probs = readProbs(nonstatPath)
	astr          = NonstatArrStream(svca, T, chgPts, probs)
	astr.updateP(prob)

	# Solver settings    
	settings = {}
	for item in cp['settings']:
		settings[item] = eval(cp['settings'][item])
		
	# Displaying progress
	debug = cp['log'].getboolean('debug')
	freq  = cp['log'].getint('freq')
	if freq < 0: freq = N+1

	start = time.clock()
	fullSearch(svca, astr, sdist, penalty, PIP2, settings, N, sd, iters,\
							 freq=freq, debug=debug)
	rt    = time.clock() - start
	print('Search took %.4f seconds' % rt)
	print('Debiasing...')
	seed(seed2) 
	obj, _ = solvePIPs(svca, astr, sdist, penalty.gamma, PIP2, settings, N, freq=freq)
	print('Done in %.3f seconds' % (time.clock() - rt))
	print('Final upper bound: %.4f +/- %.4f' % confInt(obj))

	# Write resulting multipliers to file
	penalty.writeGamma(outGammaPath)

if __name__ == '__main__':
    main()
