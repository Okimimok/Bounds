from gurobipy import Model, GRB, LinExpr 

class ModelInstance:
	# The maximum coverage location problem of Church and ReVelle (1971)
	def __init__(self, svcArea, arrStream, A):
		self.nodes = svcArea.nodes
		self.bases = svcArea.bases
		self.A     = A
		self.B     = svcArea.getB()
		self.PN    = arrStream.getPN()
		self.formulate()

	def formulate(self):
		self.m = Model()

		###################### DECISION VARIABLES
		# Number of ambulances to locate at base j
		x = {}
		for j in self.bases:
			x[j] = self.m.addVar(lb=0, ub=self.A, vtype=GRB.INTEGER)

		# Is node i covered by an ambulance?
		y = {}
		for i in self.nodes:
			y[i] = self.m.addVar(lb=0, ub=1, obj = self.PN[1][i], vtype=GRB.BINARY)

		self.m.update()

		###################### CONSTRAINTS
		# Coverage constraints
		for i in self.nodes:
			expr = LinExpr()
			for j in self.B[i]:
				expr.add(x[j], 1)
			self.m.addConstr(expr >= y[i])
	
		# Fleet capacity
		expr = LinExpr()
		for j in self.bases:
			expr.add(x[j], 1)
		self.m.addConstr(expr == self.A)

		# Dictionary containing model decision variables
		self.v = {'x' : x, 'y' : y}

	def solve(self, settings={}):	
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
		# If model solved, return objective associated with optimal solution
		return self.m.objVal
