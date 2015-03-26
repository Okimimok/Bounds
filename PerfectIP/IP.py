from gurobipy import *
import numpy as np

def solve(svcArea, arrStream, omega, flag=False):
	# Unpacking relevant problem instance parameters
	bases = svcArea.bases
	B	  = svcArea.getB()
	RP	  = arrStream.getRP()
	T	  = omega.T
	calls = omega.getCalls()
	Q	  = omega.getQ()
	
	# Number of ambulances in system
	A  = sum([bases[j]['alloc'] for j in bases])
	
	########################################################
	###################### BEGIN MODEL
	########################################################
	m = Model()

	###################### DECISION VARIABLES
	# Respond to call c with ambulance from base i, and redeploy to j?
	x = {}	
	for c in calls:
		x[c] = {}
		for j in B[calls[c]['loc']]:
			x[c][j] = {}
			for k in bases:
				x[c][j][k] = m.addVar(lb=0, ub=1, obj = 1, vtype=GRB.BINARY)

	# At time t, the number of idle ambulances at base i
	y = {}
	for t in xrange(T+1):
		y[t] = {}
		for j in bases:
			y[t][j] = m.addVar(lb=0, ub=A, vtype=GRB.INTEGER)  
	   
	# Objective: To minimize calls not receiving timely response
	m.modelSense = GRB.MAXIMIZE
	m.update()

	######################### CONSTRAINTS
	# At most one response to a call
	for c in calls:
		loc = calls[c]['loc']  
		m.addConstr(quicksum(quicksum(x[c][j][k] for j in B[loc])\
												 for k in bases) <= 1)

	# No dispatch unless ambulance idle
	for c in calls:
		loc = calls[c]['loc']
		for j in B[loc]:
		   m.addConstr(quicksum(x[c][j][k] for k in bases)	<= y[c][j])

	# Flow balance for idle ambulances
	for t in xrange(T+1):
		if t > 0: 
			# Did a call arrive during the last time period?
			if t-1 in calls:
				loc = calls[t-1]['loc']
				for j in bases:
					# Could base i have dispatched an ambulance to the call?
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

	# Optimal solution, determining response sequence
	m.setParam('OutputFlag', flag)
	m.optimize()
	obj    = m.objVal
	policy = {}

	for c in calls:
		policy[c] = [-1, -1]
		for j in B[calls[c]['loc']]:
			for k in bases:
				if x[c][j][k].x > 1e-6:
					policy[c] = [j, k]
					break
				
	return obj, policy
	
