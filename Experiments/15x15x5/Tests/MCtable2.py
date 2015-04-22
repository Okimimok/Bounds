import numpy as np 
from random import seed
from ....Methods.network import readNetwork	
from os.path import abspath, dirname, realpath, join
from ....Methods.sample import confInt
from ....Lower.compliance import readTable
from ....Components.serviceDistribution import serviceDistribution
from ....Components.arrivalStream import arrivalStream
from ....Components.samplePath import samplePath
from ....Models import MMIP2
from ....Simulation.lowerAll import simulate as simLB
from ....Simulation.tablePolicies import compliance

basePath    = dirname(realpath(__file__))
networkFile = "five.txt"
tableFile   = "daskinTable.txt"
networkPath = abspath(join(basePath, "..//Graph//",  networkFile))
tablePath   = abspath(join(basePath, "..//Inputs//",  tableFile))

T	    = 1440
vals    = np.arange(12, 25, dtype = 'int64')
probs   = np.ones(13)/13
svcDist = serviceDistribution(vals, probs)

# Network, arrival patterns
svcArea   = readNetwork(networkPath)
A         = svcArea.A
arrStream = arrivalStream(svcArea, T)
arrStream.updateP(0.08)

# Reading compliance table
table  = readTable(tablePath)

# Generating sample paths
N     = 50
seed1 = 12345
obj   = np.zeros(N)
call  = np.zeros(N)
late  = np.zeros(N)
miss  = np.zeros(N)
seed(seed1)
for k in xrange(N):
	omega   = samplePath(svcArea, arrStream, svcDist)
	stats   = simLB(svcArea, omega, lambda simState, location, fel, svcArea:\
				compliance(simState, location, fel, svcArea, table))
	call[k] = len(omega.getCalls())
	obj[k]  = stats['obj']
	late[k] = stats['late']
	miss[k] = stats['miss']

print 'Objective    : %.3f +/- %.3f' % confInt(obj)
print 'Total Calls  : %.3f +/- %.3f' % confInt(call)
print 'Late Calls   : %.3f +/- %.3f' % confInt(late)
print 'Missed Calls : %.3f +/- %.3f' % confInt(miss)
