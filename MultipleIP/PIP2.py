from gurobipy import *
import numpy as np

# Similar to PIP, but multi-counts coverage when computing penalties.
#	Variant of code allowing for quick evaluation (and gradient information)
#	from a single penalty.

def solve(svcArea, arrStream, omega, penalty, flag=False, grad=False, soln=False):
	# Unpacking relevant problem instance parameters
	bases = svcArea.bases
	B	  = svcArea.getB()
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
	# Respond to call c with ambulance from base i, and redeploy to j?
	x = {}	
	for c in calls:
		x[c] = {}
		for j in sorted(B[calls[c]['loc']]):
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
	
	
				
	######################### SOLUTION	   
	# Optimal solution, determining response sequence
	m.optimize()
	obj = m.objVal
		
	# Gradient of objective w.r.t. Lagrange multipliers
	if grad:
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
		if soln:
			return obj, gradSample, m.runTime, solution(x,y)
		else:
			return obj, gradSample, m.runTime
	else:
		if soln:
			return obj, m.runTime, solution(x, y)
		else:
			return obj, m.runTime


def solution(x, y):
	# Given a feasible solution (x, y) to the integer program, returns a dictionary
	#	containing both.
	feas = {'x': {}, 'y' : {}}
	for t in y:
		feas['y'][t] = {}
		if t in x:
			feas['x'][t] = {}
			for j in x[t]:
				feas['x'][t][j] = {}
				for k in x[t][j]:
					feas['x'][t][j][k] = x[t][j][k].x

		for j in y[t]:
			feas['y'][t][j] = y[t][j].x
	

	return feas
