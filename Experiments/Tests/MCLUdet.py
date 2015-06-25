import sys, time, configparser
import numpy as np
from random import seed
from ...Methods.network import readNetwork      
from os.path import abspath, dirname, realpath, join
from ...Methods.sample import confInt
from ...Upper.maxwell import readEta, readV
from ...Components.SvcDist import SvcDist
from ...Components.DetArrStream import DetArrStream
from ...Components.SamplePath import SamplePath
from ...Simulation.lowerUpper import simulate
from ...Simulation.staticPolicy import staticRedeploy
import pdb

def main():
    basePath   = dirname(realpath(__file__))
    configPath = abspath(join(abspath(join(basePath, "..//")), sys.argv[1]))
    cp         = configparser.ConfigParser()
    cp.read(configPath)
                                
    networkFile = cp['files']['networkFile']
    etaFile     = cp['files']['etaFile']
    vFile       = cp['files']['vFile']
    sdFile      = cp['files']['sdFile']
    networkPath = abspath(join(abspath(join(basePath, "..//")), networkFile))
    sdPath      = abspath(join(abspath(join(basePath, "..//")), sdFile))
    vPath       = abspath(join(abspath(join(basePath, "..//")), vFile))
    etaPath     = abspath(join(abspath(join(basePath, "..//")), etaFile))

    # Basic inputs
    seed1     = cp['inputs'].getint('seed1')
    T         = cp['inputs'].getint('T')
    N         = cp['inputs'].getint('N')
    prob      = cp['inputs'].getfloat('prob')
    callTimes = eval(cp['inputs']['callTimes'])

    # Service distribution
    sdist = SvcDist(sdPath=sdPath)

    # System components: network, arrival patterns, penalty
    svca  = readNetwork(networkPath)
    dastr = DetArrStream(svca, T, callTimes)

    # Service distributions for Maxwell's bounding system 
    svcDists = readEta(etaPath)
    v        = readV(vPath) 
        
    # Displaying progress
    freq  = cp['log'].getint('freq')
    debug = cp['log'].getboolean('simDebug')
    if freq < 0: freq = N+1

    # Upper bound statistics
    objUB = np.zeros(N)
    avUB  = np.zeros(N)

    # Lower bound statistics
    objLB = np.zeros(N)
    utLB  = np.zeros(N)
    ltLB  = np.zeros(N)
    msLB  = np.zeros(N)

    seed(seed1)
    for i in range(N):
        if (i+1)% freq == 0: print('Iteration %i' % (i+1))
                        
        omega = SamplePath(svca, dastr, svcDist=sdist, mxwDist=svcDists)
        tmpLB, tmpUB = simulate(svca, omega, lambda state, location, fel, svca:\
                          staticRedeploy(state, location, fel, svca), v=v, debug=debug)

        objUB[i] = tmpUB['obj']
        objLB[i] = tmpLB['obj']

    print('\nResults:')
    print('Upper Bound    : %.3f +/- %.3f' % confInt(objUB))
    print('Lower Bound    : %.3f +/- %.3f' % confInt(objLB))

if __name__ == '__main__':
    main()
