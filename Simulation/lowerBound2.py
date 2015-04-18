import sys
from ..Classes.FutureEventsList import FutureEventsList
		
def simulate(svcArea, omega, executeService, debug = False):
	# executeService a function handle that takes as input
	#  
	# 1) simState : Simulation state
	# 2) location : The location at which a service completion occurs
	# 3) fel	  : Future events list
	# 4) svcArea  : Object containing network data (distances, neighbor-
	#				 hoods, locations, etc.)
	# 
	# and then:
	# 
	# a) Selects a base to which to redeploy the ambulance
	# b) Updates the FEL accordingly
	
	bases = svcArea.getBases()
	calls = omega.getCalls()
	C	  = len(calls)
	times = sorted(calls.keys())
	locs  = [calls[t]['loc'] for t in times] 
	svcs  = [calls[t]['svc'] for t in times]
	
	# Initial simulation state
	# A = Number of ambulances in the system
	simState = {}
	simState['ambs']  = [bases[j]['alloc'] for j in bases]
	simState['t']	  = 0
	simState['A']     = sum(simState['ambs'])
	simState['debug'] = debug

	# Simulation output
	simStats = {}
	simStats['obj']   = 0
	simStats['calls'] = 0
	simStats['busy']  = 0
	
	# Initialize FEL w/ first event (first arrival)
	# Can let simulation end at T+1, as obj can only increase via 
	#	call arrivals, which cannot occur after T.
	# Arrivals have priority 1. This allows redeployments to finish
	#	before determining feasible dispatches
	# The end event has priority 2, so events occurring at time T
	# 	can clear from the FEL first. 
	T	= omega.T
	c   = 0
	fel = FutureEventsList()
	fel.addEvent(T+1, 'end', priority=2)
	if len(calls) > 0:
		fel.addEvent(times[c], 'arrival', (locs[c], svcs[c]), 1)
		
	while simState['t'] < T + 1 and fel.eventCount() > 0:
		# Find next event, update cumulative busy time, advance clock
		nextEvent	      = fel.findNextEvent()
		delta             = nextEvent[0] - simState['t']
		simStats['busy'] += delta*(simState['A'] - sum(simState['ambs']))
		simState['t']     = nextEvent[0]
		eventType	      = nextEvent[1]
		
		if simState['debug']:
			print 'Time %i' % simState['t']
			
			# Print pending service completions
			if simState['debug']:
				onScene = fel.searchEvents('service')
				if len(onScene) > 0:
					temp =	''
					for i in onScene:
						tempLoc = str(svcArea.nodes[i[2]]['loc'])
						temp += tempLoc + ' <' + str(int(i[0])) + '> '
					print 'Pending service completions: ' + temp
				else:
					print 'No ambulances treating patients'
		
			# Print idle ambulances
			if simState['debug']:
				idle = [j for j in bases if simState['ambs'][j] > 0]
				if len(idle) > 0:
					temp =	''
					for j in idle:
						temp += str(bases[j]['loc']) + ' '
					print 'Ambulances available at: ' + temp
				else:
					print 'All ambulances busy'
			
			# Print pending redeployments
			if simState['debug']:
				# Pending redeployments
				redeploys = fel.searchEvents('redeployment')
				if len(redeploys) > 0:
					temp =	''
					for j in redeploys:
						tempLoc = str(bases[j[2]]['loc'])
						temp += tempLoc + ' <' + str(int(j[0])) + '> '
					print 'Redeployments in progress to: ' + temp
				else:
					print 'No ambulances being redeployed'
						
		# Execute relevant event					 
		if eventType == 'arrival':
			# Handle the arrival, schedule next one
			executeArrival(simState, simStats, nextEvent[2], fel, svcArea)
			c += 1
			if c < C: fel.addEvent(times[c], 'arrival', (locs[c], svcs[c]), 1)
			
		elif eventType == 'service':
			executeService(simState, nextEvent[2], fel, svcArea)
			
		elif eventType == 'redeployment':
			executeRedeployment(simState, nextEvent[2], svcArea)
			
		if simState['debug']: print ''
	
	if simState['debug']:
		print 'End of simulation.'
		print '%i calls served' % simStats['obj']
	
	# Average ambulance utilization
	simStats['util'] = simStats['busy']/(1.0*T*simState['A'])
	return simStats
			
def executeArrival(simState, simStats, callInfo, fel, svcArea):
	nodes = svcArea.getNodes()
	bases = svcArea.getBases()
	B	  = svcArea.getB()
	BA    = svcArea.getBA()
	dist  = svcArea.getDist()
	
	# Call info
	loc = callInfo[0]
	svc = callInfo[1]
	finishTime = -1
	
	if simState['debug']:
		print 'Arrival at node %s' % str(nodes[loc]['loc'])
	
	# Assign closest ambulance (if applicable), schedule svc. completion
	for j in BA[loc]:
		if simState['ambs'][j] > 0:			   
			simState['ambs'][j] -= 1			
			simStats['calls']   += 1
			if j in B[loc]:
				simStats['obj'] += 1			
			finishTime = simState['t'] + svc + dist[loc][j]
			fel.addEvent(finishTime, 'service', loc)
			
			if simState['debug']:
				print 'Response from base %s' % str(bases[j]['loc'])
				if j in B[loc]:
					print 'Timely response, reward collected'
				else:
					print 'Ambulance arrives late'
				print '%i call(s) served, reward %i' %\
							 (simStats['calls'], simStats['obj'])
				print 'Arrival time: %i' % (simState['t'] + dist[loc][j])
				print 'Service time: %i' % svc
				print 'Call to be completed at time %i' % finishTime
			break
		
	if finishTime == -1 and simState['debug']: print 'Call lost'
		
def executeRedeployment(simState, base, svcArea):
	bases = svcArea.bases
	
	# Increment by one the number of ambulances available at destination
	simState['ambs'][base] += 1
	
	if simState['debug']: print 'Redeployment to base %s' % str(bases[base]['loc'])
