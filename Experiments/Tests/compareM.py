import sys, time, configparser
import numpy as np
from random import seed
from os.path import abspath, dirname, realpath, join
from ...Methods.network import readNetwork      
from ...Methods.sample import confInt
from ...Methods.dists import readSvcDist
from ...Lower.compliance import readTable
from ...Upper.gradient import fullSearch
from ...Components.ArrStream import ArrStream
from ...Components.CvgPenalty import CvgPenalty
from ...Components.SamplePath import SamplePath
from ...Models import LPIP, PIP, PIP2 

# Like compare.py, but specifically for gradient search for the IP with
#       a Big-M constraint. 

def main():
    basePath   = dirname(realpath(__file__))
    configPath = abspath(join(abspath(join(basePath, "..//")), sys.argv[1]))
    cp         = configparser.ConfigParser()
    cp.read(configPath)
                                
    networkFile = cp['files']['networkFile']
    sdFile      = cp['files']['sdFile']
    outputFile  = cp['files']['outputFile']

    networkPath = abspath(join(abspath(join(basePath, "..//")), networkFile))
    sdPath      = abspath(join(abspath(join(basePath, "..//")), sdFile))
    outputPath  = abspath(join(abspath(join(basePath, "..//")), outputFile))

    # Basic inputs
    seed1 = cp['inputs'].getint('seed1')
    seed2 = cp['inputs'].getint('seed2')
    T     = cp['inputs'].getint('T')
    N     = cp['inputs'].getint('N')
    iters = cp['inputs'].getint('iters')
    probs = eval(cp['inputs']['probs'])
    steps = eval(cp['inputs']['steps'])
    H     = len(probs)
    debug = cp['log'].getboolean('debug')

    # Service distribution
    sdist = readSvcDist(sdPath)

    # System components: network, arrival patterns, penalty
    svca = readNetwork(networkPath)
    astr = ArrStream(svca, T)

    # Penalty Multipliers: One for the Big-M IP, one for its LP relaxation
    penaltyIP = CvgPenalty(np.zeros(T+1))
    penaltyLP = CvgPenalty(np.zeros(T+1))

    # Solver settings    
    settings = {}
    for item in cp['settings']:
        settings[item] = eval(cp['settings'][item])
                
    # Displaying progress
    freqD = cp['log'].getint('freqD')
    freqG = cp['log'].getint('freqG')
    if freqD < 0: freqD = N+1

    # Summary statistics
    ubPI = np.zeros((H,N))
    ubIP = np.zeros((H,N))
    ubLP = np.zeros((H,N))

    start = time.clock()
    for h in range(H):
        penaltyIP.setStepSizes(steps)
        penaltyLP.setStepSizes(steps)
        print('Arrival probability = %.3f' % probs[h])
        astr.updateP(probs[h])

        print('Gradient search for the LP...')
        fullSearch(svca, astr, sdist, penaltyLP, LPIP, settings, N, seed1, iters, freqG, debug)
        gammaLP = penaltyLP.getGamma()

        print('Gradient search for the IP...')
        fullSearch(svca, astr, sdist, penaltyIP, PIP, settings, N, seed1, iters, freqG, debug)
        gammaIP = penaltyIP.getGamma()

        # Computing upper and lower bounds on a separate set of sample paths
        print('Debiasing...')
        seed(seed2)
        for i in range(N):
            if (i+1)% freqD == 0: print('Iteration %i' % (i+1))

            omega = SamplePath(svca, astr, svcDist=sdist)

            # Perfect information relaxation of problem (unpenalized)
            m = PIP2.ModelInstance(svca, astr, omega)
            m.solve(settings)
            ubPI[h][i] = m.getObjective()     
    
            m2 = PIP.ModelInstance(svca, astr, omega, gammaIP)
            m2.solve(settings)
            ubIP[h][i] = m2.getObjective()

            m3 = LPIP.ModelInstance(svca, astr, omega, gammaLP)
            m3.solve(settings)
            ubLP[h][i] = m3.getObjective()

        print('Perfect Info Bound : %.3f +/- %.3f' % confInt(ubPI[h]))
        print('Big M, LP Bound    : %.3f +/- %.3f' % confInt(ubLP[h]))
        print('Big M, IP Bound    : %.3f +/- %.3f' % confInt(ubIP[h]))
        
        rt = time.clock() - start
        print('Search took %.4f seconds' % rt)

        # Writing results to file
        with open(outputPath, 'w') as f:
            f.write('%i 4 %.2f %i\n' % (H, rt, N))
            f.write('PerfectInfo LPMBound IPMBound\n')
            for h in range(H):
                f.write('%.3f\n' % probs[h])
                f.write('PerfectInfo %.3f %.3f\n' % (confInt(ubPI[h])))
                f.write('LPMBound %.3f %.3f\n' % (confInt(ubLP[h])))
                f.write('IPMBound %.3f %.3f\n' % (confInt(ubIP[h])))

if __name__ == '__main__':
    main()
