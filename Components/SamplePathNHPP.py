from ..Methods.sample import discreteN
from random import random, expovariate as exprnd
from math import ceil
from bisect import bisect_left, bisect_right
import numpy as np

# No need for an arrStream object, everything generated in-house.
#   Used to generate a NHPP where rate function is piecewise 
#   linear (and possibly cyclic)
#   
# Inputs:
# 1) svca -- A service area object
# 2) Vectors rates, times. Suppose 
#      rates = [r1, r2, ..., rn]
#      times = [t1, t2, ..., tn]
#
#    Rate r1 between 0 to t1, r2 between t1 and t2.
#    Length of cycle = tn (possibly T)
#
# 3) T -- Horizon length
# 4) svcDist, mxwDist -- As in SamplePath.py
#
# Note: Functions Q and QM not implemented yet. Later, if necessary.

class SamplePathNHPP():
    def __init__(self, svca, rates, times, T, svcDist=None, mxwDist=None):
        self.T       = T  
        self.A       = svca.A
        self.svca    = svca
        self.rates   = rates
        self.times   = times
        self.svcDist = svcDist
        self.mxwDist = mxwDist

        # Some relevant inputs
        self.maxRate = max(rates)
        self.cycleLn = times[-1] 
        self.probs   = svca.probs 
        
        # Determine arrival times for NHPP
        self.__getArrivals()
        self.__buildCalls()

    def __getArrivals(self):
        # Simulate PP(maxRate) process on [0, T]
        #   Probably more efficient to do this via inversion  (See HW7, ORIE6500, F12)
        #   Rewrite if this code ends up being used a lot.
        t   = 0
        tmp = []
        while t < self.T:
            t  += exprnd(self.maxRate)
            tmp.append(t)

        # Thin arrivals using the rate function
        self.callTimes = []
        self.numCalls  = 0
        for t in tmp:
            r = random()
            if r < self.__getRate(t)/self.maxRate:
                self.callTimes.append(t)
                self.numCalls += 1

    def __getRate(self, t):
        # Given a time t, obtain rate associated with that time
        t   = t % self.cycleLn
        idx = bisect_right(self.times, t)
        return self.rates[idx]
        
    def __buildCalls(self):
        # Determine call locations and service times 
        self.calls = {}
        for i in range(self.numCalls):
            # Randomly generate call location, uniform governing service time
            callLoc = discreteN(self.probs)
            r       = random()

            # Build call i's dictionary
            self.calls[i] = {'arr': self.callTimes[i], 'rnd': r, 'loc': callLoc}
                                
            if self.svcDist is not None:
                self.calls[i]['svc'] = self.svcDist.sample(r)

            if self.mxwDist is not None:
                self.calls[i]['mxw'] = np.zeros(self.A+1, dtype='int64')
                for a in range(self.A+1):
                    self.calls[i]['mxw'][a] = self.mxwDist[a].sample(r)
                
    def getCalls(self):
        return self.calls
