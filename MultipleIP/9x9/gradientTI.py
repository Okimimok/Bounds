import sys
import numpy as np
import time
from random import seed
from ...Methods.graph import readNetworkFile
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.PenaltyMultipliers import PenaltyMultipliers
from ...Classes.SamplePath import SamplePath
from ...MultipleIP import PIP2node, PIP2nodeSearch
from ...Methods.gradientSearch import solvePIPs, lineSearch
networkFile  = "9x9//four.txt"

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
gamma   = np.zeros((T+1, len(svcArea.getNodes())))
penalty = PenaltyMultipliers(gamma)
penalty.setStepSizes([0.5, 1.0, 2.0, 4.0])

##################################################
# Estimate objective value and gradient at current point
gradN     = 20 
lineN     = 8
iters     = 1
randSeed  = 33768

start = time.clock()
for i in xrange(iters):
    print '\nIteration %i' % (i + 1)
    
    # Sampling the gradient    
    print 'Estimating gradient...'
    seed(randSeed)
    obj, nabla = solvePIPs(svcArea, arrStream, svcDist, penalty,\
                             gradN, PIP2node.solve, flag=False, freq=1)
    penalty.setNabla(nabla)
                                                              
    # Determining how far to move along the gradient 
    print 'Line Search...'
    seed(randSeed)                                                          
    vals = lineSearch(svcArea, arrStream, svcDist, penalty,\
                            lineN, PIP2nodeSearch.solve, freq=1) 
    print 'Done!'
    
    # Find best step size
    bestStep = 0
    bestVal  = np.mean(obj[:lineN ])
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
endVals, _ = solvePIPs(svcArea, arrStream, svcDist, penalty,\
                             gradN, PIP2node.solve, flag=False, freq=10)

finish = time.clock()
print 'Final upper bound: %.4f' % np.mean(endVals)
print 'Search took %.4f seconds' % (finish - start)
