import os
from time import time,sleep
from threading import Thread
import re
import select

def GetDirection(pin,direction):
    if pin in listPinExport():
        with open("/sys/class/gpio%i/direction" % pin, 'r') as f:
            if f.read() == direction:
                return True
    return False

def listPinExport():
    a = re.compile("gpio[0-9]+")
    return [c.replace("gpio","") for f in os.walk("/sys/class/gpio") for c in f[1] if a.match(c) is not None]

class GPIO(object):
    #Construction
    def __init__(self,kargs):
        #if super pwm
        self.Clean_All()
        self.dictGPIO = {}
        self.Setup(kargs)
    #Thread function
    def _threadEdge(self,pin,mode):
        previous_state = None
        with open("/sys/class/gpio/gpio%i/value" % pin,'r') as f:
            bLoop = True
            valeur = self._edge()
            po = select.poll()
            po.register(f,select.POLLPRI)
            while bLoop:
                #Set a timeout of 60 sec
                events = po.poll(100)
                f.seek(0)
                last_state = f.read()
                if valeur != 2 and last_state[0] == valeur:
                    bLoop = False
                elif last_state[0] != previous_state:
                    bLoop = False
                    previous_state = last_state[0]
    #Private function
    def _write(self,path,contents):
        with open(path, 'w') as f:
            f.write(contents)
    def _read(self,path):
        with open(path, 'r') as f:
            retour = f.read()
            return retour
    def _unexport(self,pin):
        if os.path.isfile("/sys/class/gpio/gpio%i/direction" % pin):
            self._write("/sys/class/gpio/unexport", str(pin))
    def _export(self,pin):
        if os.path.isfile("/sys/class/gpio/gpio%i/direction" % pin):
            self._unexport(pin)
        self._write("/sys/class/gpio/export",str(pin))
        self.dictGPIO[pin] = None
    def _edge(self,mode):
        x = ["falling", "rising", "both"]
        if x.__contains__(mode):
            return True

    #Public function
    def Wait_Edge(self, pin, mode):
        self._threadEdge(pin, mode)

    def CallBack_Edge(self, pin, mode, callback):
        pass

    def Pulse_High(self,pin):
        assert 0<=pin<=40
	#setup priority polling for more accuratetime reading, POLLPRI = There is urgent data to read
        with open("/sys/class/gpio/gpio%i/value" % pin, 'r') as f:
            po = select.poll()
            po.register(f,select.POLLPRI)
            #Read high pulse width
            startTime = time()
            endTime = time()
            measureCycle = 0
            while True:
                events = po.poll(60000)
                f.seek(0)
                last_state= f.read()
                #Reading high pulse width
                if last_state[0] == '0' and measureCycle == 1:
                    endTime = time()
                    break
                if last_state[0] == '1' and measureCycle == 0:
                    startTime = time()
                    measureCycle = 1
                if len(events) == 0:
                    raise Exception('timeout')
        return endTime - startTime
    def Setup(self,kargs):
        for k,v in kargs.items():
            self._export(k)
            self._write("/sys/class/gpio/gpio%i/direction" % k, v[0])
            if v[0] == "out":
                self.Set_Value(k,v[1])
    def Set_Value(self,pin,value):
        assert value in ("1","0")
        self._write("/sys/class/gpio/gpio%i/value" % pin,value)
    def Get_Value(self,pin):
        retour = self._read("/sys/class/gpio/gpio%i/value" % pin)
        return retour
    def Clean_All(self):
        for i in listPinExport():
            self._unexport(int(i))
