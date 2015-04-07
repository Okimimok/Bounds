from gurobipy import Model, GRB, quicksum 
import numpy as np

class ModelInstance:
	def __init__(self, svcArea, arrStream, svcDist, m, r):	
		self.d   = arrStream.getPN()
		self.A   = m
		self.r   = r
		self.t   = svcArea.getDist()
		self.tau = svcArea.getNBdist()
		self.formulate(svcArea, svcDist)
		
	def formulate(self, svcArea, svcDist):
		########################################################
		###################### BEGIN MODEL
		########################################################
		self.m = Model()

		###################### DECISION VARIABLES
		# Will an ambulance b placed at base j? 
		x = {}	
		for j in svcArea.bases:
			x[j] = self.m.addVar(lb=0, ub=1, vtype = GRB.BINARY)

		# Call at node i covered by ambulance at base j?
		y = {}
		for i in svcArea.nodes:
			y[i] = {}
			for j in svcArea.bases:
				y[i][j] = self.m.addVar(lb=0, ub=1, vtype=GRB.BINARY)

		# Probability that call from node i can be serviced within r periods
		p = {}
		for i in svcArea.nodes:
			p[i] = self.m.addVar(lb=0, obj=self.d[1][i])
			
		self.m.update()

		######################### CONSTRAINTS
		# Ambulances that can be located
		self.m.addConstr(quicksum(x[j] for j in svcArea.bases) <= self.A)

		# No coverage unless ambulance there
		for i in svcArea.nodes:
			for j in svcArea.bases:
				self.m.addConstr(y[i][j] <= x[j])

		# Coverage in at most one location
		for i in svcArea.nodes:
			self.m.addConstr(quicksum(y[i][j] for j in svcArea.bases) == 1)

		# Linking p-variables to y-varaibles
		for i in svcArea.nodes:
			temp = [svcDist.evalCDF(self.r - self.t[i][j] - self.tau[i])\
						for j in svcArea.bases]
			self.m.addConstr(p[i] == quicksum(y[i][j]*temp[j] for j in svcArea.bases))
												
		# Dictionary containing model decision variables
		self.v = {'x' : x, 'y' : y, 'p' : p}
		
	def solve(self, settings={}):	
		# Given a fully-formulated model, as well as solver settings, solves 
		#	the IP, and returns the model object associated with the resulting
		#	optimal solution.
		# Settings is a dictionary whose keys are model parameters (e.g., MIPGap,
		#	OutputFlag), and whose values, well, duh.
	
		# Putting settings into effect.
		if 'OutputFlag' in settings:
			self.m.setParam('OutputFlag', settings['OutputFlag'])

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
		# If model solved, return objective associated with optimal solution
		return self.m.objVal
	
