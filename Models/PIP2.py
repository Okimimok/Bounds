from gurobipy import Model, GRB, LinExpr 
import numpy as np

class ModelInstance:
	# Similar to PIP, but multi-counts coverage when computing penalties.
	#	Variant of code allowing for quick evaluation (and gradient information)
	#	from a single penalty.
	# If multipliers specified from the outset, coefficents for y-variables
	#	set without having to call updateObjective.
	def __init__(self, svca, astr, omega, gamma=None):
		self.nodes = svca.nodes
		self.bases = svca.bases
		self.dist  = svca.getDist()
		self.B     = svca.getB()
		self.A     = sum([self.bases[j]['ambs'] for j in self.bases])
		self.RP    = astr.getRP()
		self.T     = astr.T
		self.calls = omega.getCalls()
		self.Q     = omega.getQ()

		# Number of degrees of freedom in the penalty. Defaults to zero
		#	(0 = no penalty, 1 = time based, 2 = time-location based)
		if gamma is not None:
			self.dof = gamma.ndim
		else:
			self.dof = 0	

		# Create model object and dictionary of decision vars
		self.formulate(gamma)

	def formulate(self, gamma):
		# Formulates the integer program, by defining the appropriate decision
		#	variables and constraints. Objective function values for the x-vars
		#	are set, but those for the y-vars are kept to zero. 
		#
		# Returns the resulting model, as well as a dictionary containing 
		#	decision variables.
		self.m = Model()

		###################### DECISION VARIABLES
		# Respond to call c with ambulance from base i, and redeploy to j?
		x = {}	
		for c in self.calls:
			x[c] = {}
			for j in sorted(self.B[self.calls[c]['loc']]):
				x[c][j] = {}
				for k in self.bases:
					x[c][j][k] = self.m.addVar(lb=0, ub=1, obj=1, vtype=GRB.BINARY)

		# At time t, the number of idle ambulances at base j
		y = {}
		if self.dof == 1:
			for t in range(self.T+1):
				y[t] = {}
				for j in self.bases:
					if t in self.calls and j in self.B[self.calls[t]['loc']]:
						y[t][j] = self.m.addVar(lb=0, ub=self.A, vtype=GRB.INTEGER,\
									obj = gamma[t]*(self.RP[t][j]-1))
					else:
						y[t][j] = self.m.addVar(lb=0, ub=self.A, vtype=GRB.INTEGER,\
									obj = gamma[t]*self.RP[t][j])
		elif self.dof == 2:
			for t in range(self.T+1):
				y[t] = {}
				for j in self.bases:
					if t in self.calls and j in self.B[self.calls[t]['loc']]:
						y[t][j] = self.m.addVar(lb=0, ub=self.A, vtype=GRB.INTEGER,\
									obj = gamma[t][j]*(self.RP[t][j]-1))
					else:
						y[t][j] = self.m.addVar(lb=0, ub=self.A, vtype=GRB.INTEGER,\
									obj = gamma[t][j]*self.RP[t][j])
		else:
			for t in range(self.T+1):
				y[t] = {}
				for j in self.bases:
					y[t][j] = self.m.addVar(lb=0, ub=self.A, vtype=GRB.INTEGER)
			
		self.m.update()

		######################### CONSTRAINTS
		# IP constraints, all melded into one for loop. Probably difficult
		#	to read, and so longform included at end of file.
		callTimes = sorted(self.calls.keys())
		N		  = len(callTimes)

		cnt = 0
		for t in range(self.T):
			if cnt < N and t == callTimes[cnt]:
				cnt  += 1 
				loc   = self.calls[t]['loc']
				expr1 = LinExpr()
				for j in self.bases:
					expr3 = LinExpr(1, y[t][j])
					for (s, l) in self.Q[t+1][j]:
						expr3.add(x[s][l][j], 1)

					if j in self.B[loc]:
						expr2 = LinExpr()
						for k in self.bases:
							expr1.add(x[t][j][k], 1)
							expr2.add(x[t][j][k], 1)
							expr3.add(x[t][j][k], -1)
						self.m.addConstr(expr2 <= y[t][j])

					self.m.addConstr(expr3 == y[t+1][j])

				self.m.addConstr(expr1 <= 1)	
					
			elif t > 0:
				for j in self.bases: 
					expr3 = LinExpr(1, y[t][j])
					for (s, k) in self.Q[t+1][j]:
						expr3.add(x[s][k][j], 1)
					self.m.addConstr(expr3 == y[t+1][j])
			else:
				for j in self.bases:
					self.m.addConstr(y[1][j] == self.bases[j]['ambs'])

		# Boundary condition: call arrives in final time period
		if self.T == callTimes[-1]:
			loc   = self.calls[self.T]['loc']
			expr1 = LinExpr()
			for j in self.B[loc]:
				expr2 = LinExpr()
				for k in self.bases:
					expr1.add(x[self.T][j][k], 1)
					expr2.add(x[self.T][j][k], 1)
				self.m.addConstr(expr2 <= y[self.T][j])

			self.m.addConstr(expr1 <= 1)
		# Dictionary containing model decision variables
		self.v = {'x' : x, 'y' : y}

	def updateObjective(self, gamma):
		# Takes as input:
		# m		: An already formulated PIP instance (w/ dec vars and constraints)
		# v		: A dictionary containing its decision varaibles
		# gamma : Vector of penalty weights 
		#
		# Updates the objective function coefficients for the y-variables
		y		 = self.v['y']
		self.dof = gamma.ndim

		if self.dof == 1:
			for t in range(self.T+1):
				for j in self.bases:
					if t in self.calls and j in self.B[self.calls[t]['loc']]:
						y[t][j].setAttr("obj", gamma[t]*(self.RP[t][j]-1))
					else:
						y[t][j].setAttr("obj", gamma[t]*self.RP[t][j])
						
		else:
			for t in range(self.T+1):
				for j in self.bases:
					if t in self.calls and j in self.B[self.calls[t]['loc']]:
						y[t][j].setAttr("obj", gamma[t][j]*(self.RP[t][j]-1))
					else:
						y[t][j].setAttr("obj", gamma[t][j]*self.RP[t][j])

		self.m.update()

	def solve(self, settings={}):	
		# Given a fully-formulated model, as well as solver settings, solves 
		#	the PIP, and returns the model object associated with the resulting
		#	optimal solution.
		# Settings is a dictionary whose keys are model parameters (e.g., MIPGap,
		#	OutputFlag), and whose values, well, duh.
	
		# Putting settings into effect.
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
		# If the model has already been solved, return objective associated
		#	 with optimal solution
		return self.m.objVal

	def estimateUtilization(self):
		# If the model has already been solved, finds average ambulance utilization
		#	associated with the optimal solution. (By summing busy times and dividing
		#	by (# ambs)*(length of horizon)
		x	  = self.v['x']
		calls = self.calls
		dist  = self.dist
		busy  = 0.0
		for t in calls:
			loc = calls[t]['loc']
			svc = calls[t]['svc']
			for j in sorted(self.B[loc]):
				for k in self.bases:
					if x[t][j][k].x > 1e-6:
						temp = svc + dist[loc][j] + dist[loc][k]
						if t + temp > self.T:
							busy += self.T - t
						else:
							busy += temp 
	
		return busy/(1.0*self.A*self.T)
		

	def estimateGradient(self):
		# Given an already solved instance of this IP model, returns the gradient
		#	estimate arising from this solution.
		y = self.v['y']

		if self.dof == 1:
			gradSample = np.zeros(self.T+1)
			for t in range(self.T+1):
				for j in self.bases:
					gradSample[t] += y[t][j].x*self.RP[t][j]
					if t in self.calls and j in self.B[self.calls[t]['loc']]:
						gradSample[t] -= y[t][j].x
		else:
			gradSample = np.zeros((self.T+1, len(self.bases)))
			for t in range(self.T+1):
				for j in self.bases:
					gradSample[t][j] = y[t][j].x*self.RP[t][j]
					if t in self.calls and j in self.B[self.calls[t]['loc']]:
						gradSample[t][j] -= y[t][j].x

		return gradSample
