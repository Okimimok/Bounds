import sys, time, configparser
import numpy as np
from random import seed
from ...Methods.network import readNetwork      
from os.path import abspath, dirname, realpath, join
from ...Methods.sample import confInt
from ...Upper.maxwell import readEta, readV
from ...Components.SvcDist import SvcDist
from ...Components.ArrStream import ArrStream
from ...Components.SamplePath import SamplePath
from ...Simulation.lowerUpper import simulate
from ...Simulation.dynamicPolicies import daskinRedeploy

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
    seed1 = cp['inputs'].getint('seed1')
    T     = cp['inputs'].getint('T')
    N     = cp['inputs'].getint('N')
    prob  = cp['inputs'].getfloat('prob')

    # Service distribution
    sdist = SvcDist(sdPath=sdPath)

    # Params for MEXCLP-based redeployment policy
    q   = cp['mexclp'].getfloat('q')
    eta = eval(cp['mexclp']['eta'])

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

    # Head-to-head comparison statistics
    moreA = np.zeros(N)
    lessA = np.zeros(N)

    seed(seed1)
    for i in range(N):
        if (i+1)% freq == 0: print('Iteration %i' % (i+1))
                        
        omega = SamplePath(svca, astr, svcDist=sdist, mxwDist=svcDists)
        tmpLB, tmpUB, tmpLU = simulate(svca, omega, lambda state, location, fel, svca:\
                            daskinRedeploy(state, location, fel, svca),\
                            q=q, eta=eta, v=v, debug=debug)

        objUB[i] = tmpUB['obj']
        avUB[i]  = tmpUB['busy']

        objLB[i] = tmpLB['obj']
        utLB[i]  = tmpLB['util']
        ltLB[i]  = tmpLB['late']
        msLB[i]  = tmpLB['miss']

        moreA[i] = tmpLU['more']
        lessA[i] = tmpLU['less']

    print('\nResults:')
    print('Upper Bound    : %.3f +/- %.3f' % confInt(objUB))
    print('Lower Bound    : %.3f +/- %.3f' % confInt(objLB))
    print('\nComparison:')
    print('Plus Arrivals  : %.3f +/- %.3f' % confInt(moreA))
    print('Minus Arrivals : %.3f +/- %.3f' % confInt(lessA))
    print('\nLower Bound Stats')
    print('Utilization    : %.3f +/- %.3f' % confInt(utLB))
    print('Late Calls     : %.3f +/- %.3f' % confInt(ltLB))
    print('Missed Calls   : %.3f +/- %.3f' % confInt(msLB))

if __name__ == '__main__':
    main()
