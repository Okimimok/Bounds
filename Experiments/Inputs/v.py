from os.path import abspath, dirname, realpath, join
from ...Methods.network import readNetwork	
from ...Upper.maxwell import buildV, writeV
from ...Components.ArrStream import ArrStream

def main():
	basePath    = dirname(realpath(__file__))
	networkFile = input("Network file: ")
	vFile       = input("V-file      : ")
	networkPath = abspath(join(abspath(join(basePath, "..//")), networkFile))
	vPath       = abspath(join(abspath(join(basePath, "..//")), vFile))
	
	# Solve the appropriate IPs
	svca = readNetwork(networkPath)
	astr = ArrStream(svca, 2)
	v    = buildV(svca, astr)
	writeV(v, vPath)
	
if __name__ == '__main__':
	main()