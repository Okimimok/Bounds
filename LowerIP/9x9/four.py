import numpy as np
from math import exp
from ...LowerIP.compliance import buildTable
from ...Methods.graph import readNetworkFile
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
import os

networkFile = "9x9//four.txt"
tableFile   = "9x9//compliance.txt"

# Distribution: Uniformly distributed on {12, 13, ..., 24}
vals    = np.arange(12, 25, dtype = 'int64')
probs   = np.ones(13)/13
svcDist = ServiceDistribution(vals, probs)

# Network properties
T         = 2
prob      = 0.12
svcArea   = readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
arrStream.updateP(prob)

buildTable(svcArea, arrStream, svcDist, tableFile)
