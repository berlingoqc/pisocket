from time import sleep

class HC(object):
    def init_HC(self,triggerPin,echoPin):
        self.Setup(triggerPin, "out")
        self.Setup(echoPin, "in")
        self._interrupt(self, echoPin, "both")
        self.trigger = triggerPin
        self.echo = echoPin
        
    def Read_Distance(self):
        v = (331.5 + 0.6 * 20) #the speed of the wave
        path = "/sys/class/gpio/gpio%i/value" % self.trigger
        _write(self,path, "0")
        sleep(0.5)
        
        _write(self,path, "1")
        sleep(1/1000.0/1000.0)
        _write(self,path, "0")
        
        t = Pulse_High(self, self.echo)
        
        d = (t*v) / 2
        return d * 100



