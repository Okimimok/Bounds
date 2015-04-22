import numpy as np
from ..Components.samplePath import samplePath
from random import seed

# Methods that can be used to perform a gradient search with respect
#	to the penalty parameters gamma (gamma_t, gamma_tj)


# Faster gradient search, that stores every model created to memory, so that
#	repeated reformulation not necessary
def fastSearch(svcArea, arrStream, svcDist, penalty, IP, settings, N,\
											randSeed, iters, freq=-1, debug=False):
	models = {}
	seed(randSeed)

	# Initialize models, find objective and gradient estimate at starting point
	obj   = 0
	gamma = penalty.getGamma()
	nabla = np.zeros(gamma.shape)
	print 'Initialization...'
	for j in xrange(N):
		omega     = samplePath(svcArea, arrStream, svcDist)
		models[j] = IP.ModelInstance(svcArea, arrStream, omega)
		models[j].updateObjective(gamma)
		models[j].solve(settings)
		obj   += models[j].getObjective()/N
		nabla += models[j].estimateGradient()/N

	for i in xrange(iters):
		if debug: print 'Line search, iteration %i' % (i + 1)
		
		# Line search
		cands    = {}
		bestStep = 0.0
		bestVal  = obj
		bestGrad = np.array(nabla)

		if debug: print '        Step Size 0, Obj. %.4f' % bestVal

		for step in penalty.getStepSizes():
			cands[step] = {'val': 0.0, 'grad': np.zeros(gamma.shape)}
			tmp         = gamma - step*nabla
			for j in xrange(N):
				models[j].updateObjective(tmp)
				models[j].solve(settings)
				cands[step]['val']  += models[j].getObjective()/N
				cands[step]['grad'] += models[j].estimateGradient()/N
			
			if debug:
				 print '        Step Size %.3f, Obj. %.4f' %  (step, cands[step]['val'])
			if cands[step]['val'] < bestVal:
				bestStep = step 
				bestVal  = cands[step]['val']
				bestGrad = cands[step]['grad']

		# If step size is zero, take smaller steps. O/w, update gradient.
		if bestStep == 0:
			penalty.scaleStepSizes(0.5)
		else:
			penalty.updateGamma(-bestStep*nabla)
			nabla = np.array(bestGrad)
			obj   = bestVal

# Gradient search
def fastFullSearch(svcArea, arrStream, svcDist, penalty, IP, settings, N,\
											randSeed, iters, freq=-1, debug=False):
	print 'Initialization...'
	gamma = penalty.getGamma()
	obj   = 0
	nabla = np.zeros(gamma.shape)
	seed(randSeed)

	for j in xrange(N):
		omega  = samplePath(svcArea, arrStream, svcDist)
		m      = IP.ModelInstance(svcArea, arrStream, omega)
		m.updateObjective(gamma)
		m.solve(settings)
		obj   += m.getObjective()/N
		nabla += m.estimateGradient()/N													

	for i in xrange(iters):
		if debug: print 'Iteration %i' % (i+1)
		cands    = {}
		bestStep = 0.0
		bestVal  = obj
		bestGrad = np.array(nabla)
		seed(randSeed)

		for step in penalty.getStepSizes():
			cands[step] = {'val': 0.0, 'grad': np.zeros(gamma.shape)}

		if debug: print '   Step Size 0, Mean Obj. %.4f' % bestVal
		for j in xrange(N):
			# Generate sample path, create skeleton of IP
			omega = samplePath(svcArea, arrStream, svcDist)
			m     = IP.ModelInstance(svcArea, arrStream, omega)

			# Set of multipliers being evaluated
			for step in penalty.getStepSizes():
				m.updateObjective(gamma - step*nabla)
				m.solve(settings)
				cands[step]['val']  += m.getObjective()/N
				cands[step]['grad'] += m.estimateGradient()/N
			
		for step in penalty.getStepSizes():
			if debug: print '   Step Size %.3f, Obj. %.4f' %  (step, cands[step]['val'])
			if cands[step]['val'] < bestVal:
				bestStep = step 
				bestVal  = cands[step]['val']
				bestGrad = cands[step]['grad']

		# If step size is zero, take smaller steps. O/w, update gradient.
		if bestStep == 0:
			penalty.scaleStepSizes(0.5)
		else:
			penalty.updateGamma(-bestStep*nabla)
			nabla = np.array(bestGrad)
			obj   = bestVal

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
			penalty.scaleStepSizes(0.5)
		else:
			penalty.updateGamma(-bestStep*nabla)

def solvePIPs(svcArea, arrStream, svcDist, gamma, IP, settings, N, freq=-1):
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
		prob   = IP.ModelInstance(svcArea, arrStream, omega)
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
