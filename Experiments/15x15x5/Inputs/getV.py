import numpy as np
from os import pardir
from os.path import abspath, dirname, realpath, join
from ....Upper.maxwell import buildV, writeV
from ....Methods.network import readNetwork	
from ....Components.arrivalStream import arrivalStream

basePath    = dirname(realpath(__file__))
vFile       = "v.txt"
networkFile = "five.txt"
vPath       = join(basePath, vFile) 
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))

# Network, arrival patterns
svcArea   = readNetwork(networkPath)
arrStream = arrivalStream(svcArea, 2)
v         = buildV(svcArea, arrStream)
writeV(v, vPath)
