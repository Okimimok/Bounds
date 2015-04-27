from math import exp
from ....Components.SvcDist import SvcDist
from ....Methods.dists import writeSvcDist
from os.path import abspath, dirname, realpath, join
import numpy as np

def main():
	distFile = "exponential.txt"
	basePath = dirname(realpath(__file__))
	distPath = abspath(join(basePath, distFile))

	# Service distribution: ceil(X), where X ~ Exponential(1/24)
	numVals   = 120
	mu        = 24
	vals      = np.arange(1, numVals+1)
	probs     = [exp(-(vals[i]-1)/mu)*(1 - exp(-1/mu)) for i in range(numVals)]
	probs[-1] += 1 - sum(probs)
	sdist     = SvcDist(vals, probs)
	writeSvcDist(sdist, distPath)

if __name__ == '__main__':
	main()
