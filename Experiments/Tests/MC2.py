import sys, time, configparser
import numpy as np 
from random import seed
from os.path import abspath, dirname, realpath, join
from ...Methods.network import readNetwork      
from ...Methods.sample import confInt
from ...Components.ArrStream import ArrStream
from ...Components.SamplePath2 import SamplePath2
from ...Components.SvcDist import SvcDist
from ...Models import PIP2, PIPR
import pdb

# For testing the alterative formulation of the perfect info IP
#   (with separate vars for dispatching and redeployment decisions)

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
    randSeed = cp['inputs'].getint('seed1')
    T        = cp['inputs'].getint('T')
    N        = cp['inputs'].getint('N')
    prob     = cp['inputs'].getfloat('prob')
        
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
    orgObj = np.zeros(N)
    revObj = np.zeros(N)
        
    seed(randSeed)
    start = time.clock()
    for k in range(N):
        if (k+1)% freq == 0: print('Iteration %i' % (k+1))
        
        omega = SamplePath2(svca, astr, sdist)
        p1    = PIP2.ModelInstance(svca, astr, omega)
        p2    = PIPR.ModelInstance(svca, astr, omega)
        p1.solve(settings)
        p2.solve(settings)

        orgObj[k]  = p1.getObjective()
        revObj[k]  = p2.getObjective()

    rt = time.clock() - start
    print('Org. Objective : %.3f +/- %.3f' % confInt(orgObj))
    print('Rev. Objective : %.3f +/- %.3f' % confInt(revObj))
    pdb.set_trace()
                                
if __name__ == '__main__':
    main()
