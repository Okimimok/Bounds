from .FutureEventsList import FutureEventsList          
from math import ceil
import pdb

def simulate(svca, omega, executeServiceLB, q=0.5, eta=0, v=None, debug=False):
    # Simultaneous simulation of two systems: one lower bound (via a feasible
    #   redeployment policy and one upper bound (original Matt Maxwell)
    # Used to find a loss system in which the lower bound outperforms the 
    #   upper bound
    # A fusion of upperMaxwell.py and lowerAll.py 

    bases = svca.getBases()
    calls = omega.getCalls()
    C     = len(calls)
    times = sorted(calls.keys())
    locs  = [calls[t]['loc'] for t in times] 
    svcs  = [calls[t]['svc'] for t in times]
    A     = svca.A

    # Tracking states for both systems
    stateLB = {}
    stateLB['ambs']  = [bases[j]['ambs'] for j in bases]
    stateLB['t']     = 0
    stateLB['A']     = A
    stateLB['q']     = q
    stateLB['debug'] = debug
    stateLB['eta']   = eta

    stateUB = {}
    stateUB['t']     = 0
    stateUB['ambs']  = A
    stateUB['debug'] = debug

    if v is not None:
        stateUB['v'] = v
    else:
        stateUB['v'] = np.ones(A+1)

    # Summary statistics for both systems
    statsLB = {}
    statsLB['call'] = 0
    statsLB['obj']  = 0
    statsLB['late'] = 0
    statsLB['miss'] = 0
    statsLB['busy'] = 0

    statsUB = {}
    statsUB['call'] = 0
    statsUB['obj']  = 0.0
    statsUB['miss'] = 0
    statsUB['busy'] = 0.0
    statsUB['util'] = 0.0

    # Two FELs, both initialized with first arrival and end event
    #   Location doesn't matter in upper bounding system
    T  = omega.T
    c  = 0
    felLB = FutureEventsList()
    felLB.addEvent(T+1, 'end', priority=-1)

    felUB = FutureEventsList()
    felUB.addEvent(T+1, 'end', priority=-1)

    if C > 0:
        felLB.addEvent(times[0], 'arrival', (locs[0], svcs[0]), 1)
        felUB.addEvent(times[0], 'arrival',  1)

    # Extract first event from each FEL
    nextLB = felLB.findNextEvent()
    nextUB = felUB.findNextEvent()
                
    while stateLB['t'] <= T and stateUB['t'] <= T:
        # Find the first event to occur (from either FEL)
        timeLB = nextLB[0]
        timeUB = nextUB[0]
        tau    = min(timeLB, timeUB)

        # Update statistics, advance clock
        delta = tau - stateLB['t']

        statsLB['busy'] += delta*(A - sum(stateLB['ambs']))
        statsUB['busy'] += delta*(A - stateUB['ambs'])

        stateLB['t'] = tau
        stateUB['t'] = tau

        # Next events to occur in each system
        eventLB = nextLB[1]
        eventUB = nextUB[1]

        # If next event to occur in both systems are arrivals, process both
        #   simultaneously. (Arrivals have lower priority than svc completions
        #   or redeployments, in case of lower bd.)
        # Otherwise, event in one system is occurring earlier (in which case,
        #   process that event), OR
        # One system has an arrival, while the other has svc completions or
        #   redeployments to clear (in which case, process non-arrivals first.)
        if eventLB == 'arrival' and eventUB == 'arrival':
            ambsLB = sum([stateLB['ambs'][j] for j in bases])
            ambsUB = stateUB['ambs']

            executeArrivalLB(stateLB, statsLB, calls[stateLB['t']], felLB, svca)
            executeArrivalUB(stateUB, statsUB, calls[stateUB['t']], felUB)

            if c < C - 1:
                c += 1
                felLB.addEvent(times[c], 'arrival', priority=1)
                felUB.addEvent(times[c], 'arrival', priority=1)

            nextLB = felLB.findNextEvent()
            nextUB = felUB.findNextEvent()

        elif timeLB == tau and eventLB != 'arrival':
            if eventLB == 'service':
                executeServiceLB(stateLB, nextLB[2], felLB, svca)
                nextLB = felLB.findNextEvent()
            elif eventLB == 'redeployment':
                executeRedeployment(stateLB, nextLB[2])
                nextLB = felLB.findNextEvent()

        elif timeUB == tau:
            if eventUB == 'service':
                executeServiceUB(stateUB)
                nextUB = felUB.findNextEvent()


    # Average ambulance utilization
    statsLB['util'] = statsLB['busy']/(1.0*T*A)
    statsUB['util'] = statsUB['busy']/(1.0*T*A)

    return statsLB, statsUB
                        
def executeArrivalLB(stateLB, statsLB, call, felLB, svca):
    B     = svca.getB()
    BA    = svca.getBA()
    dist  = svca.getDist()
        
    # Call info
    loc = call['loc']
    svc = call['svc']
    finishTime = -1
        
    # Assign closest ambulance (if applicable), schedule svc. completion
    for j in BA[loc]:
        if stateLB['ambs'][j] > 0:                           
            stateLB['ambs'][j] -= 1
                                
            arrivalTime = stateLB['t'] + dist[loc][j]

            if j in B[loc]:
                statsLB['obj'] += 1
            else:
                statsLB['late'] += 1

            finishTime = int(ceil(arrivalTime + svc))
            felLB.addEvent(finishTime, 'service', (loc, j))
            break
                
    if finishTime < 0:
        statsLB['miss'] += 1

def executeArrivalUB(stateUB, statsUB, call, felUB):
    svc = call['mxw'][stateUB['ambs']]

    if stateUB['debug']:
        print('Time %i: Call arrival' % stateUB['t'])
        
    if stateUB['ambs'] > 0:                      
        reward = stateUB['v'][stateUB['ambs']]
        stateUB['ambs'] -= 1                      
        statsUB['call'] += 1
        statsUB['obj']  += reward                 
        finishTime = stateUB['t'] + svc
        if stateUB['debug']:
            print('Call served, to finish at %i' % finishTime)
            print('%i ambulances remaining\n' % stateUB['ambs'])
        felUB.addEvent(finishTime, 'service')
    else:
        statsUB['miss'] += 1
        if stateUB['debug']:
            print('Call lost\n')

def executeServiceUB(stateUB):
    stateUB['ambs'] += 1
    if stateUB['debug']:
        print('Time %i: Service completion' % stateUB['t'])
        print('%i ambulances free \n' % stateUB['ambs'])
                
def executeRedeployment(stateLB, base):
    stateLB['ambs'][base] += 1
