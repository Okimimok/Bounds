import numpy as np
from ..Components.samplePath import samplePath
from random import seed

# Methods that can be used to perform a gradient search with respect
#	to the penalty parameters gamma (gamma_t, gamma_tj)

# Gradient search
def fullSearch(svcArea, arrStream, svcDist, penalty, IP, settings, N,\
											randSeed, iters, freq=-1, debug=False):
	for i in xrange(iters):
		if debug: print 'Iteration %i\n    Estimating gradient...' % (i + 1)
		gamma = penalty.getGamma()
		seed(randSeed)
		obj, nabla = solvePIPs(svcArea, arrStream, svcDist, gamma, IP, settings, N, freq)
		penalty.setNabla(nabla) 
		
		if debug: print '    Line Search...'

		seed(randSeed)															
		vals = lineSearch(svcArea, arrStream, svcDist, penalty, IP, settings, N, freq) 
		bestStep = 0
		bestVal  = np.mean(obj[:N])
		count	 = 0
			
		if debug: print '        Step Size 0, Mean Obj. %.4f' % bestVal
		for j in penalty.getStepSizes():
			if debug: print '        Step Size %.3f, Mean Obj. %.4f' % (j, vals[count])
			if vals[count] < bestVal:
				bestStep = j
				bestVal  = vals[count]
			count += 1

		# If step size is zero, take smaller steps. O/w, update gradient.
		if bestStep == 0:
			penalty.scaleGamma(0.5)
		else:
			penalty.updateGamma(-bestStep*nabla)

def solvePIPs(svcArea, arrStream, svcDist, gamma, IPmodel, settings, N, freq=-1):
	# Solves N instances of the IP corresponding to different sample 
	#	 paths. Outputs the objective value attained in every problem
	#	 instance, as well as an estimate of the gradient.
	# IPmodel is a (handle to a) class, instances of which correspond
	#     to instances of the model of interest. 
	# Prints progress to console every freq sample paths

	obj   = np.zeros(N)
	nabla = np.zeros(gamma.shape)
   
	for i in xrange(N):
		if freq > 0 and (i + 1) % freq == 0: print '---Path %i' % (i+1)
		
		# Generate sample path, solve IP, get gradient estimate
		omega  = samplePath(svcArea, arrStream, svcDist)
		prob   = IPmodel.ModelInstance(svcArea, arrStream, omega)
		prob.updateObjective(gamma)
		prob.solve(settings)
		obj[i] = prob.getObjective()
		nabla += prob.estimateGradient()/N													
	   
	return obj, nabla

def lineSearch(svcArea, arrStream, svcDist, penalty, IPmodel, settings, N, freq=-1):
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
		if freq > 0 and (i+1) % freq == 0: print '---Path %i' % (i+1)
			   
		# Generate sample path, create skeleton of IP
		omega = samplePath(svcArea, arrStream, svcDist)
		prob  = IPmodel.ModelInstance(svcArea, arrStream, omega)

		# Set of multipliers being evaluated
		for j in xrange(numSteps):
			prob.updateObjective(gamma - steps[j]*nabla)
			prob.solve(settings)
			objVals[j][i] = prob.getObjective()
			
	result = np.array([np.average(stepval) for stepval in objVals])

	return result 
