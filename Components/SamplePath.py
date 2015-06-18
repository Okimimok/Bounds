from ..Methods.sample import discreteN
from random import random
from math import ceil
from bisect import bisect_left
import numpy as np

class SamplePath():
    def __init__(self, svcArea, arrStream, svcDist=None, mxwDist=None):
        self.T         = arrStream.T            
        self.A         = svcArea.A
        self.svcArea   = svcArea
        self.arrStream = arrStream
        self.svcDist   = svcDist
        self.mxwDist   = mxwDist
        self.__buildCalls()
        self.callTimes = np.array(sorted(self.calls.keys()))
        self.numCalls  = len(self.callTimes)
        
    def __buildCalls(self):
        # Generate sample path of calls
        self.calls = {}
        P = self.arrStream.getP()
        
        for t in range(self.T + 1):
            # Call pmf at time t
            callLoc = discreteN(P[t])
                
            if callLoc != 'null':
                r = random()
                self.calls[t]            = {}
                self.calls[t]['loc'] = callLoc
                self.calls[t]['rnd'] = r
                                
                if self.svcDist is not None:
                    self.calls[t]['svc'] = self.svcDist.sample(r)

                if self.mxwDist is not None:
                    self.calls[t]['mxw'] = np.zeros(self.A+1, dtype='int64')
                    for a in range(self.A+1):
                        self.calls[t]['mxw'][a] = self.mxwDist[a].sample(r)
                
    def __buildQ(self):
        # Q[t][j] : Set of dispatch-redeploy decisions (s, k), such that
        #         a dispatch from k to time s results in amb becoming free
        #         before time t at node j
        #
        # Used with the perfect information upper bd (perhaps w/ penalties)
        self.Q = {}
        B      = self.svcArea.getB()
        dist   = self.svcArea.getDist()

        for t in range(self.T + 1):
            self.Q[t] = {}
            for j in self.svcArea.bases:
                self.Q[t][j] = []

        for c in self.calls:
            arr = self.calls[c]['loc']
            svc = self.calls[c]['svc']
                
            for j in B[arr]:
                for k in self.svcArea.bases:
                    busy  = int(ceil(svc + dist[arr][j] + dist[arr][k]))
                    ready = c + busy
                    if ready <= self.T:
                        self.Q[ready][k].append((c, j))

    def __buildQM(self):
        # QM[t]: Set of pairs (s, a) s.t. if dispatch made to call s < t
        #       when a ambulances available, service completes before t arrives
        #       (and no sooner!)
        #
        # Used with Matt Maxwell's upper bound for loss systems
        self.QM = {}
        times   = sorted(self.calls.keys())
        last    = times[-1]
        for t in times:
            self.QM[t] = []

        for t in times:
            for a in range(1, self.A+1):
                # Find earliest call time following service completion
                svc    = self.calls[t]['mxw'][a]
                finish = t + svc
                # Don't append if call finishes after last arrival
                if finish <= last:
                    idx  = bisect_left(times, finish)
                    self.QM[times[idx]].append((t, a))
                                
    def getCalls(self):
        return self.calls
        
    def getQ(self):
        try:
            return self.Q
        except:
            self.__buildQ()
            return self.Q
                
    def getQM(self):
        try:
            return self.QM
        except:
            self.__buildQM()
            return self.QM
