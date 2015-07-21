from gurobipy import Model, GRB, LinExpr 
from ..Methods.sample import binary_search 
import numpy as np

class ModelInstance:
    # New penalty: based upon idle time reduction. Idea is that under perfect i
    #   information, ambulances likely spend less time idling between calls.
    #   Penalty based upon "savings" that come with using that extra information.
    #
    # Given a redeployment decision, penalty proportional to amnt of time amb
    #   waits until first call it can reach (regardless of whether or not it'd 
    #   actually be dispatched to that call), versus expected wait time
    #   (based upon knowledge of the arrival stream)
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
        self.tau       = omega.getTau()

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
        if gamma is not None:
            for t in self.callTimes:
                x[t] = {}
                for j in self.B[self.calls[t]['loc']]:
                    x[t][j] = {}
                    for k in self.bases:
                        coeff      = 1 - gamma[t]*self.tau[t][j][k]
                        x[t][j][k] = self.m.addVar(lb=0, ub=1, obj=coeff, vtype=GRB.BINARY)
        else:
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
        
        # Dictionary containing model decision variables
        self.v = {'x' : x, 'y' : y}

    def updateObjective(self, gamma):
        # Updates the objective function coefficients for the y-variables
        x        = self.v['x']

        for t in self.callTimes:
            loc = self.calls[t]['loc']
            for j in self.B[loc]:
                for k in self.bases:
                    coeff = 1 - gamma[t]*self.tau[t][j][k]
                    x[t][j][k].setAttr("obj", coeff)
                                                
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
        x = self.v['x']

        gradSample = np.zeros(self.T+1)
        for t in self.callTimes:
            for j in self.B[self.calls[t]['loc']]:
                for k in self.bases:
                    gradSample[t] -= x[t][j][k].x*self.tau[t][j][k]

        return gradSample

    def countDispatches(self):
        # If IP model has already been solved, finds the number of actual dispatches
        #   made (separate from passive reward induced by the penalty)
        x     = self.v['x']
        B     = self.B
        disps = 0

        for t in self.callTimes:
            loc    = self.calls[t]['loc']
            disps += (sum([x[t][j][k].x for j in B[loc] for k in self.bases]) > 0)

        return disps

    def ambProfile(self):
        # If IP model has already been solved, finds for every number of available
        #   ambs (from 0 to A) the average number of ambs that are in/out of range.
        # Unweighted average: every visit to a given state weighted the same.
        #
        # Also returns the fraction of time spent in each state

        data = {}
        y    = self.v['y']
        nb   = len(self.bases)
        B    = self.B

        for a in range(self.A+1):
            data[a] = {'prop': 0.0, 'in': [], 'out': []}

        prevState = self.A
        prevTime  = 0

        for t in self.callTimes:
            data[prevState]['prop'] += (t - prevTime)/self.T
            state = int(sum([y[t][j].x for j in self.bases]))

            prevTime  = t
            prevState = state

            if state > 0:
                loc    = self.calls[t]['loc']
                tmpIn  = 0
                tmpOut = 0
                for j in range(nb):
                    if j in B[loc]:
                        tmpIn += int(y[t][j].x)
                    else:
                        tmpOut += int(y[t][j].x)

                data[state]['in'].append(tmpIn)
                data[state]['out'].append(tmpOut)

        # Final bit
        data[prevState]['prop'] += (self.T - t)/self.T

        return data 
