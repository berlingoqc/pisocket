
import time
from threading import Thread

class PWM(object):
    def Init_PWM(self,pin=None,frequence=0,dutycycle=0):
        if not self.dictGPIO.__contains__(pin):
            self._export(self,pin)
        self.dictGPIO[pin] = {"timeHigh": 0.0, "timelow": 0.0, "dutycycle": 0, "timepulse": 0, "isOn": False}
        self.Setup(pin, "out")
        self.Set_Freq(pin, frequence)
        self.Set_Duty_Cycle(pin, dutycycle)

    #Public function

    #override of the start function to also active my bool control value
    def Stop_Thread(self,pin):
    	if self._checkpin(pin):
    		self.dictGPIO[pin]["isOn"] = False
    def Start_Thread(self,pin,timeTotal=0):
    	if self._checkpin(pin):
    		self.dictGPIO[pin]["isOn"] = True
    		Thread(target=self._Thread_pwm,args=(timeTotal,pin)).start()
    #set the value of the dutycycle and recall the calculatetime
    def Set_Duty_Cycle(self,pin,dutycycle):
        assert 0.0<=dutycycle<=100.0
        self.dictGPIO[pin]["dutycycle"] = dutycycle
        self._Calcul_Temps(pin)
    #set the value of the frequence and recall the calculatetime
    def Set_Freq(self,pin,frequence):
        assert 0<=frequence
        self.dictGPIO[pin]["frequence"] = frequence
        self.dictGPIO[pin]["timePulse"] = 1000.0/frequence
        self._Calcul_Temps(pin)

    #Private function
    def _checkpin(self,pin):
    	if self.dictGPIO.__contains__(pin):
    		return True
    	else:
    		return False
    #Calculate the time the pulse have to stay high and low
    def _Calcul_Temps(self,pin):
        self.dictGPIO[pin]["timeHigh"] = self.dictGPIO[pin]["dutycycle"] /100.0 * self.dictGPIO[pin]["timePulse"]
        self.dictGPIO[pin]["timeLow"] = self.dictGPIO[pin]["timePulse"] - self.dictGPIO[pin]["timeHigh"]
   #my thread
    def _Thread_pwm(self,timeTotal,pin):
        start = time.time()
        time_High = self.dictGPIO[pin]["timeHigh"]
        time_Low = self.dictGPIO[pin]["timeLow"]
        dc = self.dictGPIO[pin]["dutycycle"]
        while self.dictGPIO[pin]["isOn"]:
            if dc > 0.0:
                self.Set_Value(pin,"1")
                time.sleep(time_High/1000.0)
            if dc < 100.0:
                self.Set_Value(pin,"0")
                time.sleep(time_Low/1000.0)
            if time.time() - start > timeTotal:
            	self.dictPWM[pin]["isOn"] = False

