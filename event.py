from threading import Thread
import select

class Event(object):
    def init_Event(self):
        self.thPin = {}
        self.thValue = {}

    def _threadEvent(self,pin=None,mode="none"):
        endvalue = self._edge(mode)
        with open("/sys/class/gpio/gpio%i/value" % pin, 'r') as f:
            previous_state = f.read()
            po = select.poll()
            po.register(f, select.POLLPRI)
            while self.thPin[pin]:
                f.seek(0)
                state = f.read()
                if endvalue != 2 and state[0] == endvalue:
                    self.thValue[pin] = True
                elif endvalue == 2 and state[0] != previous_state:
                    bLoop = True
                    previous_state = state[0]

    def Add_Event(self, pin=None, mode="none"):
    	#Add a event on a mode like falling to add a event 1 -> 0 and rising form 0 -> 1 or both on a pin
        self.thPin[pin] = True
        self.thValue[pin] = False
        Thread(target=self._threadEvent,args=(pin,mode)).start()

    def Delete_Event(self,pin=None):
        self.thPin[pin] = False

    def Event_Detected(self,pin=None):
    	#Return True of False depending if the event have occurred since the last call of the function
        if self.thValue[pin]:
            self.thValue[pin] = False
            return True
        else:
            return False
