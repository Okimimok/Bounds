from os.path import abspath, dirname, realpath, join
from ...Upper.maxwell import buildEta, writeEta
from ...Methods.network import readNetwork	
from ...Methods.dists import readSvcDist
from ...Components.ArrStream import ArrStream

def main():
	basePath    = dirname(realpath(__file__))
	networkFile = input("Network file  : ")
	sdFile      = input("Svc Dist file : ")
	etaFile     = input("Eta file      : ")
	networkPath = abspath(join(abspath(join(basePath, "..//")), networkFile))
	sdPath      = abspath(join(abspath(join(basePath, "..//")), sdFile))
	etaPath     = abspath(join(abspath(join(basePath, "..//")), etaFile))

	# Read service distribution
	sdist = readSvcDist(sdPath)

	# Network, arrival patterns (assuming stationary arrivals)
	svca = readNetwork(networkPath)
	astr = ArrStream(svca, 2)
	eta  = buildEta(svca, astr, sdist, etaPath, debug=True)
	writeEta(eta, etaPath)

if __name__ == '__main__':
	main()
