class myQueue:
    def __init__(self,size):#sets up variables required for circular queue structure
        self.size = size
        self.queue = [None]*(self.size)
        
        #position of first item in queue, position of first item after end of queue
        self.start = -1
        self.end = 0

    def deQueue(self):
        x = self.isEmpty()
        if not x:
            #removes and returns the value at queue[start]
            self.val = self.queue.pop(self.start)
            #changes front of queue to next item waiting
            self.start = (self.start+1) % (self.size)
            #maintains size of the queue
            self.queue.insert((self.start-1),None)
            print("Value removed from queue.")
    
    def enQueue(self, value):
        self.val = value
        if None in self.queue:#checks for space in queue
            #inserts value at the back of queue and removes a None (keep size)
            self.queue.insert((self.end),self.val)
            self.queue.remove(None)
            #adjusting size for queue
            if self.start == -1:
                self.start = 0
                self.end = 1
            else:
                self.end = (self.end+1) % (self.size)
            print("Value added to queue.")
        else:#queue must be full
            print("Not possible.")
        
    def isEmpty(self):
        for element in self.queue: #if any element != None, list is not empty
            if element != None:
                return False
            else:
                pass
        print("Queue empty.")
        return True

    def isFull(self):
        for element in self.queue:#if any element = None, list is not full
            if element == None:
                return False
            else:
                pass
        return True

class HiddenValues:
    def __init__(self,item):
        self.item = item

    def hideValues(self,startVal,endVal):
        self._hiddenVal = list(self.item)
        #replaces values up to endval with *
        for i in range (startVal,endVal+1):
            (self._hiddenVal)[i-1]='*'
        self.hiddenWord = ''.join(self._hiddenVal)
        return self.hiddenWord