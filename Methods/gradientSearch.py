import numpy as np
from ..Classes.SamplePath import SamplePath

# Methods that can be used to perform a gradient search with respect
#	to the penalty parameters gamma (gamma_t, gamma_tj)

def solvePIPs(svcArea, arrStream, svcDist, penalty, N, solveIP,\
				 freq=1, flag=False):
	# Solves N instances of the IP corresponding to different sample 
	#	 paths. Outputs the objective value attained in every problem
	#	 instance, as well as an estimate of the gradient.
	# Takes as input a function handle solveIP, which takes as input:
	# 1) A ServiceArea object
	# 2) An ArrivalStream object
	# 3) A sample path omega
	# 4) A penalty object (containing information about current penalty
	#			 and maybe gradient information and step sizes )
	# Prints progress to console every freq sample paths

	obj   = np.zeros(N)
	gamma = penalty.getGamma()
   
	if gamma.ndim == 1:  
		nabla = np.zeros(arrStream.T + 1)
	else:
		nabla = np.zeros((arrStream.T + 1, len(gamma[0])))
   
	for k in xrange(N):
		if (k + 1) % freq == 0: print '---Path %i' % (k+1)
		 
		omega = SamplePath(svcArea, arrStream, svcDist)

		# Penalized IP, Multiple Coverage, Time multipliers
		obj[k], temp, _ = solveIP(svcArea, arrStream, omega, penalty, flag, grad=True)
															
		nabla += temp/N
	   
	return obj, nabla
   

def lineSearch(svcArea, arrStream, svcDist, penalty, N, solveIP,\
				  flag=False, freq=1):
	# Given an incumbent solution and gradient estimate at that point,
	#	evaluates the objective function value associated with penalty
	#	obtained by moving for various step sizes along the gradient.
	# Displays progress every freq sample paths
						 
	objVals = np.zeros(len(penalty.getStepSizes()))
	 
	for i in xrange(N):
		if (i+1) % freq == 0: print '---Path %i' % (i+1)
			   
		# Generate sample path
		omega = SamplePath(svcArea, arrStream, svcDist)
		
		# Set of multipliers being evaluated
		temp = solveIP(svcArea, arrStream, omega, penalty, flag)
		
		# Update objective estimates
		objVals += temp/N
		
	return objVals
