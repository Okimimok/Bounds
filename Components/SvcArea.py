import numpy as np

class SvcArea():
    def __init__(self, nodes, bases, Tunit, Tresp, clst=False):
        # Tunit : Time needed (min.) to travel one unit in the network
        # Tresp : Response time threshold
        # clst  : If True, groups bases into clusters (see L and clst)
        self.nodes = nodes
        self.bases = bases
        self.A     = sum([bases[j]['ambs'] for j in bases])
        self.Tunit = Tunit
        self.Tresp = Tresp
        self.probs = [nodes[i]['prob'] for i in nodes]
        self.__buildDist()
        self.__buildB()
        self.__buildNBdist()
        self.__buildR()

        if clst:
            self.__buildL()
            self.__buildClst()
                                
    def __buildDist(self):
        # Build distance matrix between nodes (rows) and bases (columns)
        nodes = self.nodes
        bases = self.bases
        I     = len(nodes)
        J     = len(bases)
        self.dist = np.empty((I, J))
        for i in range(I):
            for j in range(J):
                self.dist[i][j] = self.distance(nodes[i]['loc'], bases[j]['loc'])

    def __buildB(self):
        # B[i] : bases that can respond to call at i within threshold,
        #                      sorted in order of distance from i        
        # BA[i] : same for all bases, not just those within reach of i
        self.__B  = {}
        self.__BA = {}
        if self.Tresp > 0:
            for i in self.nodes:
                temp = sorted([(self.dist[i][j], j) for j in self.bases]) 
                self.__BA[i] = [k[1] for k in temp]
                self.__B[i]  = [k[1] for k in temp if k[0] <= self.Tresp]
        else:
            # Special case, for debugging. Set Tresp to <= 0 only if response
            #   from arriving call's node would be considered timely
            # First element of each dictionary should be the node itself
            for i in self.nodes:
                self.__BA[i] = [i]
                self.__B[i]  = [i]
                temp = sorted([(self.dist[i][j], j) for j in self.bases if j != i]) 
                self.__BA[i] += [k[1] for k in temp]
                                                                 
    def __buildR(self):
        # R[j] = Set of demand nodes to which base j response possible
        self.__R = {}
        for j in self.bases:
            self.__R[j] = [i for i in self.nodes if j in self.__B[i]]

    def __buildNBdist(self):
        # distNBDist[i] = Distance from node i to nearest base
        # The bases in B have already been sorted in order of increasing
        #       distance from i, so just need to get first element of B[i]
        self.__NBdist = [self.dist[i][self.__BA[i][0]] for i in self.nodes]

    def __buildL(self):
        # L[j] = The cluster to which base j belongs (if applicable)
        self.L = np.zeros(len(self.bases), dtype = 'int64')
        for j in self.bases:
            self.L[j] = self.bases[j]['clst']

    def __buildClst(self):
        # clst[l] = The set of bases belonging to cluster l
        self.clst = {}
        for j in self.bases:
            l = self.L[j]
            if l in self.clst:
                self.clst[l].append(j)
            else:
                self.clst[l] = [j]

    def distance(self, x, y):
        # Outputs Manhattan travel time (min.) between two pts in the network 
        return (abs(x[0] - y[0]) + abs(x[1] - y[1]))*self.Tunit

                        
    def getNodes(self):
        return self.nodes
        
    def getBases(self):
        return self.bases
                
    def getMaxDist(self):
        return self.Tresp
                        
    def getDist(self):
        return self.dist

    def getNBdist(self):
        return self.__NBdist
                
    def getB(self):
        return self.__B

    def getBA(self):
        return self.__BA
        
    def getR(self):
        return self.__R   
        
    def getL(self):
        return self.L
        
    def getClst(self):
        return self.clst
