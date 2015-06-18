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
from ...Simulation.upperMaxwell import simulate

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

    # Matt Maxwell's upper bound
    seed(seed1)
    obj   = np.zeros(N)
    start = time.clock()
    for i in range(N):
        if (i+1)% freq == 0: print('Iteration %i' % (i+1))
                        
        omega  = SamplePath(svca, astr, svcDist=sdist, mxwDist=svcDists)
        simSts = simulate(svcDists, omega, svca.A, v, debug)
        obj[i] = simSts['obj']
        rt     = time.clock() - start

    print('Maxwell Bound: %.3f +/- %.3f' % confInt(obj))
    print('Runtime      : %.3f sec (%.3f per iter)' % (rt, rt/N))

if __name__ == '__main__':
    main()
