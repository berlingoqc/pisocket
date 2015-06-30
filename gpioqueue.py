class Queue(object):
    def Enqueue(self,*kargs):
        self.items = []
        for v in kargs:
            self.items.append(v)
    
    def Print_Queue(self):
        for i in self.items: print(i)
    
    def Dequeue(self, nbr=1):
        for i in range(nbr): 
            pin = self.items.pop(0)
            v = self.items.pop(0)
            self.Set_Value(pin,v)
