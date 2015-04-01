from gurobipy import Model, GRB, quicksum 
import numpy as np

class ModelInstance:
	# Similar to PIP, but multi-counts coverage when computing penalties.
	#	Variant of code allowing for quick evaluation (and gradient information)
	#	from a single penalty.
	def __init__(self, svcArea, arrStream, omega):
		self.nodes = svcArea.nodes
		self.bases = svcArea.bases
		self.B	   = svcArea.getB()
		self.A	   = sum([self.bases[j]['alloc'] for j in self.bases])
		self.RP    = arrStream.getRP()
		self.T	   = arrStream.T
		self.calls = omega.getCalls()
		self.Q	   = omega.getQ()

		# Number of degrees of freedom in the penalty. Defaults to one.
		#	(1 = time based, 2 = time-location based)
		self.dof = 1 
		
		# Create model object and dictionary of decision vars
		self.formulate(svcArea, omega)

	def formulate(self, svcArea, omega):
		# Formulates the integer program, by defining the appropriate decision
		#	variables and constraints. Objective function values for the x-vars
		#	are set, but those for the y-vars are kept to zero. 
		#
		# Returns the resulting model, as well as a dictionary containing 
		#	decision variables.

	
		########################################################
		###################### BEGIN MODEL
		########################################################
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
		for t in xrange(self.T+1):
			y[t] = {}
			for j in self.bases:
				y[t][j] = self.m.addVar(lb=0, ub=self.A, vtype=GRB.INTEGER)
			
		self.m.update()

		######################### CONSTRAINTS
		# At most one response to a call
		for t in self.calls:
			loc = self.calls[t]['loc']
			self.m.addConstr(quicksum(quicksum(x[t][j][k] for j in self.B[loc])\
												 for k in self.bases) <= 1)

		# No dispatch unless ambulance idle
		for t in self.calls:
			loc = self.calls[t]['loc']
			for j in self.B[loc]:
			   self.m.addConstr(quicksum(x[t][j][k] for k in self.bases) <= y[t][j])

		# Flow balance for idle ambulances
		for t in xrange(self.T+1):
			if t > 0: 
				# Did a call arrive during the last time period?
				if (t-1) in self.calls:
					loc = self.calls[t-1]['loc']
					for j in self.bases:
						# Could base i have dispatched an ambulance to the call?
						if j in self.B[loc]:
							self.m.addConstr(y[t][j] == y[t-1][j] \
								+ quicksum([x[s][k][j] for (s,k) in self.Q[t][j]])\
								- quicksum([x[t-1][j][k] for k in self.bases]))
						else:
							self.m.addConstr(y[t][j] == y[t-1][j] \
								+ quicksum([x[s][k][j] for (s,k) in self.Q[t][j]]))	   
				else:
					for j in self.bases: 
						self.m.addConstr(y[t][j] == y[t-1][j] \
							+ quicksum([x[s][k][j] for (s,k) in self.Q[t][j]]))
			else:
				for j in self.bases:
					self.m.addConstr(y[t][j] == self.bases[j]['alloc'])

		# Dictionary containing model decision variables
		self.v = {'x' : x, 'y' : y}

	def updateObjective(self, gamma):
		# Takes as input:
		# m		: An already formulated PIP instance (w/ dec vars and constraints)
		# v		: A dictionary containing its decision varaibles
		# gamma : Vector of penalty weights 
		#
		# Updates the objective function coefficients for the y-variables
		y        = self.v['y']
		self.dof = gamma.ndim

		if self.dof == 1:
			for t in xrange(self.T+1):
				for j in self.bases:
					if t in self.calls and j in self.B[self.calls[t]['loc']]:
						y[t][j].setAttr("obj", gamma[t]*(self.RP[t][j]-1))
					else:
						y[t][j].setAttr("obj", gamma[t]*self.RP[t][j])
						
		else:
			for t in xrange(self.T+1):
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
		for option in settings:
			self.m.setParam(option, settings[option])

		self.m.modelSense = GRB.MAXIMIZE
		self.m.optimize()
		self.m.fixed()

	def getModel(self):
		return self.m

	def getDecisionVars(self):
		return self.v

	def getObjective(self):
		# If the model has already been solved, return objective associated with optimal solution
		return self.m.objVal

	def estimateGradient(self):
		# Given an already solved instance of this IP model, returns the gradient
		# 	estimate arising from this solution.
		y = self.v['y']

		if self.dof == 1:
			gradSample = np.zeros(self.T+1)
			for t in xrange(self.T+1):
				for j in self.bases:
					gradSample[t] += y[t][j].x*self.RP[t][j]
					if t in self.calls and j in self.B[self.calls[t]['loc']]:
						gradSample[t] -= y[t][j].x
		else:
			gradSample = np.zeros((self.T+1, len(self.bases)))
			for t in xrange(self.T+1):
				for j in self.bases:
					gradSample[t][j] = y[t][j].x*self.RP[t][j]
					if t in self.calls and j in self.B[self.calls[t]['loc']]:
						gradSample[t][j] -= y[t][j].x

		return gradSample
