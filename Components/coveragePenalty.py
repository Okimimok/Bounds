import numpy as np

class coveragePenalty():
    def __init__(self, gamma):
        self.__gamma = gamma
        
        # Intializing gradient value to zero
        # Check if time-varying or time-base-varying multipliers
        if self.__gamma.ndim == 1:
            self.__nabla = np.zeros(len(self.__gamma))
        else:
            self.__nabla = np.zeros((len(self.__gamma), len(self.__gamma[0])))
            
        # Step sizes along gradient to evalute
        self.__stepSizes = [0] 
            
    def setNabla(self, value):
        self.__nabla = value
        
    def setStepSizes(self, newSteps):
        self.__stepSizes = newSteps
        
    def scaleGamma(self, c):
        self.__gamma *= c
        
    def updateGamma(self, delta):
        self.__gamma += delta
        
    def getGamma(self):
        return self.__gamma
        
    def getNabla(self):
        return self.__nabla
        
    def getStepSizes(self):
        return self.__stepSizes
