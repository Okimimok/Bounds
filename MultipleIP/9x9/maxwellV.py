import numpy as np
from math import exp
from ...Methods import  readFiles
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...Classes.ServiceDistribution import ServiceDistribution
from ...LowerIP import MCLP 

vFile       = "v.txt"
networkFile = "9x9//four.txt"
import os.path
basepath = os.path.dirname(__file__)
vPath    = os.path.join(basepath, vFile)

# Network, arrival patterns
T         = 2
svcArea   = readFiles.readNetworkFile(networkFile)
A         = svcArea.A
arrStream = StationaryArrivalStream(svcArea, T)
v         = {}
settings  = {'OutputFlag' : 0}

for a in xrange(1, A+1):
	p = MCLP.ModelInstance(svcArea, arrStream, a)
	p.solve(settings)
	v[a] = p.getObjective()

with open(vPath, 'w') as f:
	f.write('%i\n' % A)
	for a in xrange(1, A+1):
		f.write('%i %.4f\n' % (a, v[a]))


