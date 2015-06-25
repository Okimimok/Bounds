import numpy as np

def staticRedeploy(state, locData, fel, svca):
    nodes  = svca.nodes
    bases  = svca.bases
    q      = state['q']
    eta    = state['eta']
    ambLoc = locData[0]
    origin = locData[1]

    # Dispatched ambulances return from whence they came
    finish = state['t'] + svca.dist[ambLoc][origin]
    fel.addEvent(finish, 'redeployment', origin)

    if state['debug']:
        print('Service completion at node %s' % str(svca.nodes[ambLoc]['loc']))
        print('To be redeployed to base %s' % str(svca.bases[origin]['loc']))
        print('Redeployment completes at time %i' % finish)
