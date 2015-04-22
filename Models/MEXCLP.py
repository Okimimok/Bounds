from gurobipy import Model, GRB, LinExpr 
import numpy as np

class ModelInstance:
	# q is a systemwide busy probability

	def __init__(self, svcArea, arrStream, A, q, w):
		self.nodes = svcArea.nodes
		self.bases = svcArea.bases
		self.A     = A
		self.q     = q
		self.B     = svcArea.getB()
		self.PN    = arrStream.getPN()
		self.w     = w
		self.formulate()

	def formulate(self):
		self.m = Model()

		###################### DECISION VARIABLES
		# Number of ambulances to locate at base j in state a
		x = {}
		for j in self.bases:
			x[j]  = self.m.addVar(lb=0, ub=self.A, vtype=GRB.INTEGER)

		# Is node i covered by at least k ambulances in state a?
		y = {}
		for i in self.nodes:
			y[i] = {}
			for k in xrange(1, self.A+1):
				coeff   = self.PN[1][i]*(1-self.q)*(self.q**(k-1))
				y[i][k] = self.m.addVar(lb=0, ub=1, obj=coeff, vtype=GRB.BINARY)

		self.m.update()

		###################### CONSTRAINTS
		# Coverage constraints
		for i in self.nodes:
			exprX = LinExpr()
			exprY = LinExpr()
			for j in self.B[i]:
				exprX.add(x[j], 1)
			for k in xrange(1, self.A+1):
				exprY.add(y[i][k], 1)
			self.m.addConstr(exprX >= exprY)
	
		# Fleet capacity
		expr = LinExpr()
		for j in self.bases:
			expr.add(x[j], 1)
		self.m.addConstr(expr == self.A)
	
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
