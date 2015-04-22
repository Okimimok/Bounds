def naive(simState, location, fel, svcArea):
	# Count the number of ambulances in the process of being redeployed.
	# --If 0 ambulances, redeploy to 0 or 3 (whichever is closer)
	# --If 1 ambulance, redeploy to 0 or 3 (whichever isn't occupied)
	# --If 2 ambulances, redeploy to 1 or 2 (whichever is closer)
	# --If 3 ambulances, redeploy to 1 or 2 (whichever isn't occupied)

	nodes = svcArea.getNodes()
	bases = svcArea.getBases()
	dist  = svcArea.getDist()
		
	# Ambulances being redeployed
	results = fel.searchEvents('redeployment')
	destinations = [i[2] for i in results]
	
	# Ambulances already idle
	available  = [j for j in bases if simState['ambs'][j] > 0]
	taken	   = available + destinations
	effFree    = len(taken)
	
	if effFree == 0:
		newBase = 3*(dist[location][3] < dist[location][0])
	elif effFree == 1:
		newBase = 3*(0 in taken)
	elif effFree == 2:
		newBase = 1 + (dist[location][2] < dist[location][1])
	else:
		newBase = 1*(2 in taken) + 2*(1 in taken)
 
	finishTime = simState['t'] + dist[location][newBase]
	fel.addEvent(finishTime, 'redeployment', newBase)
	

def nearest(simState, location, fel, svcArea):
	# Redeploy ambulance to nearest base
	B	  = svcArea.getB()
	dist  = svcArea.getDist()
	nodes = svcArea.getNodes()
	bases = svcArea.getBases()
	
	newBase = B[location][0] 
	finishTime = simState['t'] + dist[location][newBase]
	fel.addEvent(finishTime, 'redeployment', newBase)
	

def nearestEmpty(simState, location, fel, svcArea):
	# Redeploy ambulance to nearest empty base (disregrading redeployments
	#	to that base). 
	dist  = svcArea.getDist()
	nodes = svcArea.getNodes()
	bases = svcArea.getBases()
	
	minDist = 9999
	
	for j in bases:
		if simState['ambs'][j] == 0 and dist[location][j] < minDist:
			newBase = j
			minDist = dist[location][j] 
		
	finishTime = simState['t'] + dist[location][newBase]
	fel.addEvent(finishTime, 'redeployment', newBase)
	

def nearestEffEmpty(simState, location, fel, svcArea):
	# Redeploy ambulance to nearest empty base (disregrading redeployments
	#	to that base). 
	dist  = svcArea.getDist()
	nodes = svcArea.getNodes()
	bases = svcArea.getBases()
	
	# Number of ambulances being redeployed to each base
	results = fel.searchEvents('redeployment')
	temp	= [i[2] for i in results]
	redp	= [sum([i == j for i in temp]) for j in bases]
	eff		= [redp[j] + simState['ambs'][j] for j in bases]
	
	minDist = 9999
	
	for j in bases:
		if eff[j] == 0 and dist[location][j] < minDist:
			newBase = j
			minDist = dist[location][j] 
		
	finishTime = simState['t'] + dist[location][newBase]
	fel.addEvent(finishTime, 'redeployment', newBase)
   
'''
	if simState['debug']:
		print 'Service completion at node %s' % str(nodes[location]['loc'])
		print 'To be redeployed to base %s' % str(bases[newBase]['loc'])
		print 'Redeployment completes at time %i' % finishTime
'''
