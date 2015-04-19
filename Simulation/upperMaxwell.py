from futureEventsList import futureEventsList
import numpy as np
		
def simulate(svcDists, omega, A, v = None, debug = False):
	# svcDists a dictionary containing ServiceDistribution objects: one for 
	#	each possible number of ambulances that can be available. E.g.,
	#	svcDists[i] = Service time distribution when i servers free
	# v = Reward vector, allowed to depend on the number of available
	#	servers. A dictionary (keys start at 1). Defaults to vector of ones.
	
	calls = omega.getCalls()
	C	  = len(calls)
	times = sorted(calls.keys())
	
	# Initial simulation state
	simState = {}
	simState['ambs']  = A
	simState['t']	  = 0
	simState['debug'] = debug

	if v is not None:
		simState['v'] = v
	else:
		simState['v'] = np.ones(A+1)
			
	simStats = {}
	simStats['obj']   = 0.0
	simStats['calls'] = 0
	simStats['busy']  = 0.0
	simStats['util']  = 0.0
	c = 0
	
	# Initialize FEL w/ first event (first arrival)
	# Can let simulation end at T+1, as obj can only increase via 
	#	call arrivals, which cannot occur after T.
	# Arrivals have priority 1. This allows service to complete 
	#	before determining feasible dispatches
	# The end event has priority 2, so events occurring at time T
	#	can clear from the FEL first. 
	T	= omega.T
	fel = futureEventsList()
	fel.addEvent(T, 'end', priority=2)
	if len(calls) > 0: 
		fel.addEvent(times[0], 'arrival', priority=1)
		 
	# Bug to be fixed later: code actually executes for one event after 'end' occurs
	# 	Restructure loop.
	while simState['t'] < T + 1:
		# Print pending service completions (has to be done before next event
		# 	pulled off FEL)
		if simState['debug']:
			busy = fel.searchEvents('service')
			if len(busy) > 0:
				tmp    = sorted([i[0] for i in busy])
				svcStr = 'Pending services: ' + ''.join(str(foo) + ' ' for foo in tmp)

		# Find next event, update total busy time, advance clock
		nextEvent		  = fel.findNextEvent()
		delta			  = nextEvent[0] - simState['t']
		simStats['busy'] += delta*(A - simState['ambs'])
		simState['t']	  = nextEvent[0]
		eventType		  = nextEvent[1]
		
		if simState['debug']:
			print 'Time %i' % simState['t']
			if len(busy) > 0: print svcStr
			else: print 'All ambulances idle'

		# Execute relevant event					 
		if eventType == 'arrival':
			# Handle the arrival, schedule next one
			executeArrival(simState, simStats, fel, calls[simState['t']])
			c += 1
			if c < C: fel.addEvent(times[c], 'arrival', priority=1)
			
		elif eventType == 'service': 
			executeService(simState)
		else: 
			if simState['debug']: print 'End simulation'
			break
			
		if simState['debug']: print ''
	
	if simState['debug']:
		 print '\n%i calls served, reward %.3f\n' % (simStats['calls'], simStats['obj'])
	
	# Average ambulance utilization
	simStats['util'] = simStats['busy']/(1.0*T*A)

	return simStats
			
def executeArrival(simState, simStats, fel, call):
	# Determine service time based upon number of ambs available
	svc = call['svc'][simState['ambs']]
	r   = call['rnd']
	
	if simState['debug']: print 'Arrival (Rnd = %.4f, Svc time = %i)' % (r, svc)
	
	if simState['ambs'] > 0:			   
		reward = simState['v'][simState['ambs']]
		simState['ambs']  -= 1			
		simStats['calls'] += 1
		simStats['obj']   += reward			
		finishTime = simState['t'] + svc
		fel.addEvent(finishTime, 'service')
			
		if simState['debug']:
			print 'Dispatch. Reward: %.3f' % reward
			print 'Completion time: %i' % finishTime 
			print '%i call(s) served, total reward: %.3f' % \
										(simStats['calls'], simStats['obj'])
		
			print '%i ambulances available' % simState['ambs']
		
	elif simState['debug']: print 'Call lost'
		
def executeService(simState):
	simState['ambs'] += 1
	
	if simState['debug']: print 'Service\n%i ambulances available' % simState['ambs']
