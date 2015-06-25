from ..Methods.sample import discreteN
from random import random
from math import ceil
from bisect import bisect_left
import numpy as np

# Like SamplePath.py, but built for a variant of the perfect information (and penalized?)
#   integer program in which dispatching and redeployment decisions are decoupled.
# A dictionary like QM (used in Matt Maxwell's upper bound for loss systems) has not
#   been implemented yet. (Do this later if upper bound is promising?)

class SamplePath2():
    def __init__(self, svca, astr, sdist):
        self.T         = astr.T            
        self.A         = svca.A
        self.svca      = svca
        self.astr      = astr
        self.sdist     = sdist
        self.__buildCalls()
        self.callTimes = np.array(sorted(self.calls.keys()))
        self.numCalls  = len(self.callTimes)
        
    def __buildCalls(self):
        # Generate sample path of calls
        self.calls = {}
        P = self.astr.getP()
        
        for t in range(self.T + 1):
            # Call pmf at time t
            callLoc = discreteN(P[t])
                
            if callLoc != 'null':
                r = random()
                self.calls[t]        = {}
                self.calls[t]['loc'] = callLoc
                self.calls[t]['rnd'] = r
                self.calls[t]['svc'] = self.sdist.sample(r)

    def __buildQ(self):
        # Q[t][j] : Set of dispatch-redeploy decisions (s, k), such that
        #         a dispatch from k to time s results in amb becoming free
        #         before time t at node j
        #
        # Used with the perfect information upper bd (perhaps w/ penalties)
        self.Q = {}
        B      = self.svca.getB()
        dist   = self.svca.getDist()

        for t in range(self.T + 1):
            self.Q[t] = {}
            for j in self.svca.bases:
                self.Q[t][j] = []

        for t in self.calls:
            arr = self.calls[t]['loc']
            svc = self.calls[t]['svc']
                
            for j in B[arr]:
                for k in self.svca.bases:
                    busy  = int(ceil(svc + dist[arr][j] + dist[arr][k]))
                    ready = t + busy
                    if ready <= self.T:
                        self.Q[ready][k].append((t, j))
                
    def __buildQD(self):
        # QD[t][i] : Set of dispatch decisions (s, j), such that
        #         a dispatch from j to time s results in amb becoming free
        #         at node i at time t
        self.QD = {}
        B       = self.svca.getB()
        dist    = self.svca.getDist()

        for t in self.calls:
            i   = self.calls[t]['loc']
            svc = self.calls[t]['svc']

            for j in B[i]:
                done = int(ceil(t + dist[i][j] + svc))
                if (done, i) in self.QD:
                    self.QD[(done, i)].append((t, j))
                else:
                    self.QD[(done, i)] = [(t, j)]

    def __buildQR(self):
        # QR[t][j]: Set of pairs (s, i) s.t. if a redeployment begins from node i
        #   at time s to node j, ambulance would arrive at j by time t
        self.QR = {}
        B       = self.svca.getB()
        dist    = self.svca.getDist()

        for (s, i) in self.QD:
            for j in self.svca.bases:
                done = int(ceil(s + dist[i][j]))
                if (done, j) in self.QR:
                    self.QR[(done, j)].append((s, i))
                else:
                    self.QR[(done, j)] = [(s, i)]
                                
    def getCalls(self):
        return self.calls

    def getQ(self):
        try:
            return self.Q
        except:
            self.__buildQ()
            return self.Q
        
    def getQR(self):
        try:
            return self.QR
        except:
            self.__buildQR()
            return self.QR

    def getQD(self):
        try:
            return self.QD
        except:
            self.__buildQD()
            return self.QD
