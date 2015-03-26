from gurobipy import *
import numpy as np

def solve(svcArea, arrStream, omega, penalty, flag=False):
    # Unpacking relevant problem instance parameters
    nodes = svcArea.nodes
    bases = svcArea.bases
    B     = svcArea.getB()
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
    m  = Model()

    ###################### DECISION VARIABLES
    # When call c arrives, can an ambulance respond?
    v = {}
    for t in calls:
        loc  = calls[t]['loc']
        v[t] = m.addVar(lb=0, ub=1, obj=0, vtype=GRB.BINARY)

    # At time t, can system respond to call arriving at node i?
    w = {}
    for t in xrange(1, T+1):
        w[t] = {}
        for i in nodes:
            w[t][i] = m.addVar(lb=0, ub=1, obj=0, vtype=GRB.BINARY)

    # Respond to call c with ambulance from base j, and redeploy to k?
    x = {}  
    for t in calls:
        x[t] = {}
        for j in B[calls[t]['loc']]:
            x[t][j] = {}
            for k in bases:
                x[t][j][k] = m.addVar(lb=0, ub=1, obj=1, vtype=GRB.BINARY)

    # At time t, the number of idle ambulances at base j
    y = {}
    for t in xrange(T+1):
        y[t] = {}
        for j in bases:
            y[t][j] = m.addVar(lb=0, ub=A, vtype=GRB.INTEGER)            
                
    # Objective: To minimize calls not receiving timely response
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
                    # Could base j have dispatched an ambulance?
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

    # Determining values for w-variables
    for t in xrange(1, T+1):
        for i in nodes:
            m.addConstr(w[t][i] <= quicksum(y[t][j] for j in B[i]))

    # Constraints for v-variables
    for t in calls:
        loc = calls[t]['loc']
        m.addConstr(A*v[t] >= quicksum(y[t][j] for j in B[loc]))
        
    
    ################################
    ### Valid Inequalities
    ################################
    
    # Linking v-variables and w-varaibles
    for t in calls:
        loc = calls[t]['loc']
        m.addConstr(v[t] == w[t][loc])
        
    # v_t = 1 if dispatch made
    for t in calls:
        loc = calls[t]['loc']
        m.addConstr(v[t] >= quicksum(quicksum(x[t][j][k] \
                                for j in B[loc]) for k in bases))
                                    
    # Constraints on v-variables whenever calls don't arrive
    for t in calls:
        if t > 1:
            if t-1 not in calls:   
                loc = calls[t]['loc']
                m.addConstr(v[t] >= w[t-1][loc])
    
    # IP solver settings
    m.setParam('OutputFlag', flag)
    m.setParam('MIPGap', 0.01)
    m.setParam('TimeLimit', 60)
    #m.setParam('Method', 2)   
    #m.setParam('Sifting', 0)
    
    ############################
    # Branch priority
    ############################
    for t in calls:
        v[t].setAttr('BranchPriority', 5)  
        
    # Iterate over various step sizes 
    obj = np.zeros(len(steps))
    for s in xrange(len(steps)):
        print '--------Step Size %.2f' % steps[s]
        current = gamma - steps[s]*nabla
        
        for t in xrange(1, T+1):
            if t in calls:
                v[t].setAttr("obj", -current[t])
            for i in nodes:
                w[t][i].setAttr("obj", current[t]*P[t][i])
                
        m.optimize()
        obj[s] = m.objVal
                  
    return obj