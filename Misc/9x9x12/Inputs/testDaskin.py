import numpy as np
from ....Methods.network import readNetwork	
from ....Lower.compliance import buildDaskinTable, writeTable
from ....Components.arrivalStream import arrivalStream
from ....Components.serviceDistribution import serviceDistribution
from ....Models import MEXCLP
from os.path import abspath, dirname, realpath, join

basePath    = dirname(realpath(__file__))
networkFile = "twelve.txt"
tableFile   = "daskinTable.txt"
tablePath   = abspath(join(basePath, tableFile))
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))

# Distribution: Uniformly distributed on {12, 13, ..., 24}
vals    = np.arange(12, 25, dtype = 'int64')
probs   = np.ones(13)/13
svcDist = serviceDistribution(vals, probs)

# Network properties
svcArea   = readNetwork(networkPath)
arrStream = arrivalStream(svcArea, 2)
prob      = 0.12
mu        = svcDist.mean
arrStream.updateP(prob)

settings = {'OutputFlag': 0, 'MIPGap': 0.005}
for A in xrange(1, svcArea.A+1):
	print 'Fleet size %i' % A
	q = prob*mu/(svcArea.A)
	w = [q**(i-1) for i in xrange(A+1)]
	p = MEXCLP.ModelInstance(svcArea, arrStream, A, q, w)
	p.solve(settings)
	v = p.getDecisionVars()
	for j in svcArea.bases:
		if v['x'][j].x > 1e-6:
			print 'Base %i : %i ambulances' % (j, int(v['x'][j].x))
