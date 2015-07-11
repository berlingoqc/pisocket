# -*- coding: utf-8 -*-
import time
import newgpio
from threading import Thread

class PWM(newgpio.GPIO):
    def __init__(self,pin=None,frequence=0,dutycycle=0):
        self.pinpwm = {"timeHigh": 0.0, "timelow": 0.0, "dutycycle": 0, "timepulse": 0, "isOn": False}
        self.pin = pin
        newgpio.GPIO.__init__({pin:["out","0"]})
        self.Set_Freq(pin, frequence)
        self.Set_Duty_Cycle(pin, dutycycle)
    #Public function

    #override of the start function to also active my bool control value
    def Stop_Thread(self):
    	self.pinpwm["isOn"] = False

    def Start_Thread(self,timeTotal=0):
    	self.dictGPIO[pin]["isOn"] = True
    	Thread(target=self._Thread_pwm,args=(timeTotal)).start()
    
    #set the value of the dutycycle and recall the calculatetime
    def Set_Duty_Cycle(self,dutycycle):
        assert 0.0<=dutycycle<=100.0
        self.pinpwm["dutycycle"] = dutycycle
        self._Calcul_Temps(self.pin)
    #set the value of the frequence and recall the calculatetime
    def Set_Freq(self,frequence):
        assert 0<=frequence
        self.pinpwm["frequence"] = frequence
        self.pinpwm["timePulse"] = 1000.0/frequence
        self._Calcul_Temps(self.pin)
    #Calculate the time the pulse have to stay high and low
    def _Calcul_Temps(self,pin):
        self.pinpwm["timeHigh"] = self.pinpwm["dutycycle"] /100.0 * self.pinpwm["timePulse"]
        self.pinpwm["timeLow"] = self.pinpwm["timePulse"] - self.pinpwm["timeHigh"]
   #my thread
    def _Thread_pwm(self,timeTotal,pin):
        start = time.time()
        time_High = self.pinpwm["timeHigh"]
        time_Low = self.pinpwm["timeLow"]
        dc = self.pinpwm["dutycycle"]
        while self.pinpwm["isOn"]:
            if dc > 0.0:
                self.Set_Value(self.pin,"1")
                time.sleep(time_High/1000.0)
            if dc < 100.0:
                self.Set_Value(self.pin,"0")
                time.sleep(time_Low/1000.0)
            if time.time() - start > timeTotal:
            	self.dictPWM[self.pin]["isOn"] = False

