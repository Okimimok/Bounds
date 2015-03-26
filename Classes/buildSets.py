def distance(x, y):
    # Outputs Manhattan distance between two points x and y in R^2
    return abs(x[0] - y[0]) + abs(x[1] - y[1])

def buildB(nodes, bases, dist, maxDist):
    # Dictionary B, that for each node i, specifies the set of bases that
    #   can respond to a call at that node within the response time threshold
    #
    # Assumed dist[i][j] gives the distance from node i to base j
    B = {}
    for i in nodes:
        B[i] = []
        for j in bases:
            if dist[i][j] <= maxDist:
                B[i].append(j)
    return B

def buildQ(calls, bases, dist, B, T):
    Q = {}

    for t in xrange(T+1):
        Q[t] = {}
        for j in bases:
            Q[t][j] = []

    for c in calls:
        arr = calls[c]['loc']
        svc = calls[c]['svc']
        
        for j in B[arr]:
            for k in bases:
                busy  = svc + dist[arr][j] + dist[arr][k]
                ready = c + busy
                if ready <= T:
                    Q[ready][k].append((c, j))

    return Q

def buildR(nodes, bases, B):
    # Dictionary, with bases as keys
    # R[j] = Set of demand nodes to which response from base j possible
    R = {}
    for j in bases:
        R[j] = [i for i in nodes if j in B[i]]

    return R
