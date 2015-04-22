import sys
from futureEventsList import futureEventsList
		
def simulate(svcArea, omega, executeService, debug=False):
	# executeService a function handle that takes as input
	#  
	# 1) state : Simulation state
	# 2) location : The location at which a service completion occurs
	# 3) fel	  : Future events list
	# 4) svcArea  : Object containing network data (distances, neighbor-
	#				 hoods, locations, etc.)
	# and then selects a base to which to redeploy the ambulance
	
	bases = svcArea.getBases()
	calls = omega.getCalls()
	C	  = len(calls)
	times = sorted(calls.keys())
	locs  = [calls[t]['loc'] for t in times] 
	svcs  = [calls[t]['svc'] for t in times]
	
	# Initial simulation state, A = Number of ambulances in the system
	state = {}
	state['ambs']  = [bases[j]['alloc'] for j in bases]
	state['t']	   = 0
	state['A']     = sum(state['ambs'])
	state['debug'] = debug

	# Summary statistics
	stats = {}
	stats['call'] = 0
	stats['obj']  = 0
	stats['late'] = 0
	stats['miss'] = 0
	stats['busy'] = 0
	
	# Initialize FEL w/ first event (first arrival) and last event (end)
	# Arrivals have priority 1. End event has priority -1 (happens first at T+1). 
	T	= omega.T
	c   = 0
	fel = futureEventsList()
	fel.addEvent(T+1, 'end', priority=-1)
	if len(calls) > 0: fel.addEvent(times[c], 'arrival', (locs[c], svcs[c]), 1)
		
	while state['t'] <= T:
		# Find next event, update cumulative busy time, advance clock
		nextEvent	   = fel.findNextEvent()
		delta          = nextEvent[0] - state['t']
		stats['busy'] += delta*(state['A'] - sum(state['ambs']))
		state['t']     = nextEvent[0]
		eventType	   = nextEvent[1]
		
		if state['debug']:
			print 'Time %i' % state['t']
			
			# Print pending service completions, idle ambulances, pending redeploys
			if state['debug']:
				tmp  = fel.searchEvents('service')
				if len(tmp) > 0:
					output = ''
					for svc in tmp:
						tmpLoc = str(svcArea.nodes[svc[2]]['loc'])
						temp += tmpLoc + ' <' + str(int(svc[0])) + '> '
					print 'Pending service completions: %s' % output 
				else:
					print 'No ambulances treating patients'
		
				idle = [j for j in bases if state['ambs'][j] > 0]
				if len(idle) > 0:
					output = ''
					for j in idle:
						output += str(bases[j]['loc']) + ' '
					print 'Ambulances available at: %s' % output 
				else:
					print 'All ambulances busy'
			
				redeploys = fel.searchEvents('redeployment')
				if len(redeploys) > 0:
					output =	''
					for j in redeploys:
						tmpLoc = str(bases[j[2]]['loc'])
						output += tmpLoc + ' <' + str(int(j[0])) + '> '
					print 'Redeployments in progress to: %s' % output
				else:
					print 'No ambulances being redeployed'
						
		# Execute relevant event					 
		if eventType == 'arrival':
			# Handle the arrival, schedule next one
			executeArrival(state, stats, nextEvent[2], fel, svcArea)
			c += 1
			if c < C: fel.addEvent(times[c], 'arrival', (locs[c], svcs[c]), 1)
			
		elif eventType == 'service':
			executeService(state, nextEvent[2], fel, svcArea)
			
		elif eventType == 'redeployment':
			executeRedeployment(state, nextEvent[2], svcArea)
		
		else:
			if state['debug']: print 'End of simulation.'
			
		if state['debug']: print ''
	
	# Average ambulance utilization
	stats['util'] = stats['busy']/(1.0*T*state['A'])
	return stats
			
def executeArrival(state, stats, callInfo, fel, svcArea):
	nodes = svcArea.getNodes()
	bases = svcArea.getBases()
	B	  = svcArea.getB()
	BA    = svcArea.getBA()
	dist  = svcArea.getDist()
	debug = state['debug']
	
	# Call info
	loc = callInfo[0]
	svc = callInfo[1]
	finishTime = -1
	
	if debug: print 'Arrival at %s' % str(nodes[loc]['loc'])
	
	# Assign closest ambulance (if applicable), schedule svc. completion
	for j in BA[loc]:
		if state['ambs'][j] > 0:			   
			state['ambs'][j] -= 1
			if debug: print 'Response from %s' % str(bases[j]['loc'])
				
			arrivalTime = state['t'] + dist[loc][j]
			if debug: print 'Arrival time: %i' % (state['t'] + dist[loc][j])

			if j in B[loc]:
				stats['obj'] += 1
				if debug: print 'Ambulance arrives in time'
			else:
				stats['late'] += 1
				if debug: print 'Ambulance arrives late'

			finishTime  = arrivalTime + svc 
			fel.addEvent(finishTime, 'service', loc)
			if debug:
				print 'Service time %i, call finishes at %i' % (svc, finishTime)
				print '%i call(s) served in time, %i late' % (stats['late'], stats['obj'])
			break
		
	if finishTime < 0:
		stats['miss'] += 1
		if debug: print 'Call lost\n%i missed calls' % stats['miss']
		
def executeRedeployment(state, base, svcArea):
	bases = svcArea.bases
	
	# Increment by one the number of ambulances available at destination
	state['ambs'][base] += 1
	
	if state['debug']: print 'Redeployment to %s' % str(bases[base]['loc'])
