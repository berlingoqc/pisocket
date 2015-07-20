# -*- coding: utf-8 -*-
import time
import newgpio
from threading import Thread

class PWM(newgpio.GPIO,Thread):
    def __init__(self,pin=None,frequence=0,dutycycle=0):
        self.pinpwm = {"timeHigh": 0.0, "timelow": 0.0, "dutycycle": 0, "timepulse": 0, "isOn": False}
        self.pin = pin
        self.Set_Freq(frequence)
        self.Set_Duty_Cycle(dutycycle)
        newgpio.GPIO.__init__(self,{pin:["out","0"]})
        Thread.__init__(self, name="Thread PWM pin :{0}".format(pin))
    #Public function

    #override of the start function to also active my bool control value
    def Stop_Thread(self):
    	self.pinpwm["isOn"] = False

    def Start_Thread(self,timeTotal=0):
    	self.pinpwm["isOn"] = True
    	self.start()
    
    #set the value of the dutycycle and recall the calculatetime
    def Set_Duty_Cycle(self,dutycycle):
        assert 0.0<=dutycycle<=100.0
        self.pinpwm["dutycycle"] = dutycycle
        self._Calcul_Temps()
    #set the value of the frequence and recall the calculatetime
    def Set_Freq(self,frequence):
        assert 0<=frequence
        self.pinpwm["frequence"] = frequence
        self.pinpwm["timePulse"] = 1000.0/frequence
        self._Calcul_Temps()
    #Calculate the time the pulse have to stay high and low
    def _Calcul_Temps(self):
        self.pinpwm["timeHigh"] = self.pinpwm["dutycycle"] /100.0 * self.pinpwm["timePulse"]
        self.pinpwm["timeLow"] = self.pinpwm["timePulse"] - self.pinpwm["timeHigh"]
   #my thread
    def run(self):
        print("Start PWM on pin {0} frequence : {1} dc : {2}".format(self.pin, self.pinpwm["frequence"],self.pinpwm["dutycycle"]))
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
        self.Set_Value(self.pin,"0")
        print("Fin de la thread PWM {0}".format(self.pin))

