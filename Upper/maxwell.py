import numpy as np
from ..Models import MMIP, MCLP
from ..Components.SvcDist import SvcDist

def buildEta(svcArea, arrStream, svcDist, filePath, debug=False):
    # Construct dominating service time distributions by solving a sequence
    #       of MCLPs for various values of r (cdf breakpoints) and a (number of
    #       available ambulances
    maxA  = sum([svcArea.bases[j]['ambs'] for j in svcArea.bases])
    maxR  = -1

    for i in svcArea.nodes:
        for j in svcArea.bases:
            temp = int(svcArea.getDist()[i][j] + svcArea.getNBdist()[i])
            if temp > maxR:
                maxR = temp

    maxR += max(svcDist.support)

    # Obtaining eta values
    eta      = np.zeros((maxR+1, maxA+1))
    settings = {'OutputFlag': 0, 'MIPGap': 0.005}

    for r in range(maxR + 1):
        for a in range(1, maxA+1):
            # Ceasing to solve IPs if we hit 1 on the cdf
            if eta[max(r-1,0)][a] >= 1 or eta[r][a-1] >= 1:
                eta[r][a] = 1
            else:
                p = MMIP.ModelInstance(svcArea, arrStream, svcDist, a, r)
                p.solve(settings)
                # Preserving monotonicity
                if r > 0:
                    eta[r][a] = abs(max(p.getObjective(), eta[r][a-1], eta[r-1][a]))
        
            if debug: print('r : %i of %i, a : %i of %i, Obj = %.4f' %\
                                                        (r, maxR, a, maxA, eta[r][a]))
        eta[r][0] = eta[r][1]
    return eta

def buildV(svcArea, arrStream, settings=None): 
    # Determine state-dependent rewards for Matt Maxwell's upper bound
    A = svcArea.A
    v = np.zeros(A+1)
    if settings is None:
        settings  = {'OutputFlag' : 0}

    for a in range(1, A+1):
        p = MCLP.ModelInstance(svcArea, arrStream, a)
        p.solve(settings)
        v[a] = p.getObjective()
        v[0] = v[1]

    return v

def writeEta(eta, etaPath):
    # Write Maxwell's service time distributions to file 
    with open(etaPath, 'w') as f:
        numR = len(eta)
        numA = len(eta[0])
        f.write('%i %i\n' % (numR, numA))
        fmtString = '%.4f ' * (numA-1) + '%.4f\n'

        for r in range(numR):
            f.write(fmtString  % tuple(abs(eta[r])))

def writeV(v, vPath):
    # Write state-dependent rewards to file
    tmp = len(v)
    with open(vPath, 'w') as f:
        f.write('%i\n' % tmp)
        for a in range(tmp):
            f.write('%i %.4f\n' % (a, v[a]))

def readEta(etaPath):
    # Read service time distributions from file, returns ServiceDistribution
    #       objects: one for each possible number of available ambulances
    with open(etaPath, 'r') as f:
        line  = f.readline().split()
        R     = int(line[0]) 
        M     = int(line[1])
        vals  = np.arange(1, R)
        cdfs  = np.empty((M, R))
        
        for r in range(R):
            line = f.readline().split()
            for m in range(M):
                cdfs[m][r] = float(line[m])

    svcDists = {}
    for m in range(M):
        pmf = cdfs[m][1:] - cdfs[m][:R-1]
        svcDists[m] = SvcDist(vals=vals, probs=pmf)

    return svcDists

def readV(vPath):
    with open(vPath, 'r') as f:
        tmp = int(f.readline()) 
        v   = np.zeros(tmp)
        for a in range(tmp):    
            line = f.readline().split()
            v[a] = float(line[1])

    return v
