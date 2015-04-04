import numpy as np
from ..Classes.SamplePath import SamplePath

# Methods that can be used to perform a gradient search with respect
#	to the penalty parameters gamma (gamma_t, gamma_tj)

def solvePIPs(svcArea, arrStream, svcDist, gamma, IPmodel, settings, N, freq = 1):
	# Solves N instances of the IP corresponding to different sample 
	#	 paths. Outputs the objective value attained in every problem
	#	 instance, as well as an estimate of the gradient.
	# IPmodel is a (handle to a) class, instances of which correspond
	#     to instances of the model of interest. 
	# Prints progress to console every freq sample paths

	obj   = np.zeros(N)
	nabla = np.zeros(gamma.shape)
   
	for i in xrange(N):
		if (i + 1) % freq == 0: print '---Path %i' % (i+1)
		
		# Generate sample path
		omega = SamplePath(svcArea, arrStream, svcDist)

		# Create instance of integer program, solve, get gradient estimate
		prob = IPmodel.ModelInstance(svcArea, arrStream, omega)
		prob.updateObjective(gamma)
		prob.solve(settings)
		obj[i] = prob.getObjective()
		nabla += prob.estimateGradient()/N													
	   
	return obj, nabla

def lineSearch(svcArea, arrStream, svcDist, penalty, IPmodel, settings, N, freq=1):
	# Given an incumbent solution and gradient estimate at that point,
	#	evaluates the objective function value associated with penalty
	#	obtained by moving for various step sizes along the gradient.
	# Displays progress every freq sample paths
						 
	steps    = penalty.getStepSizes()
	numSteps = len(steps)
	objVals  = np.zeros((numSteps, N))
	gamma    = penalty.getGamma()
	nabla    = penalty.getNabla()
	 
	for i in xrange(N):
		if (i+1) % freq == 0: print '---Path %i' % (i+1)
			   
		# Generate sample path, create skeleton of IP
		omega = SamplePath(svcArea, arrStream, svcDist)
		prob  = IPmodel.ModelInstance(svcArea, arrStream, omega)

		# Set of multipliers being evaluated
		for j in xrange(numSteps):
			prob.updateObjective(gamma - steps[j]*nabla)
			prob.solve(settings)
			objVals[j][i] = prob.getObjective()
			
	result = np.array([np.average(stepval) for stepval in objVals])

	return result 
