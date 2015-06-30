import mycam
import metagpio
from time import sleep

myled = metagpio.Object_GPIO("Queue","Event","PWM",pinRouge=4,pinJaune=3,pinVerte=2)
mycamera = mycam.PiCamera()

mycamera.name = "/home/pi/yolop"
mycamera.cam.rotation = 90
mycamera.cam.brightness = 70

myled.Init_PWM(pin=4,frequence=2,dutycycle=50)
myled.Init_PWM(pin=3,frequence=2,dutycycle=50)
myled.Init_PWM(pin=2,frequence=2,dutycycle=50)

mycamera.TimeLapse_Capture(3,10)


myled.Start_Thread(4,timeTotal=30)
sleep(1.5)
myled.Start_Thread(3,timeTotal=30)
sleep(0.75)
myled.Start_Thread(2,timeTotal=30)




