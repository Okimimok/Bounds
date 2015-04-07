import numpy as np
from random import seed
from ...Methods.graph import readNetworkFile
from ...Methods.sample import confInt
from ...Classes.ServiceDistribution import ServiceDistribution
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...MaxwellIP import getEta 

networkFile = "15x15//eight.txt"
outputFile	= "etaeight.txt"

import os.path
basepath  = os.path.dirname(__file__)
filepath  = os.path.abspath(os.path.join(basepath, outputFile))

#################################################
# Basic inputs
T		= 1440
vals    = np.arange(12, 25, dtype = 'int64')
probs   = np.ones(13)/13.0
svcDist = ServiceDistribution(vals, probs)

##################################################
# Network, arrival patterns
svcArea   = readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
getEta.solveIPs(svcArea, arrStream, svcDist, filepath)
