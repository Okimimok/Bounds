import numpy as np

class CvgPenalty():
    # Can be initialized in one of two ways:
    #   1) A numpy array
    #   2) A .txt file (time-location multipliers not yet supported)
    # In either case, determines initial penalty multipliers.
    def __init__(self, gamma=None, gammaPath=None):
        if gamma is not None:
            self.gamma = gamma
        elif gammaPath is not None:
            with open(gammaPath, 'r') as f:
                T          = int(f.readline())
                self.gamma = np.zeros(T+1)
                for t in range(T+1):
                    line          = f.readline().split()
                    self.gamma[t] = float(line[1])
                
        # Intializing gradient value to zero
        # Check if time-varying or time-base-varying multipliers
        if self.gamma.ndim == 1:
            self.nabla = np.zeros(len(self.gamma))
        else:
            self.nabla = np.zeros((len(self.gamma), len(self.gamma[0])))
                        
        # Step sizes along gradient to evalute
        self.__stepSizes = np.array([0])
                        
    def setNabla(self, value):
        self.nabla = value
                
    def setStepSizes(self, newSteps):
        self.__stepSizes = np.array(newSteps)
                
    def scaleGamma(self, c):
        self.gamma *= c
                
    def updateGamma(self, delta):
        self.gamma += delta
                
    def getGamma(self):
        return self.gamma
                
    def getNabla(self):
        return self.nabla
                
    def getStepSizes(self):
        return self.__stepSizes

    def scaleStepSizes(self, c):
        self.__stepSizes *= c

    def writeGamma(self, outPath):
        # Write current penalty to file (e.g., post gradient search)
        T = len(self.gamma) - 1
        with open(outPath, 'w') as f:
            f.write('%i\n' % T)
            for t in range(T+1):
                f.write('%i %.6f\n' % (t, self.gamma[t]))
