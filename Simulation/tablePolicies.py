from math import ceil

# An assortment of compliance table policies
def compliance(simState, location, fel, svcArea, table):
	# Checks for the first deviation from a compliance table policy,
	#	and sends the ambulance there.

	# Locations of ambulances that are idle, being redeployed
	redp = [i[2] for i in fel.searchEvents('redeployment')]
	idle = []
	for j in svcArea.bases:
		for i in range(simState['ambs'][j]):
			idle.append(j)
	eff  = sorted(redp+idle)

	# Checking for a deviation...
	done = False
	for a in range(1, len(eff)+2):
		tmp = list(eff)	
		for b in range(a):
			if table[a][b] not in tmp:
				newBase = table[a][b]
				done    = True
			else:
				tmp.remove(table[a][b])

		if done: break
	
	finish = int(ceil(simState['t'] + svcArea.dist[location][newBase]))
	fel.addEvent(finish, 'redeployment', newBase)

	if simState['debug']:
		print('Service completion at node %s' % str(svcArea.nodes[location]['loc']))
		print('To be redeployed to base %s' % str(svcArea.bases[newBase]['loc']))
		print('Redeployment completes at time %i' % finish)
