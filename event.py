# -*- coding: utf-8 -*-
from threading import Thread, Lock
import newgpi
import gpioqueue
import select

class Event(newgpio.GPIO):
    def __init__(self):
        # PIN: [thread, bool ,gpioqueue, mode, HaveAppend, retourcallback]
        #le callback est une lambda
        self.lockSpi = Lock()
        self.PinEvent = {}
        # CHANNEL: [thread, bool , Function ,gpioqueue, [HaveAppend, value], retourcallback]
        self.SpiEvent = {}

    def __str__(self):
        #String representation of all the thread active both Pin and Spi in the object
        msg = ["Pin # {0} mode : {1}\nCallback : {2}".format(k,v[3]," ".join([str(i) for i in v[2]])) for k,v in self.PinEvent.items()]
        msg2 = ["Channel # {0} function : {1}\nCallback : {2}".format(k,v[2]," ".join([str(i) for i in v[2]])) for k,v in self.SpiEvent.items()]
        return "\n".join(msg+msg2)

    def _threadEvent(self,pin=None, mode=0, endvalue=0):
        egde = self._edge(mode)
        with open("/sys/class/gpio/gpio%i/value" % pin, 'r') as f:
            previous_state = f.read()
            po = select.poll()
            po.register(f, select.POLLPRI)
            while self.PinEvent[pin][1]:
                f.seek(0)
                state = f.read()
                if edge != 3 and state[0] == edge:
                    if endvalue == 0:
                        #fin de la thread
                        self.PinEvent[pin][1] = False
                        keepo = False
                    else:
                        keepo = True
                    self.PinEvent[pin][2].dequeue(keep=keepo)
                elif edge == 3 and state[0] != previous_state:
                    if endvalue == 0:
                        self.PinEvent[pin][1] = False
                        keepo = False
                    else:
                        keepo = True
                    self.PinEvent[pin][2].dequeue(keep=keepo)
                previous_state = state[0]

    def _threadSpi(self,channel,function,callback,value,endvalue):
        while self.SpiEvent[channel][1]:
            self.lockSpi.aquire()
            try:
                retour = function(channel)
            finally:
                self.lockSpi.release()
            if retour > value:
                #Condition de la thread est la do le shit
                #Change la valeur pour etre appeler dans Event_Detect_Spi
                self.SpiEvent[channel][4][0] = True
                self.SpiEvent[channel][4][1] = retour
                if endvalue == 0:
                    #finit la thread
                    self.SpiEvent[channel][1] = False
                    keepo = False
                else:
                    keepo = True
                self.SpiEvent[channel][3].dequeue(keep=keepo)

    def Add_Event(self, pin, mode, callback):
    	#Add a event on a mode like falling to add a event 1 -> 0 and rising form 0 -> 1 or both on a pin
        if not self.PinEvent.__contains__(pin):
            queue = gpioqueue.queue(callback)
            self.PinEvent[pin] = [Thread(target=self._threadEvent,args=(pin,mode)),True,queue, mode]
            self.PinEvent[pin][0].start()

    def Add_Event_Spi(self, channel, function, value, callback, endvalue):        
        if not self.SpiEvent.__contains__(channel):
            queue = gpioqueue.queue(callback)
            self.SpiEvent[channel] = [Thread(target=self._threadSpi,args=(channel,function,queue,value,endvalue)\
                ,name="Thread channel {0}".format(channel)), callback, [False,0]]
            self.SpiEvent[channel][0].start()
            return True
        else:
            return False

    def Delete_Event(self,pin=None):
        if pin is not None and self.PinEvent.__contains__(pin):
            self.PinEvent[pin][1] = False
            del self.PinEvent[pin]
            return True
        return False

    def Delete_Event_Spi(self,channel):
        if channel is not None and self.SpiEvent.__contains__(channel):
            self.SpiEvent[channel[1] = False
            del self.SpiEvent[channel]
            return True
        return False

    def Event_Detected(self,pin=None):
    	#Return True of False depending if the event have occurred since the last call of the function
        if self.PinEvent[pin][4]:
            self.PinEvent[pin][4] = False
            return True
        else:
            return False

    def Event_Detected_Spi(self,channel):
        if self.SpiEvent[channel][0]:
            self.SpiEvent[channel][0] = False
            return True, self.SpiEvent[3][1]
        else
            return False
