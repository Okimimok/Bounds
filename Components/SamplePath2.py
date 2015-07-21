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
            loc = self.calls[t]['loc']
            svc = self.calls[t]['svc']
                
            for j in B[loc]:
                for k in self.svca.bases:
                    busy  = int(ceil(svc + dist[loc][j] + dist[loc][k]))
                    ready = t + busy
                    if ready <= self.T:
                        self.Q[ready][k].append((t, j))

    def __buildQ2(self):
        # Q2[t][j] : Set of dispatch decisions (s, k) for which an ambulance 
        #   dispatched at time s to base k results in amb finishing the call,
        #   but traveling to base j at time t
        self.Q2 = {}
        B       = self.svca.getB()
        dist    = self.svca.getDist()

        for t in range(self.T + 1):
            self.Q2[t] = {}
            for j in self.svca.bases:
                self.Q2[t][j] = []

        for t in self.calls:
            loc = self.calls[t]['loc']
            svc = self.calls[t]['svc']
                
            for j in B[loc]:
                for k in self.svca.bases:
                    svcComp = int(ceil(t + dist[loc][j] + svc))
                    tAtBase = int(ceil(svcComp + dist[loc][k]))
                    #tAtBase = int(ceil(t + dist[loc][j] + svc + dist[loc][k]))
                    for s in range(svcComp, min(tAtBase, self.T+1)):
                        self.Q2[s][k].append((t, j))
                
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

    def __buildQE(self):
        # QE[t][j]: Set of pairs (s, i) s.t. if a redeployment begins from node i
        #   at time s to node j, ambulance would be en route to j at time t
        self.QE = {}
        dist    = self.svca.getDist()

        for t in range(1, self.T+1):
            for j in self.svca.bases:
                self.QE[(t, j)] = []

        for (s, i) in self.QD:
            for j in self.svca.bases:
                done = int(ceil(s+dist[i][j]))
                #for t in range(s+1, min(done, self.T+1)):
                for t in range(s, min(done, self.T+1)):
                    self.QE[(t, j)].append((s, i))

    def __buildQR(self):
        # QR[t][j]: Set of pairs (s, i) s.t. if a redeployment begins from node i
        #   at time s to node j, ambulance would arrive at j by time t
        self.QR = {}
        dist    = self.svca.getDist()

        for (s, i) in self.QD:
            for j in self.svca.bases:
                done = int(ceil(s + dist[i][j]))
                if (done, j) in self.QR:
                    self.QR[(done, j)].append((s, i))
                else:
                    self.QR[(done, j)] = [(s, i)]
    
    def __buildTau(self):
        # idle[t][j][k] = Fix a sample path, and consider an ambulance dispatched 
        #       at time t from base j, and redeployed to base k. Suppose it has
        #       just become idle at base k. Then the number of time periods that
        #       pass before the first call that it can respond to (on that path).
        # Then tau[t][j][k] = idle[t][j][k] - E[idle[t][j][k]]
        B     = self.svca.getB()
        bases = self.svca.bases
        calls = self.calls
        dist  = self.svca.dist
        RP    = self.astr.getRP()
        times = self.callTimes
        C     = self.numCalls
        p     = self.astr.getArrProb()
        T     = self.T

        self.tau = {}
        for t in times:
            self.tau[t] = {}
            i           = calls[t]['loc']
            svc         = calls[t]['svc']
            for j in B[i]:
                self.tau[t][j] = {}
                for k in bases:
                    done  = t + dist[i][j] + svc + dist[i][k]
                    idx   = bisect_left(times, done)
                    expv  = (1 - (1-RP[t][k])**(T-done))/RP[t][k]
                    self.tau[t][j][k] = T - done - expv

                    for s in range(idx, C):
                        if k in B[calls[times[s]]['loc']]:
                            self.tau[t][j][k] = times[s] - done - expv
                            break

    def getCalls(self):
        return self.calls

    def getQ(self):
        try:
            return self.Q
        except:
            self.__buildQ()
            return self.Q

    def getQ2(self):
        try:
            return self.Q2
        except:
            self.__buildQ2()
            return self.Q2
        
    def getQD(self):
        try:
            return self.QD
        except:
            self.__buildQD()
            return self.QD

    def getQE(self):
        try:
            return self.QE
        except:
            self.__buildQE()
            return self.QE

    def getQR(self):
        try:
            return self.QR
        except:
            self.__buildQR()
            return self.QR

    def getTau(self):
        try:
            return self.tau
        except:
            self.__buildTau()
            return self.tau
