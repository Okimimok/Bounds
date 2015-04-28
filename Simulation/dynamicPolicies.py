from math import ceil
import numpy as np

# An assortment of compliance table policies
def daskinRedeploy(state, location, fel, svca):
	# Checks for the first deviation from a compliance table policy,
	#	and sends the ambulance there.
	nodes = svca.nodes
	bases = svca.bases
	R     = svca.getR()
	
	# Locations of ambulances that are idle, being redeployed
	redp = [i[2] for i in fel.searchEvents('redeployment')]
	idle = []
	for j in svca.bases:
		for i in range(state['ambs'][j]):
			idle.append(j)
	eff  = sorted(redp+idle)

	# Computing node coverages
	cvg = np.zeros(len(nodes))
	
	for j in eff:
		for i in R[j]:
			cvg[i] += 1

	# Find base maximizing improvement to coverage
	bestBase  = -1
	bestDelta = -1
	for j in bases:
		delta = sum([nodes[i]['prob']*state['q']*(1-state['q'])**(cvg[i] - 1)\
								 for i in R[j]])
		if delta > bestDelta:
			bestDelta = delta
			bestBase  = j
	
	finish = int(ceil(state['t'] + svca.dist[location][bestBase]))
	fel.addEvent(finish, 'redeployment', bestBase)

	if state['debug']:
		print('Service completion at node %s' % str(svca.nodes[location]['loc']))
		print('To be redeployed to base %s' % str(svca.bases[bestBase]['loc']))
		print('Redeployment completes at time %i' % finish)
