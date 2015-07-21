import sys, time, configparser
import numpy as np 
from random import seed
from os.path import abspath, dirname, realpath, join
from ...Methods.network import readNetwork      
from ...Methods.sample import confInt
from ...Components.ArrStream import ArrStream
from ...Components.CvgPenalty import CvgPenalty
from ...Components.SamplePath import SamplePath
from ...Components.SamplePath2 import SamplePath2
from ...Components.SvcDist import SvcDist
from ...Models import PIP2, PIP3, PIP4, PIP5, PIPR
import pdb
import warnings

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
    name     = cp['inputs']['name']
    
    try:
        snapshot = cp['log'].getboolean('snapshot')
    except:
        snapshot = False

    try:
        profile = cp['log'].getboolean('profile')
    except:
        profile = False
        
    # Service distribution
    sdist = SvcDist(sdPath=sdPath)
        
    # System components: network, arrival patterns
    svca = readNetwork(networkPath)
    astr = ArrStream(svca, T)
    astr.updateP(prob)
        
    # Penalty multipliers!
    try:
        inGammaFile = cp['files']['inGammaFile']
        inGammaPath = abspath(join(abspath(join(basePath, "..//")), inGammaFile))
        cvgp        = CvgPenalty(gammaPath = inGammaPath)
        gamma       = cvgp.gamma
    except:
        gamma = eval(cp['inputs']['gamma'])

    # Solver settings        
    settings = {}
    for item in cp['settings']:
        settings[item] = eval(cp['settings'][item])
                
    # Displaying progress
    freq = cp['log'].getint('freq')
    if freq < 0: freq = N+1

    # Monte Carlo Simulation 
    obj   = np.zeros(N)
    disps = np.zeros(N)
    seed(randSeed)
    start = time.clock()

    if profile:
        A       = svca.A
        disps   = np.zeros(N)
        avgIn   = np.zeros((A+1, N))
        avgOut  = np.zeros((A+1, N))
        avgProp = np.zeros((A+1, N)) 

    for k in range(N):
        if (k+1)% freq == 0: print('Iteration %i' % (k+1))
        
        omega = SamplePath2(svca, astr, sdist)
        if name == 'two':
            p = PIP2.ModelInstance(svca, astr, omega, gamma)
        elif name == 'three':
            p = PIP3.ModelInstance(svca, astr, omega, gamma)
        elif name == 'four':
            p = PIP4.ModelInstance(svca, astr, omega, gamma)
        elif name == 'five':
            p = PIP5.ModelInstance(svca, astr, omega, gamma)
        elif name == 'revised':
            p = PIPR.ModelInstance(svca, astr, omega, gamma)

        p.updateObjective(gamma)
        p.solve(settings)
        obj[k]   = p.getObjective()
        disps[k] = p.countDispatches()

        if profile:
            ap = p.ambProfile()
            for a in range(A+1):
                avgProp[a][k] = np.nanmean(ap[a]['prop'])
                if a > 0:
                    # Suppress warnings caused by averaging NaN arrays
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", category=RuntimeWarning)
                        avgIn[a][k]  = np.nanmean(ap[a]['in'])
                        avgOut[a][k] = np.nanmean(ap[a]['out'])

    
    rt = time.clock() - start
    print('\nObjective  : %.3f +/- %.3f' % confInt(obj))
    print('Dispatches : %.3f +/- %.3f' % confInt(disps))
    
    if snapshot:
        print("\nSystem Snapshot:\n")
        p.systemSnapshot()

    if profile:
        print("\nState Profile\n")
        for a in range(svca.A+1):
            print('State %i (%.3f of time)' % (a, np.average(avgProp[a])))
            if a > 0:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=RuntimeWarning)
                    print('Within range: %.3f' % np.nanmean(avgIn[a]))
                    print('Out of range: %.3f\n' % np.nanmean(avgOut[a]))
            else:
                print('')

if __name__ == '__main__':
    main()
