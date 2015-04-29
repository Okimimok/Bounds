from gurobipy import Model, GRB, LinExpr 
from ..Methods.sample import binary_search 
import numpy as np

# Perfect information problem with one-step look-ahead penalty. Involves
#	 a big-M constraint. Don't use for problems involving more than 2 or 3 
#	 ambulances. Warm start not implemented yet (and probably won't be).
#
# Time-based penalty multipliers only!

class ModelInstance:
	def __init__(self, svca, astr, omega, gamma=None):
		self.bases     = svca.bases
		self.nodes     = svca.nodes
		self.A         = svca.A 
		self.B         = svca.getB()
		self.P         = astr.getP()
		self.T         = omega.T
		self.calls     = omega.getCalls()
		self.callTimes = omega.callTimes
		self.numCalls  = omega.numCalls
		self.Q         = omega.getQ()

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
		for t in self.callTimes:
			x[t] = {}
			for j in self.B[self.calls[t]['loc']]:
				x[t][j] = {}
				for k in self.bases:
					x[t][j][k] = self.m.addVar(lb=0, ub=1, obj=1, vtype=GRB.BINARY)
	
		# At time t, the number of idle ambulances at base j
		y = {}
		for t in range(1, self.T+1):
			y[t] = {}
			for j in self.bases:
				y[t][j] = self.m.addVar(lb=0, ub=self.A, vtype=GRB.INTEGER)
			
		self.m.update()

		# When call c arrives, can an ambulance respond?
		v = {}
		if gamma is not None:
			for t in self.callTimes:
				v[t] = self.m.addVar(lb=0, ub=1, obj=-gamma[t], vtype=GRB.BINARY)
		else:
			for t in self.callTimes:
				v[t] = self.m.addVar(lb=0, ub=1, vtype=GRB.BINARY)

		# At time t, can system respond to call arriving at node i?
		w = {}
		if gamma is not None:
			for t in range(1, self.T+1):
				w[t] = {}
				for i in self.nodes:
					w[t][i] = self.m.addVar(lb=0, ub=1, obj=gamma[t]*self.P[t][i],\
									   vtype=GRB.BINARY)
		else:
			for t in range(1, self.T+1):
				w[t] = {}
				for i in self.nodes:
					w[t][i] = self.m.addVar(lb=0, ub=1, vtype=GRB.BINARY)
				
		self.m.update()	

		######################### CONSTRAINTS
		# At most one response to a call
		for t in self.callTimes:
			expr = LinExpr()
			loc  = self.calls[t]['loc']
			for j in self.B[loc]:
				for k in self.bases:
					expr.add(x[t][j][k], 1)
			self.m.addConstr(expr <= 1)

		# No dispatch unless ambulance idle
		for t in self.callTimes:
			loc  = self.calls[t]['loc']
			for j in self.B[loc]:
				expr = LinExpr()
				for k in self.bases:
					expr.add(x[t][j][k], 1)
				self.m.addConstr(expr <= y[t][j])

		# Determining values for w-variables
		for t in range(1, self.T+1):
			for i in self.nodes:
				expr = LinExpr()
				for j in self.B[i]:
					expr.add(y[t][j], 1)
				self.m.addConstr(expr >= w[t][i])

		# Constraints for v-variables
		for t in self.callTimes:
			loc  = self.calls[t]['loc']
			expr = LinExpr()
			for j in self.B[loc]:
				expr.add(y[t][j], 1)
			self.m.addConstr(expr <= self.A*v[t])

		# Flow balance for idle ambulances
		for t in range(self.T):
			if binary_search(self.callTimes, t, n=self.numCalls):
				loc = self.calls[t]['loc']
				for j in self.bases:
					expr = LinExpr(1, y[t][j])
					for (s, l) in self.Q[t+1][j]:
						expr.add(x[s][l][j], 1)

					if j in self.B[loc]:
						for k in self.bases:
							expr.add(x[t][j][k], -1)

					self.m.addConstr(expr == y[t+1][j])
			elif t > 0:
				for j in self.bases: 
					expr = LinExpr(1, y[t][j])
					for (s, k) in self.Q[t+1][j]:
						expr.add(x[s][k][j], 1)
					self.m.addConstr(expr == y[t+1][j])
			else:
				for j in self.bases:
					self.m.addConstr(y[1][j] == self.bases[j]['ambs'])
		
		######################## Valid Inequalities
		# Linking v-variables and w-varaibles
		'''
		for t in self.callTimes:
			loc = self.calls[t]['loc']
			self.m.addConstr(v[t] == w[t][loc])
		'''

		# v_t = 1 if dispatch made
		for t in self.callTimes:
			loc  = self.calls[t]['loc']
			expr = LinExpr()
			for j in self.B[loc]:
				for k in self.bases:
					expr.add(x[t][j][k], 1)
			self.m.addConstr(v[t] >= expr)
		'''
		# Constraints on v-variables whenever calls don't arrive
		for t in self.callTimes:
			if t > 1 and t-1 not in self.callTimes:   
				loc = self.calls[t]['loc']
				self.m.addConstr(v[t] >= w[t-1][loc])
		'''
		self.dvars = {'v': v, 'w': w, 'x': x, 'y': y}
		self.m.update()

	def updateObjective(self, gamma):
		# Takes as input:
		# m		: An already formulated PIP instance (w/ dec vars and constraints)
		# v		: A dictionary containing its decision varaibles
		# gamma : Vector of penalty weights 
		#
		# Updates the objective function coefficients for the y-variables
		v  = self.dvars['v']
		w  = self.dvars['w']

		for t in range(1, self.T+1):
			for i in self.nodes:
				w[t][i].setAttr("obj", self.P[t][i]*gamma[t])
				if binary_search(self.callTimes, t, n=self.numCalls):
					v[t].setAttr("obj", -gamma[t])

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
		return self.dvars

	def getObjective(self):
		# If the model has already been solved, return objective associated
		#	 with optimal solution
		return self.m.objVal
		
	def estimateGradient(self):
		# Given an already solved instance of this IP model, returns the gradient
		#	estimate arising from this solution.
		v = self.dvars['v']
		w = self.dvars['w']

		grad = np.zeros(self.T+1)
		for t in xrange(1, self.T+1):
			grad[t] = sum([w[t][i].x*self.P[t][i] for i in self.nodes])
			if binary_search(self.callTimes, t, n=self.numCalls):
				grad[t] -= v[t].x

		return grad
