class FutureEventsList():
    def __init__(self):
        # Initialize with time at which simulation ends
        self.fel = []
                
    def addEvent(self, eventTime, eventName, param = -1, priority = 0):
        # Third argument : associated with an event. Could be an
        #        arbitrary object. Defaults to -1 if no extra info needed.
        #
        # Event priority an optional parameter (defaults to 0).
        #        Events with lower priority numbers take precedence
        self.fel.append([eventTime, eventName, param, priority])
                
    def removeEvent(self, eventTime, eventName, param, priority):
        self.fel.remove([eventTime, eventName, param, priority])
                
    def searchEvents(self, name):
        # Finds all events of type name, returns all hits as a list
        hits = []
        for event in self.fel:
            if event[1] == name:
                hits.append([event[0], event[1], event[2], event[3]])
                                
        return sorted(hits)
                
    def eventCount(self):
        # Finds the number of events in the FEL
        return len(self.fel)

    def findNextEvent(self):
        # Find next event to occur (taking priorities into account)
        minTime = -1
        minPrio = 999
                
        for i in self.fel:
            if (minTime == -1 or i[0] < minTime) or\
                            (i[0] == minTime and i[3] < minPrio):
                minTime  = i[0]
                minName  = i[1]
                minParam = i[2]
                minPrio  = i[3]
                                
        self.removeEvent(minTime, minName, minParam, minPrio)
                                
        return [minTime, minName, minParam, minPrio]
