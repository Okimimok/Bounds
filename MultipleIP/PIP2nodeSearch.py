from gurobipy import *
import numpy as np

# Similar to PIP, but multi-counts coverage when computing penalties.
#   Variant of code allowing for quick evaluation (and gradient information)
#   from a single penalty.

def solve(svcArea, arrStream, omega, penalty, flag=False, grad=False):
    # Unpacking relevant problem instance parameters
    bases = svcArea.getBases()
    B     = svcArea.getB()
    R     = svcArea.getR()
    P     = arrStream.getP()
    T     = omega.T
    calls = omega.getCalls()
    Q     = omega.getQ()
    
    # The penalty
    gamma = penalty.getGamma()
    nabla = penalty.getNabla()
    steps = penalty.getStepSizes()
    
    # Number of ambulances in system
    A  = sum([bases[j]['alloc'] for j in bases])
    
    ########################################################
    ###################### BEGIN MODEL
    ########################################################
    m = Model()

    ###################### DECISION VARIABLES
    # Respond to call c with ambulance from base i, and redeploy to j?
    x = {}  
    for c in calls:
        x[c] = {}
        for j in sorted(B[calls[c]['loc']]):
            x[c][j] = {}
            for k in bases:
                x[c][j][k] = m.addVar(lb=0, ub=1, obj=1, vtype=GRB.BINARY)
    
    # At time t, the number of idle ambulances at base j
    # Proper objective coefficients to be added later
    y = {}
    for t in xrange(T+1):
        y[t] = {}

        for j in bases:
            if t in calls and j in B[calls[t]['loc']]:
                y[t][j] = m.addVar(lb=0, ub=A, vtype=GRB.INTEGER, obj=0)
            else:
                y[t][j] = m.addVar(lb=0, ub=A, vtype=GRB.INTEGER, obj=0)
                
    # Objective: To minimize calls not receiving timely response
    m.setParam('OutputFlag', flag)
    m.modelSense = GRB.MAXIMIZE
    m.update()

    ######################### CONSTRAINTS
    # At most one response to a call
    for t in calls:
        loc = calls[t]['loc']
        m.addConstr(quicksum(quicksum(x[t][j][k] for j in B[loc])\
                                                 for k in bases) <= 1)

    # No dispatch unless ambulance idle
    for t in calls:
        loc = calls[t]['loc']
        for j in B[loc]:
           m.addConstr(quicksum(x[t][j][k] for k in bases) <= y[t][j])

    # Flow balance for idle ambulances
    for t in xrange(T+1):
        if t > 0: 
            # Did a call arrive during the last time period?
            if (t-1) in calls:
                loc = calls[t-1]['loc']
                for j in bases:
                    # Could base i have dispatched an ambulance to the call?
                    if j in B[loc]:
                        m.addConstr(y[t][j] == y[t-1][j] \
                            + quicksum([x[s][k][j] for (s,k) in Q[t][j]])\
                            - quicksum([x[t-1][j][k] for k in bases]))
                    else:
                        m.addConstr(y[t][j] == y[t-1][j] \
                            + quicksum([x[s][k][j] for (s,k) in Q[t][j]]))     
            else:
                for j in bases: 
                    m.addConstr(y[t][j] == y[t-1][j] \
                        + quicksum([x[s][k][j] for (s,k) in Q[t][j]]))
        else:
            for j in bases:
                m.addConstr(y[t][j] == bases[j]['alloc'])
                
    ######################### SOLUTION
    # Iterating over a set of candidate penalties 
    obj = np.zeros(len(steps))

    for l in xrange(len(steps)):
        current = gamma - steps[l]*nabla

        # At time t, the number of idle ambulances at base j
        for t in xrange(T+1):
            if t in calls:
                callFlag = True
                loc      = calls[t]['loc']
            else:
                callFlag = False
                
            for j in bases:
                temp = sum([gamma[t][i]*P[t][i] for i in R[j]])
                
                if callFlag and j in B[loc]:
                    y[t][j].setAttr("obj", -current[t][loc] + temp)
                else:
                    y[t][j].setAttr("obj", temp)
           
                
        m.optimize()
        obj[l] = m.objVal

    return obj