from gurobipy import Model, GRB, LinExpr 
from ..Methods.sample import binary_search 
import numpy as np

class ModelInstance:
    # Modification of PIP2 in which coverage also includes ambulances en route
    #   to a base. Time-based penalty multipliers only.
    def __init__(self, svca, astr, omega, gamma=None):
        self.nodes     = svca.nodes
        self.bases     = svca.bases
        self.dist      = svca.getDist()
        self.B         = svca.getB()
        self.A         = svca.A 
        self.RP        = astr.getRP()
        self.T         = astr.T
        self.calls     = omega.getCalls()
        self.callTimes = omega.callTimes
        self.numCalls  = omega.numCalls
        self.Q         = omega.getQ()
        self.Q2        = omega.getQ2()

        # Create model object and dictionary of decision vars
        self.formulate(gamma)

    def formulate(self, gamma):
        # Formulates the integer program, by defining the appropriate decision
        #       variables and constraints. Objective function values for the x-vars
        #       are set, but those for the y-vars are kept to zero. 
        #
        # Returns the resulting model, as well as a dictionary containing 
        #       decision variables.
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

        # Effective coverage of base j at time t
        z = {}
        if gamma is not None:
            for t in range(1, self.T+1):
                z[t] = {}
                for j in self.bases:
                    if t in self.calls and j in self.B[self.calls[t]['loc']]:
                        z[t][j] = self.m.addVar(lb=0, ub=self.A, vtype=GRB.INTEGER,\
                                        obj = gamma[t]*(self.RP[t][j]-1))
                    else:
                        z[t][j] = self.m.addVar(lb=0, ub=self.A, vtype=GRB.INTEGER,\
                                        obj = gamma[t]*self.RP[t][j])
        else:
            for t in range(1, self.T+1):
                z[t] = {}
                for j in self.bases:
                    z[t][j] = self.m.addVar(lb=0, ub=self.A, vtype=GRB.INTEGER)
                        
        self.m.update()

        ######################### CONSTRAINTS
        # IP constraints, all melded into one for loop. Probably difficult
        #       to read, and so longform included at end of file.
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
        
        # Linking z-variables with x-variables and y-variables
        for t in range(1, self.T+1):
            for j in self.bases:
                expr = LinExpr(1, y[t][j])
                for (s, k) in self.Q2[t][j]:
                    expr.add(x[s][k][j], 1) 
                self.m.addConstr(z[t][j] == expr)

        # Dictionary containing model decision variables
        self.v = {'x' : x, 'y' : y, 'z': z}

    def updateObjective(self, gamma):
        # Updates the objective function coefficients for the y-variables
        z        = self.v['z']
        self.dof = gamma.ndim

        for t in range(1, self.T+1):
            for j in self.bases:
                if t in self.calls and j in self.B[self.calls[t]['loc']]:
                    z[t][j].setAttr("obj", gamma[t]*(self.RP[t][j]-1))
                else:
                    z[t][j].setAttr("obj", gamma[t]*self.RP[t][j])
                                                
        self.m.update()

    def solve(self, settings={}):   
        # Given a fully-formulated model, as well as solver settings, solves 
        #   the PIP, and returns the model object associated with the resulting
        #   optimal solution.
        # Settings is a dictionary whose keys are model parameters (e.g., MIPGap,
        #   OutputFlag), and whose values, well, duh.
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
        #   with optimal solution
        return self.m.objVal

    def estimateGradient(self):
        # Given an already solved instance of this IP model, returns the gradient
        #   estimate arising from this solution.
        z = self.v['z']

        gradSample = np.zeros(self.T+1)
        for t in range(1, self.T+1):
            for j in self.bases:
                gradSample[t] += z[t][j].x*self.RP[t][j]
                if t in self.calls and j in self.B[self.calls[t]['loc']]:
                    gradSample[t] -= z[t][j].x

        return gradSample
