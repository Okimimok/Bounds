import sys
import numpy as np
import time
from random import seed

sys.path.append("Z:\\Redeployment Bounds Project\\Methods\\")
from graph import readNetworkFile

sys.path.append("Z:\\Redeployment Bounds Project\\Classes\\")
from StationaryArrivalStream import StationaryArrivalStream
from PenaltyMultipliers import PenaltyMultipliers

sys.path.append("Z:\\Redeployment Bounds Project\\PenalizedIP")
from search import solvePIPs, lineSearch

networkFile  = "3by3NetworkUniform.txt"

#################################################
# Basic inputs
T       = 1440
svcDist = {}
for i in xrange(12, 25):
    svcDist[i] = 1.0/13

##################################################
# Network, arrival patterns
svcArea   = readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)

##################################################
# Penalty Multipliers
gamma   = np.zeros(T+1)
penalty = PenaltyMultipliers(gamma)
penalty.setStepSizes([0.5, 1.0, 2.0, 4.0, 8.0])

##################################################
# Estimate objective value and gradient at current point
gradPaths = 100
linePaths = 20 
iters     = 8
randSeed  = 33768
DPobj     = 82.2092389004

start = time.clock()
for i in xrange(iters):
    print '\nIteration %i' % (i + 1)
    
    # Sampling the gradient    
    print 'Estimating gradient...'
    seed(randSeed)
    obj, nabla = solvePIPs(svcArea, arrStream, svcDist, penalty, gradPaths)
    penalty.setNabla(nabla)
                                                              
    # Determining how far to move along the gradient 
    print 'Line Search...'
    seed(randSeed)                                                          
    vals = lineSearch(svcArea, arrStream, svcDist, penalty, linePaths)
    print 'Done!'
    
    # Find best step size
    bestStep = 0
    bestVal  = np.mean(obj[:linePaths])
    count    = 0
    
    print 'Step Size 0, Mean Obj. %.4f' % bestVal
    for j in penalty.getStepSizes():
        print 'Step Size %.3f, Mean Obj. %.4f' % (j, vals[count])
        if vals[count] < bestVal:
            bestStep = j
            bestVal  = vals[count]
        count += 1
        
    print 'Best objective value : %.4f \n' % bestVal    
        
    # If step size is zero, take smaller steps. O/w, update gradient.
    if bestStep == 0:
        penalty.scaleGamma(0.5)
    else:
        penalty.updateGamma(-bestStep*nabla)
                         
# Upon termination, sample the objective value at the point selected
print 'Computing final objective value...'   
endVals, _ = solvePIPs(svcArea, arrStream, svcDist, penalty, gradPaths)

finish = time.clock() 
print 'Final upper bound: %.4f' % np.mean(endVals)
print 'Search took %.4f seconds' % (finish - start)
