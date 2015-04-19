import numpy as np
from ..Models import MMIP, MCLP
from ..Components.serviceDistribution import serviceDistribution

def buildEta(svcArea, arrStream, svcDist, filePath, debug=False):
	# Construct dominating service time distributions by solving a sequence
	# 	of MCLPs for various values of r (cdf breakpoints) and a (number of
	#	available ambulances
	maxA  = sum([svcArea.bases[j]['alloc'] for j in svcArea.bases])
	maxR  = -1

	for i in svcArea.nodes:
		for j in svcArea.bases:
			temp = int(svcArea.getDist()[i][j] + svcArea.getNBdist()[i])
			if temp > maxR:
				maxR = temp

	maxR += max(svcDist.support)

	# Obtaining eta values
	eta      = np.zeros((maxR+1, maxA+1))
	settings = {'OutputFlag': 0, 'MIPGap': 0.005}

	for r in xrange(maxR + 1):
		for a in xrange(1, maxA+1):
			if debug: print 'r : %i of %i, a : %i of %i' % (r, maxR, a, maxA)

			p = MMIP.ModelInstance(svcArea, arrStream, svcDist, a, r)
			p.solve(settings)
			eta[r][a] = p.getObjective()
		eta[r][0] = eta[r][1]
	
	return eta

def buildV(svcArea, arrStream, settings=None): 
	# Determine state-dependent rewards for Matt Maxwell's upper bound
	A = svcArea.A
	v = np.zeros(A+1)
	if settings is None:
		settings  = {'OutputFlag' : 0}

	for a in xrange(1, A+1):
		p = MCLP.ModelInstance(svcArea, arrStream, a)
		p.solve(settings)
		v[a] = p.getObjective()

	v[0] = v[1]

	return v

def writeEta(eta, etaPath):
	# Write Maxwell's service time distributions to file 
	with open(etaPath, 'w') as f:
		numR = len(eta)
		numA = len(eta[0])
		f.write('%i %i\n' % (numR, numA))
		fmtString = '%.4f ' * (numA-1) + '%.4f\n'

		for r in xrange(numR):
			f.write(fmtString  % tuple(abs(eta[r])))

def writeV(v, vPath):
	# Write state-dependent rewards to file
	tmp = len(v)
	with open(vPath, 'w') as f:
		f.write('%i\n' % tmp)
		for a in xrange(tmp):
			f.write('%i %.4f\n' % (a, v[a]))

def readEta(etaPath):
	# Read service time distributions from file, returns ServiceDistribution
	# 	objects: one for each possible number of available ambulances
	with open(etaPath, 'r') as f:
		line  = f.readline().split()
		R     = int(line[0]) 
		M     = int(line[1])
		vals  = np.arange(1, R)
		cdfs  = np.empty((M, R))
	
		for r in xrange(R):
			line = f.readline().split()
			for m in xrange(M):
				cdfs[m][r] = float(line[m])

	svcDists = {}
	for m in xrange(M):
		pmf = cdfs[m][1:] - cdfs[m][:R-1]
		svcDists[m] = serviceDistribution(vals, pmf)

	return svcDists

def readV(vPath):
	with open(vPath, 'r') as f:
		tmp = int(f.readline()) 
		v   = np.zeros(tmp)
		for a in xrange(tmp):	
			line = f.readline().split()
			v[a] = float(line[1])

	return v
