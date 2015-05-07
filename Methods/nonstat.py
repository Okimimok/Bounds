import numpy as np

def readProbs(probPath):
	with open(probPath, 'r') as f:
		# Comment line
		f.readline()
		# Number of changepoints, number of nodes
		line  = f.readline().split()
		C     = int(line[0])
		N     = int(line[1])
		probs = np.zeros((C, N))
		
		# Comment line
		f.readline()	
		# Changepoint times
		line   = f.readline().split()
		chgPts = np.array([int(entry) for entry in line], dtype='int64')
		
		# Comment line
		f.readline()
		# Populate probability matrix
		for i in range(N):
			line        = f.readline().split()
			probs[:, i] = [float(entry) for entry in line]
			
		return chgPts, probs
	
def writeProbs(probs, chgPts, probPath):
	C, N = probs.shape
	with open(probPath, 'w') as f:
		f.write('#NumChangepoints NumNodes\n')
		f.write('%i %i\n' % (C, N))

		f.write('#ChangeTimes\n')
		for c in range(C):
			f.write('%i ' % chgPts[c])
		f.write('\n')
		
		f.write('#ArrivalProbs\n')
		for i in range(N):
			for c in range(C):
				f.write('%.5f ' % probs[c][i])
			f.write('\n')
