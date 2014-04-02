
import collections
import time
import datetime

class TimeExpiredDict:
    """
TimeExpiredDict. Implemented only IN,LEN,STR  operators !!
    """
    def __init__(self, timeout):
        self.timeout = timeout
        self.container = {}

    def add(self,item):
        """Add event time
        """
        if item in self:
            return True

        self.container[item] = time.time()
        return  True  #return True, that item was sucessfully added

    def __len__(self):
        """Return number of active events
        """
        return len(self.container)


    def __str__(self):
        return 'Container: %s' % str(self.container.keys())

    def __contains__(self, val):
        if val in self.container:
            if time.time() - self.container[val] < self.timeout:
                return True
            else:
                self.container.pop(val,None)
                return False



c = TimeExpiredDict(timeout=1)
assert(len(c) == 0) #blank dict
print(c)

c.add('BOB')
c.add('BOB') #Bob will be added only once , here you will see error message
 
c.add('SANDY') #add new client
assert(len(c) == 2) #check we have both clients in dict
print(c)
print('BOB' in c)
time.sleep(4)

print('BOB' in c)

print(c)

time.sleep(4)

print('SANDY' in c)
print(c)

