from gurobipy import Model, GRB, LinExpr 

# Matt Maxwell's upper bound, adapted for loss systems. Computing this bound
# 	for a given sample path entails solving an integer program (to "optimize"
#	the system's response to incoming calls, provided the sample path known
#	at the beginning of the horizon). Decisions made under the optimal 
#	nonanticipative policy a feasible solution to this IP.

class ModelInstance:
	def __init__(self, svcArea, arrStream, omega, v):	
		self.A     = svcArea.A
		self.calls = omega.calls
		self.times = sorted(self.calls.keys())
		self.QM    = omega.getQM()
		self.v     = v
		self.formulate()
		
	def formulate(self):
		self.m = Model()

		###################### DECISION VARIABLES
		# Dispatch to call t when a ambulances available/ 
		x = {}
		for t in self.calls:
			x[t] = {}
			for a in range(1, self.A+1):
				x[t][a] = self.m.addVar(lb=0, ub=1, obj=self.v[a])

		# Number of idle ambulances when call t arrives
		y = {}
		for t in self.calls:
			y[t] = self.m.addVar(lb=0, ub=self.A, vtype=GRB.INTEGER)

		self.m.update()

		######################### CONSTRAINTS
		# At most one dispatch 
		for t in self.times:
			expr = LinExpr()
			for a in range(1, self.A+1):
				expr.add(x[t][a], 1)
			self.m.addConstr(expr <= 1)

		# Linking x- and y- variables
		for t in self.times:
			expr = LinExpr()
			for a in range(1, self.A+1):
				expr.add(x[t][a], a)
			self.m.addConstr(expr <= y[t])

		# Flow balance
		for i in range(len(self.times)):
			if i == 0:
				self.m.addConstr(y[self.times[0]] == self.A)
			else:
				expr = LinExpr(1, y[self.times[i-1]])
				for a in range(1, self.A+1):
					expr.add(x[self.times[i-1]][a], -1)
				for (s, a) in self.QM[self.times[i]]:
					expr.add(x[s][a], 1)
				self.m.addConstr(expr == y[self.times[i]])
												
		# Dictionary containing model decision variables
		self.v = {'x' : x, 'y' : y}
		
	def solve(self, settings={}):	
		# Given a fully-formulated model, solves the IP, and returns the model 
		#   object associated with the resulting optimal solution.
		# Settings is a dictionary whose keys are model parameters (e.g., MIPGap,
		#	OutputFlag), and whose values, well, duh.
	
		for key in settings:
			if key.lower() == 'outputflag':
				self.m.setParam(key, settings[key])
				break

		for key in settings:
			self.m.setParam(key, settings[key])

		self.m.modelSense = GRB.MAXIMIZE
		self.m.optimize()
		self.m.fixed()

	def getModel(self):
		return self.m

	def getDecisionVars(self):
		return self.v

	def getObjective(self):
		return self.m.objVal
