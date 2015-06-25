from gurobipy import Model, GRB, LinExpr 
from ..Methods.sample import binary_search 
import numpy as np

# "Revised PIP": Penalty not implemented yet, but variant of perfect information IP in
#    which dispatching and redeployment are separate decisions

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
        self.QD        = omega.getQD()
        self.QR        = omega.getQR()

        # Create model object and dictionary of decision vars
        self.formulate(gamma)

    def formulate(self, gamma):
        self.m = Model()

        ###################### DECISION VARIABLES
        # Respond to call t with ambulance from base j?
        xD = {}  
        for t in self.callTimes:
            for j in self.B[self.calls[t]['loc']]:
                xD[(t, j)] = self.m.addVar(lb=0, ub=1, obj=1, vtype=GRB.BINARY)
        
        # Redeploy ambulance at time t from node i to base j?
        xR = {}  
        for (t, i) in self.QD:
            for j in self.bases:
                xR[(t, i, j)] = self.m.addVar(lb=0, ub=self.A, vtype=GRB.INTEGER)

        # At time t, the number of idle ambulances at base j
        yD = {}
        for t in range(1, self.T+1):
            for j in self.bases:
                yD[(t, j)] = self.m.addVar(lb=0, ub=self.A, vtype=GRB.INTEGER)

        # At time t, the number of ambulances at node i awaiting redeployment
        yR = {}
        for (t, i) in self.QD:
            yR[(t, i)] = self.m.addVar(lb=0, ub=self.A, vtype=GRB.INTEGER)

        self.m.update()

        ######################### CONSTRAINTS
        # At most one response to a call
        for t in self.callTimes:
            expr = LinExpr()
            loc  = self.calls[t]['loc']
            for j in self.B[loc]:
                expr.add(xD[(t, j)], 1)
                self.m.addConstr(expr <= 1)

        # No dispatch unless ambulance idle
        for t in self.callTimes:
            loc = self.calls[t]['loc']
            for j in self.B[loc]:
                self.m.addConstr(xD[(t, j)] <= yD[(t, j)])

        # Flow balance for idle ambulances
        for t in range(self.T):
            if binary_search(self.callTimes, t, n=self.numCalls):
                loc = self.calls[t]['loc']
                for j in self.bases:
                    expr = LinExpr(1, yD[(t, j)])
                    if j in self.B[loc]:
                        expr.add(xD[(t, j)], -1)
                    if (t+1, j) in self.QR:
                        for (s, i) in self.QR[(t+1, j)]:
                            expr.add(xR[(s, i, j)], 1)
                    self.m.addConstr(expr == yD[(t+1, j)])

            elif t > 0:
                for j in self.bases: 
                    expr = LinExpr(1, yD[(t, j)])
                    if (t+1, j) in self.QR:
                        for (s, i) in self.QR[(t+1, j)]:
                            expr.add(xR[(s, i, j)], 1)
                    self.m.addConstr(expr == yD[(t+1, j)])
            else:
                for j in self.bases:
                    self.m.addConstr(yD[(1, j)] == self.bases[j]['ambs'])

        # Are ambulances available to be redeployed?
        for (t, i) in self.QD:
            expr = LinExpr()
            for (s, j) in self.QD[(t, i)]:
                expr.add(xD[(s, j)], 1)
            self.m.addConstr(expr == yR[(t, i)])

        for (t, i) in self.QD:
            expr = LinExpr()
            for j in self.bases:
                expr.add(xR[(t, i, j)], 1)
            self.m.addConstr(expr <= yR[(t, i)])
                
        self.dvars = {'xD': xD, 'xR': xR, 'yD': yD, 'yR': yR}
        self.m.update()

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
        return self.dvars

    def getObjective(self):
        return self.m.objVal
