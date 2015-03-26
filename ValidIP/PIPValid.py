from gurobipy import *
import numpy as np

def solve(svcArea, arrStream, omega, penalty, flag=False, grad=False, warm=False,\
				solver=-1):
	# Set flag = True to display output to console, and to write to
	#	Gurobi log file
	# Set grad = True to output an estimate of the gradient resulting
	#	from the previous problem instances
	# Set warm = True to perform a warmstart. This involves passing in a function
	#	that can be used to output a feasible solution (e.g. a faster IP) that takes
	#	as input svcArea, arrStream, omega, and penalty
	
	nodes = svcArea.getNodes()
	bases = svcArea.getBases()
	B	  = svcArea.getB()
	P	  = arrStream.getP()
	T	  = omega.T
	calls = omega.getCalls()
	Q	  = omega.getQ()
	
	# The penalty
	gamma = penalty.getGamma()
	
	# Number of ambulances in system
	A  = sum([bases[j]['alloc'] for j in bases])
	
	########################################################
	###################### BEGIN MODEL
	########################################################	
	m  = Model()

	###################### DECISION VARIABLES
	# When call c arrives, can an ambulance respond?
	v = {}
	for t in calls:
		loc  = calls[t]['loc']
		v[t] = m.addVar(lb=0, ub=1, obj= -gamma[t], vtype=GRB.BINARY)

	# At time t, can system respond to call arriving at node i?
	w = {}
	for t in xrange(1, T+1):
		w[t] = {}
		for i in nodes:
			w[t][i] = m.addVar(lb=0, ub=1, obj=gamma[t]*P[t][i],\
									   vtype=GRB.BINARY)

	# Respond to call c with ambulance from base j, and redeploy to k?
	x = {}	
	for t in calls:
		x[t] = {}
		for j in B[calls[t]['loc']]:
			x[t][j] = {}
			for k in bases:
				x[t][j][k] = m.addVar(lb=0, ub=1, obj=1, vtype=GRB.BINARY)

	# At time t, the number of idle ambulances at base j
	y = {}
	for t in xrange(T+1):
		y[t] = {}
		for j in bases:
			y[t][j] = m.addVar(lb=0, ub=A, vtype=GRB.INTEGER)	 
			
	
	'''
	# Redundant decision variables
	# At time of call, number of idle ambulances that can respond
	z = {}
	for t in calls:
		loc  = calls[t]['loc']
		z[t] = m.addVar(lb=0, ub=A, vtype=GRB.INTEGER)
	'''
				
	# Objective: To minimize calls not receiving timely response
	m.modelSense = GRB.MAXIMIZE
	m.update()

	######################### CONSTRAINTS
	# At most one response to a call
	for t in calls:
		loc = calls[t]['loc']
		m.addConstr(quicksum(quicksum(x[t][j][k] for j in B[loc])\
												 for k in bases) <= 1)

	# No dispatch unless ambulance idle
	for t in calls:
		loc = calls[t]['loc']
		for j in B[loc]:
		   m.addConstr(quicksum(x[t][j][k] for k in bases) <= y[t][j])

	# Flow balance for idle ambulances
	for t in xrange(T+1):
		if t > 0: 
			# Did a call arrive during the last time period?
			if (t-1) in calls:
				loc = calls[t-1]['loc']
				for j in bases:
					# Could base j have dispatched an ambulance to the call?
					if j in B[loc]:
						m.addConstr(y[t][j] == y[t-1][j] \
							+ quicksum([x[s][k][j] for (s,k) in Q[t][j]])\
							- quicksum([x[t-1][j][k] for k in bases]))
					else:
						m.addConstr(y[t][j] == y[t-1][j] \
							+ quicksum([x[s][k][j] for (s,k) in Q[t][j]]))
			else:
				for j in bases:
					m.addConstr(y[t][j] == y[t-1][j] \
						+ quicksum([x[s][k][j] for (s,k) in Q[t][j]]))
		else:
			for j in bases:
				m.addConstr(y[t][j] == bases[j]['alloc'])

	# Determining values for w-variables
	for t in xrange(1, T+1):
		for i in nodes:
			m.addConstr(w[t][i] <= quicksum(y[t][j] for j in B[i]))

	# Constraints for v-variables
	for t in calls:
		loc = calls[t]['loc']
		m.addConstr(A*v[t] >= quicksum(y[t][j] for j in B[loc]))
		
	################################
	### Valid Inequalities
	################################
		
	# Linking v-variables and w-varaibles
	for t in calls:
		loc = calls[t]['loc']
		m.addConstr(v[t] == w[t][loc])
		
	# v_t = 1 if dispatch made
	for t in calls:
		loc = calls[t]['loc']
		m.addConstr(v[t] >= quicksum(quicksum(x[t][j][k] \
								for j in B[loc]) for k in bases))
									
	# Constraints on v-variables whenever calls don't arrive
	for t in calls:
		if t > 1 and t-1 not in calls:   
			loc = calls[t]['loc']
			m.addConstr(v[t] >= w[t-1][loc])
	
	'''														
	# Constraints on v-variables whenever calls don't arrive
	for t in calls:
		if t > 1:
			if t-1 not in calls:   
				loc = calls[t]['loc']
				m.addConstr(v[t] >= w[t-1][loc])
			else:
				loc = calls[t-1]['loc']
				m.addConstr(v[t] >= v[t-1] \
									- quicksum(quicksum(x[t-1][j][k] \
									for j in B[loc]) for k in bases))
	
	# Monotonicity in w-variables (bad!)
	R = svcArea.getR()
	for t in xrange(2, T+1):
		if t-1 in calls:
			loc = calls[t-1]['loc']
			for i in nodes:
				m.addConstr(w[t][i] >= w[t-1][i]\
								- quicksum(quicksum(x[t-1][j][k]\
									for k in bases) for j in B[loc]\
									if i in R[j]))
		else:
			for i in nodes:
				m.addConstr(w[t][i] >= w[t-1][i])				 
	'''									  
		   
	

	'''
	# Redundant constraints: z-variables
	# In the style of cover inequalities for facility location
	for t in calls:
		loc = calls[t]['loc']
		m.addConstr(z[t] == quicksum(y[t][j] for j in B[loc]))
		
	for t in calls:
		loc = calls[t]['loc']
		m.addConstr(A*v[t] >= z[t])
	'''   
	
	m.update()
	
	############################
	# Branch priority
	############################
	for t in calls:
		v[t].setAttr('BranchPriority', 5)							  
		
	############################ 
	# Warm start 
	############################
	if warm:
		# Obtain feasible solution
		_, _, feas = solver(svcArea, arrStream, omega, penalty)
		
		# Use feasible solution to set initial values for IP
		for t in calls:
			for j in B[calls[t]['loc']] :
				for k in bases:
					x[t][j][k].setAttr('Start', feas['x'][t][j][k])

		for t in xrange(1,T+1):
			for j in bases:
				y[t][j].setAttr('Start', feas['y'][t][j])

		# Now for the v- and w- variables...
		for t in calls:
			if sum([feas['y'][t][j]	for j in B[calls[t]['loc']]]) > 1e-4:
				v[t].setAttr('Start', 1)

		for t in xrange(1, T+1):
			for i in nodes:
				w[t][i].setAttr('Start', min(1, sum([feas['y'][t][j] for j in B[i]])))

	m.update()
	
	# Optimal solution
	m.setParam('OutputFlag', flag)
	m.setParam('MIPGap', 0.01)
	m.setParam('TimeLimit', 600)
	#m.setParam('Method', 2)   
	#m.setParam('Sifting', 0)
	m.optimize()
	obj		  = m.objVal

	# Gradient of objective w.r.t. Lagrange multipliers
	if grad:
		nabla = np.zeros(T+1)
		
		for t in xrange(1, T+1):
			nabla[t] = sum([P[t][i]*w[t][i].x for i in nodes])
			if t in calls:
				loc = calls[t]['loc']
				nabla[t] -= v[t].x
	
		return obj, nabla, m.runTime
	else:
		return obj, m.runTime
