import picamera
import io
import time
from fractions import Fraction
from threading import Thread, Lock

class PiCamera(object):
    """
    type inclure photo : file(jpeg...),stream,PIL,OpenCV,timelapse,fast,networkstream,overlapping,lowlightt
                 video : file,stream,multiplefile,circularstream,networkstream, overlapping
    """
    def __init__(self,**kargs):
        self.lockCam = Lock()
        self.name = "image"
        self.typeImg = ".jpg"
        self.cam = picamera.PiCamera()
    def _threadCapture(self,nbr,tl,nom,typeImg):
        for i in range(nbr):
            self.lockCam.acquire()
            try:
                self.cam.start_preview()
                time.sleep(1)
                self.cam.capture((nom + "%i" % i + typeImg))
            finally:
                self.cam.stop_preview()
                print((nom + "%i" % i + typeImg)) 
                self.lockCam.release()          
            if i == nbr-1:
                break
            time.sleep(tl)
    #Fonction Public
    def Capture(self):
        self.lockCam.acquire()
        try:
            self.cam.start_preview()
            time.sleep(1)
            self.cam.capture((self.name + self.typeImg))
        finally:
            self.lockCam.release()
    def Consistence_Sequence_Capture(self,nbr):
        assert 0<nbr
        self.lockCam.acquire()
        try:
            self.cam.capture_sequence([(self.name + "%i" % i + self.typeImg) for i in range(nbr)])
        finally:
            self.lockCam.release()

    def TimeLapse_Capture(self,nbrPhoto,timelapse):
        assert 0<nbrPhoto
        assert 0<timelapse

        Thread(target=self._threadCapture,args=(nbrPhoto,timelapse,self.name,self.typeImg)).start()
        """ICI toute les fonctions qui ne font que changer params """
    #Assigne les bonnes valeurs a la cam pour permettre meilleu qualiter photo low light
    def Low_Light(self):
        #Set the camera to the wrigth value to take good low light photo
        dictLow = {"resolution":(1280,720),"framerate":Fraction(1,6),"shutter_speed":6000000,"exposure_mode":'off',"iso":800}
        self._activeparams(dictLow)
    #Fonction appeller pour configuer la camera avant de prendre des photos en boucle 
    def Consistent_Mode(self):
        #Wait for analog gain to settle on a higher value than 1
        while self.cam.analog_gain <= 1:
            time.sleep(0.1)
        #Now fixe the values for the consistent image
        dictConststent = {"shutter_speed":self.cam.exposure_speed,"exposure_mode":'off'}
        self._activeparams(dictConststent)
        g = self.cam.awb_gains
        self.cam.awb_mode = 'off'
        self.cam.awb_gains = g

        




