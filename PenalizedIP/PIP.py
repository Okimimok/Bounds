from gurobipy import * 
import numpy as np

# Perfect information problem with one-step look-ahead penalty. Involves
#	 a big-M constraint. Don't use for problems involving more than 2 or 3 
#	 ambulances. Warm start not implemented yet (and probably won't be).

def solve(svcArea, arrStream, omega, penalty, flag=False, grad=False):
	# Unpacking relevant problem instance parameters
	bases = svcArea.bases
	nodes = svcArea.nodes
	B	  = svcArea.getB()
	P     = arrStream.getP()
	RP	  = arrStream.getRP()
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
	m = Model()

	###################### DECISION VARIABLES
	# When call c arrives, can an ambulance respond?
	v = {}
	for c in calls:
		loc  = calls[c]['loc']
		v[c] = m.addVar(lb=0, ub=1, obj= -gamma[c], vtype=GRB.BINARY)

	# At time t, can system respond to call arriving at node i?
	w = {}
	for t in xrange(1, T+1):
		w[t] = {}
		for i in nodes:
			w[t][i] = m.addVar(lb=0, ub=1, obj=gamma[t]*P[t][i],\
									   vtype=GRB.BINARY)

	# Respond to call c with ambulance from base j, and redeploy to k?
	x = {}	
	for c in calls:
		x[c] = {}
		for j in B[calls[c]['loc']]:
			x[c][j] = {}
			for k in bases:
				x[c][j][k] = m.addVar(lb=0, ub=1, obj=1, vtype=GRB.BINARY)

	# At time t, the number of idle ambulances at base j
	y = {}
	if gamma.ndim == 1:
		for t in xrange(T+1):
			y[t] = {}
			
			for j in bases:
				if t in calls and j in B[calls[t]['loc']]:
					y[t][j] = m.addVar(lb=0, ub=A, vtype=GRB.INTEGER,\
							obj = gamma[t]*(RP[t][j]-1))
				else:
					y[t][j] = m.addVar(lb=0, ub=A, vtype=GRB.INTEGER,\
							obj = gamma[t]*RP[t][j])
	else:
		for t in xrange(T+1):
			y[t] = {}
			
			for j in bases:
				if t in calls and j in B[calls[t]['loc']]:
					y[t][j] = m.addVar(lb=0, ub=A, vtype=GRB.INTEGER,\
							obj = gamma[t][j]*(RP[t][j]-1))
				else:
					y[t][j] = m.addVar(lb=0, ub=A, vtype=GRB.INTEGER,\
							obj = gamma[t][j]*RP[t][j])
				
	# Objective: To minimize calls not receiving timely response
	m.setParam('OutputFlag', flag)
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
		   m.addConstr(quicksum(x[c][j][k] for k in bases) <= y[c][j])

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
	for c in calls:
		loc = calls[c]['loc']
		m.addConstr(A*v[c] >= quicksum(y[c][j] for j in B[loc]))

 
	# Optimal solution, determining response sequence
	m.setParam('MIPGap', 0.01)
	m.setParam('TimeLimit', 600)
	m.optimize()
	obj		  = m.objVal

	if grad:
		# Gradient of objective w.r.t. Lagrange multipliers
		if gamma.ndim == 1:
			gradSample = np.zeros(T+1)
			for t in xrange(T+1):
				for j in bases:
					gradSample[t] += y[t][j].x*RP[t][j]
					if t in calls and j in B[calls[t]['loc']]:
						gradSample[t] -= y[t][j].x
		else:
			gradSample = np.zeros((T+1, len(bases)))
			for t in xrange(T+1):
				for j in bases:
					gradSample[t][j] = y[t][j].x*RP[t][j]
					if t in calls and j in B[calls[t]['loc']]:
						gradSample[t][j] -= y[t][j].x
		return obj, gradSample, m.runTime
	else:
		return obj, m.runTime
