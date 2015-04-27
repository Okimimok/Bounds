from os.path import abspath, dirname, realpath, join
from ....Methods.network import readNetwork	
from ....Upper.maxwell import buildV, writeV
from ....Components.ArrStream import ArrStream

basePath    = dirname(realpath(__file__))
vFile       = "vTenBall.txt"
networkFile = "tenBall.txt"
vPath       = join(basePath, vFile) 
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))

# Network, arrival patterns
svca = readNetwork(networkPath)
astr = ArrStream(svca, 2)
v    = buildV(svca, astr)
writeV(v, vPath)