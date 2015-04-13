from ..Classes.FutureEventsList import FutureEventsList
		
def simulate(svcDists, omega, debug = False):
	# svcDists a dictionary containing ServiceDistribution objects: one for 
	#	each possible number of ambulances that can be available. E.g.,
	#	svcDists[i] = Service time distribution when i servers free
	
	calls = omega.getCalls()
	C	  = len(calls)
	times = sorted(calls.keys())
	rnds  = [calls[t]['rnd'] for t in times] 
	A	  = len(svcDists) - 1
	
	# Initial simulation state
	simState = {}
	simState['ambs']  = A
	simState['t']	  = 0
	simState['debug'] = debug

	simStats = {}
	simStats['obj']  = 0
	simStats['busy'] = 0
	simStats['util'] = 0
	c = 0
	
	# Initialize FEL w/ first event (first arrival)
	# Can let simulation end at T+1, as obj can only increase via 
	#	call arrivals, which cannot occur after T.
	# Arrivals have priority 1. This allows service to complete 
	#	before determining feasible dispatches
	# The end event has priority 2, so events occurring at time T
	#	can clear from the FEL first. 
	T	= omega.T
	fel = FutureEventsList()
	fel.addEvent(T, 'end', priority=2)
	if len(calls) > 0: fel.addEvent(times[c], 'arrival', rnds[c], 1)
		
	while simState['t'] < T + 1 and fel.eventCount() > 0:

		# Find next event, update total busy time, advance clock
		nextEvent		  = fel.findNextEvent()
		delta			  = nextEvent[0] - simState['t']
		simStats['busy'] += delta*(A - simState['ambs'])
		simState['t']	  = nextEvent[0]
		eventType		  = nextEvent[1]
		
		if simState['debug']: print 'Time %i' % simState['t']

		# Print pending service completions
		if simState['debug']:
			busy = fel.searchEvents('service')
			print '%i ambulances available' % (A - len(busy))
			if len(busy) > 0:
				tmp = sorted([i[0] for i in busy])
				print 'Pending services: ' + ''.join(str(foo) + ' ' for foo in tmp)

		# Execute relevant event					 
		if eventType == 'arrival':
			# Handle the arrival, schedule next one
			executeArrival(simState, simStats, nextEvent[2], fel, svcDists)
			c += 1
			if c < C: fel.addEvent(times[c], 'arrival', rnds[c], 1)
			
		elif eventType == 'service': executeService(simState)
			
		if simState['debug']: print ''
	
	if simState['debug']: print 'End simulation. \n%i calls served.' % simStats['obj']
	
	# Average ambulance utilization
	simStats['util'] = simStats['busy']/(1.0*T*A)

	return simStats
			
def executeArrival(simState, simStats, r, fel, svcDists):
	svc = svcDists[simState['ambs']].sample(r)
	
	if simState['debug']: print 'Call arrival (Rnd = %.4f, Svc time = %i)'\
					 % (r, svc)
	
	if simState['ambs'] > 0:			   
		simState['ambs'] -= 1			
		simStats['obj']  += 1			
		finishTime = simState['t'] + svc
		fel.addEvent(finishTime, 'service')
			
		if simState['debug']:
			print 'Call receives response, %i ambulances left' % simState['ambs']
			print 'To be completed at time %i' % finishTime 
			print '%i call(s) served' % simStats['obj']
		
	elif simState['debug']: print 'Call lost'
		
def executeService(simState):
	simState['ambs'] += 1
	
	if simState['debug']: print 'Service completion \n%i ambs available' % simState['ambs']
