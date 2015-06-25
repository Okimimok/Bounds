import numpy as np

# Deterministic in the sense that arrival times are specified, but call locations
#   remain random. (We assume here that they're i.i.d.) Contrary to ArrStream.py, 
#   we require a vector specifying the times at which we want arrivals to happen.

class DetArrStream():
    def __init__(self, svca, T, times):
        self.T         = T
        self.callTimes = times
        self.__svca    = svca
        self.__buildP()
        self.__buildRP()
                                
    def __buildP(self):
        # P[t][i] = Probability of call arrival to node i at time t
        # By default, no arrivals at time zero. Start-up period.
        self.__P = np.zeros((self.T + 1, len(self.__svca.nodes)))
        for t in range(1, self.T + 1):
            if t in self.callTimes:
                for i in self.__svca.nodes:
                    self.__P[t][i] = self.__svca.nodes[i]['prob']

    def __buildRP(self):
        # RP[t][j] = Probability that ambulance at base j can respond to
        #       call arrival at time t
        R = self.__svca.getR()
                
        self.__RP = np.zeros((self.T + 1, len(self.__svca.bases)))
        for t in range(self.T + 1):
            for j in self.__svca.bases:
                self.__RP[t][j] = sum(self.__P[t][i] for i in R[j])


    def getP(self):
        return self.__P

    def getRP(self):
        return self.__RP

    def getCallTimes(self):
        return self.callTimes
                
