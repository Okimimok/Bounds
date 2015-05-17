from ....Components.SvcDist import SvcDist
from ....Methods.dists import writeSvcDist
from os.path import abspath, dirname, realpath, join
import numpy as np

def main():
	distFile = "rTail.txt"
	basePath = dirname(realpath(__file__))
	distPath = abspath(join(basePath, distFile))

	vals  = np.arange(15, 31, dtype = 'int64')
	wts   = [1, 2, 2, 3, 3, 4, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1]
	W     = sum(wts)
	probs = np.array([i/W for i in wts])
	sdist = SvcDist(vals, probs)
	writeSvcDist(sdist, distPath)

if __name__ == '__main__':
	main()
	
