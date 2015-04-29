from math import ceil
import numpy as np

# An assortment of compliance table policies
def daskinRedeploy(state, location, fel, svca):
	# Checks for the first deviation from a compliance table policy,
	#	and sends the ambulance there.
	# eta weights various redeployment decisions by travel distance.
	#   E.g., if redeployment from node i to base j improves cvg. by 
	#   	C(i,j) and involves traveling d(i,j), assign index
	#				C(i,j)/(d(i,j)**eta)
	#	to that decision.
	#
	# q denotes a systemwide busy probability. Default value chosen
	#	for now, but could be replaced with more accurate measure of
	#	system utilization later.

	nodes = svca.nodes
	bases = svca.bases
	R     = svca.getR()
	q     = state['q']
	eta   = state['eta']
	
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
		num  = sum([nodes[i]['prob']*q*(1-q)**(cvg[i] - 1) for i in R[j]])
		
		# To avoid dividing by zero...
		tmp  = svca.dist[location][j]
		if tmp < 1:
			denom = 1
		else:
			denom = tmp**eta

		if num/denom > bestDelta:
			bestDelta = num/denom
			bestBase  = j
	
	finish = int(ceil(state['t'] + svca.dist[location][bestBase]))
	fel.addEvent(finish, 'redeployment', bestBase)

	if state['debug']:
		print('Service completion at node %s' % str(svca.nodes[location]['loc']))
		print('To be redeployed to base %s' % str(svca.bases[bestBase]['loc']))
		print('Redeployment completes at time %i' % finish)
