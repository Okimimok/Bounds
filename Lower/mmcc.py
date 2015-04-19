# Assorted steady-state calculations for an M/M/C/C/ system
import numpy as np


def computeDenominator(rho, C):
	terms = np.zeros(C+1)
	for j in xrange(C+1):
		terms[j] = 1
		for k in xrange(1, j+1):
 			terms[j] *= rho/k
	
	return sum(terms), terms

def stationaryDist(lam, mu, C):
	# Given arrival rate, service rate, and the number of servers, gives the
	# 	steady-state probability that exactly i servers are available
	rho          = float(lam)/mu
	denom, terms = computeDenominator(rho, C)
	stdist       = [terms[i]/denom for i in xrange(C+1)]
	return stdist[-2::-1]
	

def erlangLoss(lam, mu, C):
	# Loss probability using the Erlang-B formula
	rho          = float(lam)/mu
	denom, terms = computeDenominator(rho, C)
	return terms[C]/denom 
