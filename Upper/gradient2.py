import numpy as np
from ..Components.SamplePath2 import SamplePath2
from random import seed

# Methods that can be used to perform a gradient search with respect
#       to the penalty parameters gamma (gamma_t, gamma_tj)
def fullSearch(svca, astr, sdist, penalty, IP, stngs, N, randSeed, iters, freq=-1, debug=0):
    print('Initialization...')
    gamma = penalty.getGamma()
    obj   = 0
    nabla = np.zeros(gamma.shape)
    seed(randSeed)

    for j in range(N):
        if freq > 0 and (j + 1) % freq == 0 : print('  Path %i' % (j+1))

        omega  = SamplePath2(svca, astr, sdist)
        m      = IP.ModelInstance(svca, astr, omega)
        m.updateObjective(gamma)
        m.solve(stngs)
        obj   += m.getObjective()/N
        nabla += m.estimateGradient()/N
        for i in range(len(nabla)):
            nabla[i] = min(nabla[i], 0)
        
    for i in range(iters):
        if debug: print('Line Search, Iteration %i' % (i+1))

        cands    = {}
        bestStep = 0.0
        bestVal  = obj
        bestGrad = np.array(nabla)
        seed(randSeed)

        for step in penalty.getStepSizes():
            cands[step] = {'val': 0.0, 'grad': np.zeros(gamma.shape)}

        if debug: print('  Step Size 0, Mean Obj. %.4f' % bestVal)

        for j in range(N):
            if freq > 0 and (j + 1) % freq == 0 : print('  Path %i' % (j+1))
            # Generate sample path, create skeleton of IP
            omega = SamplePath2(svca, astr, sdist)
            m     = IP.ModelInstance(svca, astr, omega)

            # Set of multipliers being evaluated
            for step in penalty.getStepSizes():
                m.updateObjective(gamma - step*nabla)
                m.solve(stngs)
                cands[step]['val']  += m.getObjective()/N
                cands[step]['grad'] += m.estimateGradient()/N
                        
        for step in penalty.getStepSizes():
            if debug: print('  Step Size %.3f, Obj. %.4f' % (step, cands[step]['val']))

            if cands[step]['val'] < bestVal:
                bestStep = step 
                bestVal  = cands[step]['val']
                bestGrad = cands[step]['grad']

        # If step size is zero, take smaller steps. O/w, update gradient.
        if bestStep == 0:
            penalty.scaleStepSizes(0.5)
        else:
            penalty.updateGamma(-bestStep*nabla)
            nabla = np.array(bestGrad)
            obj   = bestVal

def solvePIPs(svca, astr, sdist, gamma, IP, stngs, N, freq=-1):
    # Solves N instances of the IP corresponding to different sample 
    #    paths. Outputs the objective value attained in every problem
    #    instance, as well as an estimate of the gradient.
    # IPmodel is a (handle to a) class, instances of which correspond
    #     to instances of the model of interest. 
    # Prints progress to console every freq sample paths

    obj   = np.zeros(N)
    nabla = np.zeros(gamma.shape)
   
    for i in range(N):
        if freq > 0 and (i + 1) % freq == 0: print('  Path %i' % (i+1))
                
        # Generate sample path, solve IP, get gradient estimate
        omega  = SamplePath2(svca, astr, sdist)
        prob   = IP.ModelInstance(svca, astr, omega)
        prob.updateObjective(gamma)
        prob.solve(stngs)
        obj[i] = prob.getObjective()
        nabla += prob.estimateGradient()/N

    return obj, nabla
