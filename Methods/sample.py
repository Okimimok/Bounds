from random import random
from scipy.stats import norm
from numpy import average, std

def discreteN(probs):
    # Given a list of values of length N, with returns a sample of a RV X with
    #   support {0, 1, ..., N-1}, and for which P(X = i) = probs[i], or 'null'
    #   if pmf does not sum to one, and item in support not selected

    r     = random()
    index = 0
    
    for prob in probs:
        r -= prob
        if r < 0: 
            break
        else:
            index += 1

    if r > 0: index = 'null'
    
    return index

def discreteDict(A):
    # Given a dictionary of values, of the form A[key] = p,
    #   returns a sample of a random variable X where P(X = key) = p, or
    #   'null' if pmf does not sum to one, and item in support not selected
    r  = random()

    for key in A:
        r -= A[key]
        if r < 0: break

    if r > 0: key = 'null'
    
    return key
    
def generateCalls(nodes, svcTime, P):
    # Given a graph (represented by a list of nodes), a service time dist.
    #   (stored as a dict), an arrival probability matrix P, generates a
    #   sample path of arrivals (times, locations, service reqt's)
    calls = {}
    
    for t in xrange(len(P)):
        # Call pmf at time t
        callLoc = discreteN(P[t])
        
        if callLoc != 'null':
            calls[t]        = {}
            calls[t]['loc'] = callLoc
            calls[t]['svc'] = discreteDict(svcTime)
    return calls

def confInt(A, level=0.95):
    # Given an array A of values, computes a 100*(1-level)% CI of the
    #   form "mean +/- hwidth"

    n  = len(A)
    z  = norm.ppf(norm.cdf(1-0.5*level))
    mu = average(A)
    hw = z*std(A)/(n**0.5)

    return mu, hw
