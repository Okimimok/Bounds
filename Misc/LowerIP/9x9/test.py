import numpy as np
from random import seed
from ...Methods.graph import readNetworkFile
from ...Classes.StationaryArrivalStream import StationaryArrivalStream
from ...LowerIP import MCLP, MECRP

networkFile = "15x15//five.txt"

# Network properties
T         = 2
svcArea   = readNetworkFile(networkFile)
arrStream = StationaryArrivalStream(svcArea, T)
arrStream.updateP(0.20)
PN = arrStream.getPN()

# Solving the resulting coverage problems
opt = {}
A   = 5

# Solver settings
settings = {'OutputFlag' : 0, 'MIPGap' : 0.005}

for a in xrange(1, A+1):
	p = MCLP.ModelInstance(svcArea, arrStream, a)
	p.solve(settings)
	
	# Obtaining resulting base locations
	v = p.getDecisionVars()
	opt[a] = {'soln' : [], 'obj' : p.getObjective()}
	x = v['x']
	for j in svcArea.bases:
		if x[j].x > 1e-6:
			opt[a]['soln'].append(j)

w = [1, 1, 1, 1, 1]
p = MECRP.ModelInstance(svcArea, arrStream, A, w)
p.solve(settings)
v = p.getDecisionVars()
x = v['x']
y = v['y']
opt2 = {}

for a in xrange(1, A+1):
	opt2[a] = {'soln' : [], 'obj' : 0.0}
	for j in svcArea.bases:
		if x[a][j].x > 1e-6:
			opt2[a]['soln'].append(j)
	
	for i in svcArea.nodes:
		opt2[a]['obj'] += y[a][i].x*PN[1][i]

for a in opt:
	print sorted(opt[a]['soln']), opt[a]['obj']

print ''

for a in opt2:
	print sorted(opt2[a]['soln']), opt2[a]['obj']
