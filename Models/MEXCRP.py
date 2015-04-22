from gurobipy import Model, GRB, LinExpr 
import numpy as np

class ModelInstance:
	# MEXCRP, adapted to allow for nested compliance tables. Approach is due to 
	# 	Gendreau, Laporte, and Semet (2006), although they used MCLP instead.
	#
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
		for a in xrange(1, self.A+1):
			x[a] = {}
			for j in self.bases:
				x[a][j]  = self.m.addVar(lb=0, ub=a, vtype=GRB.INTEGER)

		# Is node i covered by at least k ambulances in state a?
		y = {}
		for a in xrange(1, self.A+1):
			y[a] = {}
			for i in self.nodes:
				y[a][i] = {}
				for k in xrange(1, a+1):
					coeff      = self.w[a]*self.PN[1][i]*(1-self.q)*(self.q**(k-1))
					y[a][i][k] = self.m.addVar(lb=0, ub=1, obj=coeff, vtype=GRB.BINARY)

		self.m.update()

		###################### CONSTRAINTS
		# Coverage constraints
		for a in xrange(1, self.A+1):
			for i in self.nodes:
				exprX = LinExpr()
				exprY = LinExpr()
				for j in self.B[i]:
					exprX.add(x[a][j], 1)
				for k in xrange(1, a+1):
					exprY.add(y[a][i][k], 1)
				self.m.addConstr(exprX >= exprY)
	
		# Fleet capacity
		for a in xrange(1, self.A+1):
			expr = LinExpr()
			for j in self.bases:
				expr.add(x[a][j], 1)
			self.m.addConstr(expr == a)
	
		# Nesting constraints
		for a in xrange(1, self.A):
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
