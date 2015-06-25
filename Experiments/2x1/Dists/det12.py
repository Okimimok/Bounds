from ....Components.SvcDist import SvcDist
from ....Methods.dists import writeSvcDist
from os.path import abspath, dirname, realpath, join
import numpy as np

def main():
    distFile = "det12.txt"
    basePath = dirname(realpath(__file__))
    distPath = abspath(join(basePath, distFile))

    # Service distribution: DiscreteUniform(12, 24)
    vals  = [12] 
    probs = [1.0]
    sdist = SvcDist(vals, probs)
    writeSvcDist(sdist, distPath)

if __name__ == '__main__':
    main()
        
