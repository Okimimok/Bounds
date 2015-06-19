from os.path import dirname, realpath, join
from ....Methods.network import writeNetwork, heatmap, bivariateNormalIntegral as bvni  

# Network file location
basePath    = dirname(realpath(__file__))
networkFile = "seven2.txt"
heatFile    = "seven2heat.pdf"
networkPath = join(basePath, networkFile)
heatPath    = join(basePath, heatFile)

# Size of grid, response time threshold
sizeX = 5 
sizeY = 5
Tresp = 9
Tunit = 3.01
grid  = 1 

# Nodes: center of each cell in 5x5 grid
nodes = {}
bases = {}
count = 0
deployed = [2, 6, 8, 12, 16, 18, 22]
for i in range(sizeX):
    for j in range(sizeY):
        nodes[count] = {'loc': (i + 0.5, j + 0.5), 'prob': 0.04}
        bases[count] = {'loc': (i + 0.5, j + 0.5), 'ambs': int(count in deployed)}
        count += 1

writeNetwork(networkPath, nodes, bases, Tunit, Tresp)
heatmap(heatPath, sizeX, sizeY, grid, nodes, bases, minorAx=1, majorAx=3)
