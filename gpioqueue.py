import newgpio

class Queue(newgpio.GPIO):
    
    def __init__():
        self.listcmd = []

    def __str__(self):
        for i in self.listcmd:
            print(i)
    
    def enqueue(self,dictCmd):
        for k,v in dictCmd.items():
            if k == 1:
                a = lambda: self.Set_Value(v[1],v[2]),0
            elif k == 2:
                a = lambda: self.Get_Value(V[1]),1, v[1]
            elif k == 3:
                a = lambda: self.Setup({v[1]:[v[2],v[3]]}),0
            elif k == 4:
                a = lambda: self._unexport(v[1]),0
            self.listcmd.append(a)

    def dequeue(self, nbr=0, keep=False):
        dictretour = {}
        keeplist = []
        nbr = len(self.listcmd) if nbr == 0 else nbr
        for i in range(nbr): 
            function = self.listcmd.pop(0)
            if keep:
                keeplist.append(function)
            if function[1] == 1:
                 dictretour[function[2]] = function[0]()
            else:
                function()
            self.listcmd += keeplist
        return dictretour

