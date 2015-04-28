from gurobipy import Model, GRB, LinExpr 
import numpy as np

class ModelInstance:
	# The maximum coverage location problem, adapted to allow for nested compliance
	#	tables. Approach is due to Gendreau, Laporte, and Semet (2006)
	# w is a vector that can be used to weight the importance of the objective
	#	function for particular system states. Defaults to equal weights
	def __init__(self, svcArea, arrStream, A, w = None):
		self.nodes = svcArea.nodes
		self.bases = svcArea.bases
		self.A     = A
		self.B     = svcArea.getB()
		self.PN    = arrStream.getPN()
		self.w     = w
		self.formulate()

	def formulate(self):
		self.m = Model()

		###################### DECISION VARIABLES
		# Number of ambulances to locate at base j, when a ambulances are free
		x = {}
		for a in range(1, self.A+1):
			x[a] = {}
			for j in self.bases:
				x[a][j]  = self.m.addVar(lb=0, ub=a, vtype=GRB.INTEGER)

		# Is node i covered by an ambulance in "state" a?
		y = {}
		for a in range(1, self.A+1):
			y[a] = {}
			for i in self.nodes:
				y[a][i] = self.m.addVar(lb=0, ub=1, obj=self.w[a]*self.PN[1][i],\
											 vtype=GRB.BINARY)

		self.m.update()

		###################### CONSTRAINTS
		# Coverage constraints
		for a in range(1, self.A+1):
			for i in self.nodes:
				expr = LinExpr()
				for j in self.B[i]:
					expr.add(x[a][j], 1)
				self.m.addConstr(expr >= y[a][i])
	
		# Fleet capacity
		for a in range(1, self.A+1):
			expr = LinExpr()
			for j in self.bases:
				expr.add(x[a][j], 1)
			self.m.addConstr(expr == a)
	
		# Nesting constraints
		for a in range(1, self.A):
			for j in self.bases:
				self.m.addConstr(x[a][j] <= x[a+1][j])

		# Dictionary containing model decision variables
		self.v = {'x' : x, 'y' : y}

	def solve(self, settings={}):	
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
