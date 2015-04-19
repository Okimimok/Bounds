import numpy as np
from ..Models import MECRP
from mmcc import stationaryDist

def buildTable(svcArea, arrStream, svcDist, w):
	# If none specified, wWeights from steady-state dist of M/M/c/c system
	lam = arrStream.getArrProb()
	A   = sum([svcArea.bases[j]['alloc'] for j in svcArea.bases])
	mu  = 1.0/svcDist.mean

	# Solving the resulting coverage problems
	settings = {'OutputFlag' : 0, 'MIPGap' : 0.005}
	p = MECRP.ModelInstance(svcArea, arrStream, A, w)
	p.solve(settings)

	# Obtaining compliance table
	table = {}
	v     = p.getDecisionVars()

	for a in xrange(1, A+1):
		table[a] = []
		for j in svcArea.bases:
			if v['x'][a][j].x > 1e-6:
				table[a].append(j)

	return table 

def writeTable(table, tablePath):
	# Given a compliance table, save it to the location tablePath
	A = len(table)
	with open(tablePath, 'w') as f:
		f.write('%i\n' % A)
		for a in xrange(1, A+1):
			for j in xrange(a):
				f.write('%i ' % table[a][j])
			f.write('\n')

def readTable(tablePath):
	# Given a path to a compliance table policy, a file having the form
	# A
	# b1
	# b1 b2 (etc.)
	# ...reads the file and saves the compliance table in a dictionary
	table = {}
	with open(tablePath, 'r') as f:
		A = int(f.readline())
		for a in xrange(1, A+1):
			table[a] = [int(i) for i in f.readline().split()]

	return table

