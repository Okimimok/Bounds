import numpy as np
from ..Models import MMIP, MCLP
from ..Components.SvcDist import SvcDist

# Reading SvcDist objects from file, and writing them to file

def writeSvcDist(sdist, filePath):
	vals  = sdist.support
	probs = sdist.pmf
	N     = len(vals)

	with open(filePath, 'w') as f:
		f.write('%i\n' % N)
		for i in range(N):
			f.write('%i %.6f\n' % (vals[i], probs[i]))

def readSvcDist(filePath):
	with open(filePath, 'r') as f:
		N     = int(f.readline())
		vals  = np.zeros(N, dtype = 'int64')
		probs = np.zeros(N)
		for i in range(N):
			line     = f.readline().split()
			vals[i]  = int(line[0])
			probs[i] = float(line[1])

	return SvcDist(vals, probs)

def readGradFile(gradPath):
	with open(gradPath, 'r') as f:
		T     = int(f.readline())
		gamma = np.zeros(T+1)
		for t in range(T+1):
			line     = f.readline().split()
			gamma[t] = float(line[1])

	return gamma
