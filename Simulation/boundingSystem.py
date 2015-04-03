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
	simState['obj']   = 0
	simState['t']	  = 0
	simState['debug'] = debug
	c = 0
	
	# Initialize FEL w/ first event (first arrival)
	# Can let simulation end at T+1, as obj can only increase via 
	#	call arrivals, which cannot occur after T.
	# Arrivals have priority 1. This allows service to complete 
	#	before determining feasible dispatches
	T	= omega.T
	fel = FutureEventsList()
	fel.addEvent(T+1, 'end')
	if len(calls) > 0:
		fel.addEvent(times[c], 'arrival', rnds[c], 1)
		
	while simState['t'] < T + 1:
		# Find next event, advance clock
		nextEvent	  = fel.findNextEvent()
		simState['t'] = nextEvent[0]
		eventType	  = nextEvent[1]
		
		if simState['debug']:
			print 'Time %i' % simState['t']
			
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
			executeArrival(simState, nextEvent[2], fel, svcDists)
			c += 1
			if c < C:
				fel.addEvent(times[c], 'arrival', rnds[c], 1)
			
		elif eventType == 'service':
			executeService(simState)
			
		if simState['debug']: print ''
	
	if simState['debug']:
		print 'End of simulation.'
		print '%i calls served' % simState['obj']
	
	return simState['obj']
			
def executeArrival(simState, r, fel, svcDists):
	# Call info
	svc = svcDists[simState['ambs']].sample(r)
	
	if simState['debug']:
		print 'Call arrival (Svc time = %i)' % svc
	
	# Assign closest ambulance (if applicable), schedule svc. completion
	if simState['ambs'] > 0:			   
		simState['ambs'] -= 1			
		simState['obj']  += 1			
		finishTime = simState['t'] + svc
		fel.addEvent(finishTime, 'service', -1)
			
		if simState['debug']:
			print 'Call receives response, %i ambulances left' % simState['ambs']
			print 'To be completed at time %i' % finishTime 
			print '%i call(s) served' % simState['obj']
		
	elif simState['debug']:
		print 'Call lost'
		
def executeService(simState):
	# Increment by one the number of available ambulances 
	simState['ambs'] += 1
	
	if simState['debug']:
		print 'Service completion' 
		print '%i ambulances available' % simState['ambs']
