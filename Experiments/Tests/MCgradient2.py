import sys, time, configparser
import numpy as np 
from random import seed
from os.path import abspath, dirname, realpath, join
from ...Methods.network import readNetwork      
from ...Methods.sample import confInt
from ...Components.SvcDist import SvcDist
from ...Components.ArrStream import ArrStream
from ...Components.CvgPenalty import CvgPenalty
from ...Upper.gradient2 import fullSearch, solvePIPs
from ...Models import PIP2, PIP3, PIP4, PIP5, PIPR

# Test code. Gradient search on "revised" PIPs where definition of coverage 
#   is modified to include ambulances en route to a base. 

def main():
    basePath   = dirname(realpath(__file__))
    configPath = abspath(join(abspath(join(basePath, "..//")), sys.argv[1]))
    cp         = configparser.ConfigParser()
    cp.read(configPath)

    networkFile  = cp['files']['networkFile']
    sdFile       = cp['files']['sdFile']

    try:
        outGammaFile  = cp['files']['outGammaFile']
        outGammaPath  = abspath(join(abspath(join(basePath, "..//")), outGammaFile))
        printGradient = True
    except:
        printGradient = False

    networkPath  = abspath(join(abspath(join(basePath, "..//")), networkFile))
    sdPath       = abspath(join(abspath(join(basePath, "..//")), sdFile))
        
    # Basic inputs
    seed1 = cp['inputs'].getint('seed1')
    seed2 = cp['inputs'].getint('seed2')
    T     = cp['inputs'].getint('T')
    N     = cp['inputs'].getint('N')
    prob  = cp['inputs'].getfloat('prob')
    iters = cp['inputs'].getint('iters')
    name  = cp['inputs']['name']

    # Step sizes used for gradient search           
    penalty = CvgPenalty(np.zeros(T+1))
    steps   = eval(cp['inputs']['steps'])
    penalty.setStepSizes(steps)

    # Service distribution    
    sdist = SvcDist(sdPath=sdPath)
 
    # System components: network, arrival patterns, penalty
    svca = readNetwork(networkPath)
    astr = ArrStream(svca, T)
    astr.updateP(prob)

    # Solver settings    
    stngs = {}
    for item in cp['settings']:
        stngs[item] = eval(cp['settings'][item])
                
    # Displaying progress
    debug = cp['log'].getboolean('debug')
    freq  = cp['log'].getint('freq')
    if freq < 0: freq = N+1

    start = time.clock()
    if name == 'two':
        fullSearch(svca, astr, sdist, penalty, PIP2, stngs, N, seed1, iters, freq, debug)
    elif name == 'three':
        fullSearch(svca, astr, sdist, penalty, PIP3, stngs, N, seed1, iters, freq, debug)
    elif name == 'four':
        fullSearch(svca, astr, sdist, penalty, PIP4, stngs, N, seed1, iters, freq, debug)
    elif name == 'five':
        fullSearch(svca, astr, sdist, penalty, PIP5, stngs, N, seed1, iters, freq, debug)
    elif name == 'revised':
        fullSearch(svca, astr, sdist, penalty, PIPR, stngs, N, seed1, iters, freq, debug)

    rt    = time.clock() - start
    print('Search took %.4f seconds' % rt)
    print('Debiasing...')
    seed(seed2) 
    if name == 'two':
        obj, _ = solvePIPs(svca, astr, sdist, penalty.gamma, PIP2, stngs, N, freq=freq)
    elif name == 'three':
        obj, _ = solvePIPs(svca, astr, sdist, penalty.gamma, PIP3, stngs, N, freq=freq)
    elif name == 'four':
        obj, _ = solvePIPs(svca, astr, sdist, penalty.gamma, PIP4, stngs, N, freq=freq)
    elif name == 'five':
        obj, _ = solvePIPs(svca, astr, sdist, penalty.gamma, PIP5, stngs, N, freq=freq)
    elif name == 'revised':
        obj, _ = solvePIPs(svca, astr, sdist, penalty.gamma, PIPR, stngs, N, freq=freq)

    print('Done in %.3f seconds' % (time.clock() - rt))
    print('Final upper bound: %.4f +/- %.4f' % confInt(obj))

    # Write resulting penalty multipliers to file
    if printGradient:
       penalty.writeGamma(outGammaPath)

if __name__ == '__main__':
    main()

'''
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

'''
