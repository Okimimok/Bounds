import numpy as np
import MECRP
import os
from ..Methods.MMCC import stationaryDist

def buildTable(svcArea, arrStream, svcDist, w = None):
	# If none specified, wWeights from steady-state dist of M/M/c/c system
	lam = arrStream.getArrProb()
	A   = sum([svcArea.bases[j]['alloc'] for j in svcArea.bases])
	mu  = 1.0/svcDist.mean

	if w is None:
		w  = stationaryDist(lam, mu, A)

	# Solving the resulting coverage problems
	settings = {'OutputFlag' : 0, 'MIPGap' : 0.005}
	p = MECRP.ModelInstance(svcArea, arrStream, A, w)
	p.solve(settings)

	# Obtaining compliance table
	opt = {}
	v   = p.getDecisionVars()

	for a in xrange(1, A+1):
		opt[a] = []
		for j in svcArea.bases:
			if v['x'][a][j].x > 1e-6:
				opt[a].append(j)

	return opt


def writeTable(tableFile):
	basepath  = os.path.dirname(__file__)
	tablePath = os.path.join(basepath, tableFile) 

	# Writing table to file
	with open(tablePath, 'w') as f:
		f.write('%i\n' % A)
		for a in xrange(1, A+1):
			for j in xrange(a):
				f.write('%i ' % opt[a][j])
			f.write('\n')

def readTable(tableFile):
	basepath  = os.path.dirname(__file__)
	tablePath = os.path.join(basepath, tableFile) 

	table = {}
	with open(tablePath, 'r') as f:
		A = int(f.readline())
		for a in xrange(1, A+1):
			table[a] = [int(i) for i in f.readline().split()]

	return table
