from .FutureEventsList import FutureEventsList
import numpy as np
                
def simulate(svcDists, omega, A, v = None, debug = False):
    # svcDists a dictionary containing ServiceDistribution objects: one for 
    #       each possible number of ambulances that can be available. E.g.,
    #       svcDists[i] = Service time distribution when i servers free
    # v = Reward vector, allowed to depend on the number of available
    #       servers. A dictionary (keys start at 1). Defaults to vector of ones.
        
    calls = omega.getCalls()
    C     = len(calls)
    times = sorted(calls.keys())
        
    # Initial simulation state
    state = {}
    state['ambs']  = A
    state['t']     = 0
    state['debug'] = debug

    if v is not None:
        state['v'] = v
    else:
        state['v'] = np.ones(A+1)
                        
    stats         = {}
    stats['obj']  = 0.0
    stats['call'] = 0
    stats['miss'] = 0
    stats['busy'] = 0.0
    stats['util'] = 0.0
    c = 0
          
    # Initialize FEL w/ first event (first arrival) and last event (end)
    # Arrivals have priority 1. End event has priority -1 (happens first at T+1). 
    T   = omega.T
    fel = FutureEventsList()
    fel.addEvent(T+1, 'end', priority=-1)
    if len(calls) > 0: fel.addEvent(times[0], 'arrival', priority=1)
                 
    while state['t'] <= T:
        # Print pending service completions (has to be done before next event
        #       pulled off FEL)
        if state['debug']:
            busy = fel.searchEvents('service')
            if len(busy) > 0:
                tmp    = sorted([i[0] for i in busy])
                svcStr = 'Pending services: ' + ''.join(str(foo) + ' ' for foo in tmp)

        # Find next event, update total busy time, advance clock
        nextEvent      = fel.findNextEvent()
        delta          = nextEvent[0] - state['t']
        stats['busy'] += delta*(A - state['ambs'])/T
        state['t']     = nextEvent[0]
        eventType      = nextEvent[1]
                
        if state['debug']:
            print('Time %i' % state['t'])
            if len(busy) > 0: print(svcStr)
            else: print('All ambulances idle')

        # Execute relevant event                                         
        if eventType == 'arrival':
            # Handle the arrival, schedule next one
            executeArrival(state, stats, fel, calls[state['t']])
            c += 1
            if c < C: fel.addEvent(times[c], 'arrival', priority=1)
                        
        elif eventType == 'service': 
            executeService(state)
        else: 
            if state['debug']: print('End simulation\n')
        
        if state['debug']:
             print('\n%i calls served, reward %.3f\n' % (stats['call'], stats['obj']))
        
    # Average ambulance utilization
    stats['util'] = stats['busy']/(1.0*T*A)

    return stats
                        
def executeArrival(state, stats, fel, call):
    #print(call)
    # Determine service time based upon number of ambs available
    svc = call['mxw'][state['ambs']]
    r   = call['rnd']
        
    if state['debug']: print('Arrival (Rnd = %.4f, Svc time = %i)' % (r, svc))
        
    if state['ambs'] > 0:                      
        reward = state['v'][state['ambs']]
        state['ambs'] -= 1                      
        stats['call'] += 1
        stats['obj']  += reward                 
        finishTime = state['t'] + svc
        fel.addEvent(finishTime, 'service')
                        
        if state['debug']:
            print('Dispatch. Reward: %.3f' % reward)
            print('Completion time: %i' % finishTime)
            print('%i call(s) served, total reward: %.3f' % \
                                    (stats['call'], stats['obj']))
            print('%i ambulances available' % state['ambs'])
    else:
        stats['miss'] += 1
        if state['debug']: print('Call lost\n%i calls lost' % stats['miss'])
                
def executeService(state):
    state['ambs'] += 1
        
    if state['debug']: print('Service\n%i ambulances available' % state['ambs'])
