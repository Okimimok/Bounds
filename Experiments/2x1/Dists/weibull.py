from math import exp
from ....Components.SvcDist import SvcDist
from ....Methods.dists import writeSvcDist
from os.path import abspath, dirname, realpath, join
import numpy as np
from scipy.stats import exponweib

# exponweib.pdf and exponweib.cdf take on four parameters
# x     : Point at which to evaluate pdf/cdf
# scale : scale parameter
# a     : Set to 1 (Python reasons)
# c     : shape parameter

def main():
    distFile = "weibull.txt"
    basePath = dirname(realpath(__file__))
    distPath = abspath(join(basePath, distFile))

    # Service distribution: ceil(X), where X ~ Exponential(1/24)
    scale     = 30
    shape     = 5
    maxVal    = 60
    vals      = np.arange(1, maxVal+1)
    probs     = [exponweib.cdf(i+1, a=1, scale=scale, c=shape) - \
                    exponweib.cdf(i, a=1, scale=scale, c=shape) for i in range(maxVal)]
    probs[-1] += 1 - sum(probs)
    sdist     = SvcDist(vals, probs)
    writeSvcDist(sdist, distPath)

if __name__ == '__main__':
    main()
