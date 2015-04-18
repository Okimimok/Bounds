import numpy as np
from ...Methods import  readFiles
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
from ...MultipleIP import PIP2 
from ...MaxwellIP import getEta

etaFile     = "eta.txt"
networkFile = "9x9//four.txt"
import os.path
basepath = os.path.dirname(__file__)
etaPath  = os.path.join(basepath, etaFile) 

# Distribution: ceil(Y), where Y ~ Exponential(1/24)
T	      = 2 
vals      = np.arange(12, 25, dtype='int64')
probs     = np.ones(13)/13.0
svcDist   = ServiceDistribution(vals, probs)

# Network, arrival patterns
svcArea   = readFiles.readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
getEta.solveIPs(svcArea, arrStream, svcDist, etaPath)
