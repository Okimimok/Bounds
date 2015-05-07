from os.path import dirname, realpath, join, abspath
from ....Methods.nonstat import readProbs, writeProbs
import numpy as np

basePath    = dirname(realpath(__file__))
probFile    = "sixTwoPeaks.txt"
networkFile = "Graph/sixTwoPeaks.txt"
probPath    = join(basePath, probFile)
networkPath = abspath(join(abspath(join(basePath, "..//")), networkFile))

with open(networkPath, 'r') as f:
	# Comment line
	f.readline()
	# Node data
	line = f.readline().split()
	N    = int(line[0])
	p    = np.zeros(N)

	# Demand alternates between two halves of graph. Left half: x <= 7.5
	#	Right half (x > 7.5). left = 1 if node on left half
	left = np.zeros(N)
	

	# Comment line
	f.readline()
	for i in range(N):
		line    = f.readline().split()
		xVal    = float(line[1])
		p[i]    = float(line[3])
		left[i] = (xVal <= 7.5)

# Changepoints, multipliers for left half and right half
chgPts = np.array([1, 361, 721, 1081])
C      = len(chgPts)
lfMult = np.array([2, 0.5, 2, 0.5])
rtMult = np.array([0.5, 2, 0.5, 2])
probs  = np.zeros((C, N))

# Filling phase-probability matrix
for c in range(C):
	for i in range(N):
		probs[c][i] = p[i]*(lfMult[c]*left[i] + rtMult[c]*(1-left[i]))

# Writing to file
writeProbs(probs, chgPts, probPath)
probs, chgPts = readProbs(probPath)
