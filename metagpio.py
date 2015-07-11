# -*- coding: utf-8 -*-
import newgpio
import pwm
#import spi
#import mycam
import gpioqueue
import event
import hc
import trame
import socket
import struct
from threading import Thread
from binascii import hexlify

def Object_GPIO(args, kargs):
    listClass = {"pwm": pwm.PWM, "spi": None, "queue": gpioqueue.Queue, "hc": hc.HC, "event": event.Event}
    x = [newgpio.GPIO]
    x += [listClass[i] for i in args if listClass.__contains__(i)]
    #Return the instant of a object with the chosen class and with the pins to initialize in kargs
    return type("GPIO", tuple(x), dict())(kargs)

class Server(object):

    def __init__(self):
        print("Jecoute sur le port 1995")
        Thread(target=self.ecoute, args=()).start()
        
    def ecoute(self):
        activethread = []
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #ecoute sur le port 1995
        sock.bind(("0.0.0.0", 1995))
        sortit = True
        while sortit:
            try:
                retour = sock.recvfrom(516)
                print("Data receive on socket")
            except socket.timeout:
                print("timeoute on continue")
                continue
            print(retour)
            tramedec = trame.dec_trameInitial(retour[0])
            if tramedec[0] == 0:
                #demarre la thread qui utilisera cette object
                print("Demarre ServerObject")
                th = ServerObject(tramedec[1], tramedec[2], retour[1])
                th.start()
                activethread.append(th)
            else:
                #erreur dans le opcode de la  trame
                print("fermeture serveur")
                sortit = False
                sock.sendto(b'\x00\x71',(retour[1][0],1996))
                for i in activethread:
                    if i.is_alive():
                        print("closing a thread")
                        i.finish()
        sock.close()

class ServerObject(Thread):

    def __init__(self, listclasse, dictPin, adr):
        print(listclasse)
        print(dictPin)
        self.sortit = True
        self.dictpwm = {}
        self.event = event.Event()
        self.sock = None
        self.objectgpio = Object_GPIO(listclasse, dictPin)
        self.adr = (adr[0], 1996)
        self.function = {1:write,2:read,3:setup,5:spi,4:unexport,7:start_pwm,16:stop_pwm,98:stop_server}
        Thread.__init__(self, name="Thread Serveur object {0}".format(adr[0]))

    def finish(self):
        self.sortit = False

    def CloseThreadPwm(handle):
        if self.dictpwm.__contains__(handle):
            self.dictpwm[handle].Stop_Thread()
            return 0
        else:
            # handle invalide
            return 1

    def write(self, data):
        print("Write")
        retour = trame.dec_op_WR(data)
        self.objectgpio.Set_Value(retour[1],retour[2])
        self.ACK()

    def read(self, data):
        print("read")
        retour = trame.dec_op_WR(data)
        valeur = self.objectgpio.Get_Value(retour[1])
        #opcode de retour de valeur de pin
        self.sock.sendto(b'\x00\x51' + (b'\x01' if valeur == "1" else b'\x00'), self.adr)

    def setup(self, data):
        print("Setup")
        retour = trame.dec_op_ModifPin(data)
        print(retour)
        self.objectgpio.Setup({retour[1]:[retour[2],retour[3]]})
        self.ACK()

    def spi(self, data):
        retour = trame.dec_op_SPI(data)
        #option = [None, self.objectgpio.ReadPotentiometer, self.objectgpio.Read_Analog, self.objectgpio.Get_Voltage]
        #valeur = option[retour[2]](retour[1])
        valeur = 1024
        self.sock.sendto(b'\x00\x52' + struct.pack(">H", valeur), self.adr)

    def unexport(self, data):
        print("Unexport")
        self.objectgpio._unexport(data[2])
        self.sock.sendto(b'\x00\x71',self.adr)

    def start_pwm(self, data):
        print("Start PWM")
        retour = trame.dec_op_Pwm(data)
        self.dictpwm[retour[4]] = pwm.PWM(retour[1],retour[2],retour[3])
        #Demarre la thread
        self.dictpwm[retour[4]].Start_Thread()
        #Renvoit le retour au client avec le handle pour refermer le pwm
        self.sock.sendto(b'\x00\x53' + struct.pack(">B", str(retour[4])), self.adr)

    def stop_pwm(self, data):
        print("Fermeture thread pwm")
        #Op code pour refermer une thread pwm
        if self.CloseThreadPwm(data[2]) == 0:
            print("Thread Fermer")
            self.sock.sendto(ACK, self.adr) 
        else:
            print("Mauvais handle")
            self.sock.sendto(NACK, self.adr)

    def start_event(self, data):
        retour = trame.dec_op_StartEvent(data)
        if retour[0][0] == 0:
            #Event Edge
            self.event.Add_Event(pin=retour[1],mode=retour[2])
            self.ACK()
        elif retour[0][0] == 1:
            #Event spi
            #channel, function, value, callback, endvalue
            self.event.Add_Event_Spi(retour[0][1][1],retour[0][1][2]\
                ,retour[0][2],retour[1],retour[0][3])
            self.ACK()

    def get_event_detected(self, data):
        retour = trame.dec_op_EventDetected(data)
        if retour[0] == 77:
            if self.event.Event_Detected():
                #Send True return
                self.sock.sendto(b'\x00\x55',self.adr)
        elif retour[0] == 78:
            if self.event.Event_Detected_Spi() 


    def stop_event(self, data):
        retour = trame.dec_op_StopEvent(data)
        if retour[0] == 77:
            event.Delete_Event(retour[1]))
            self.ACK()
        elif retour[0] == 78:
            event.Delete_Event(retour[1])
            self.ACK()

    def stop_server(self, data):
        print("fin de la communication")
        self.sock.sendto(b'\x00\x71',self.adr)
        sortit = False
        self.objectgpio.Clean_All()

    def NACK(self):
        sock.sendto(b'\x00\x72', self.adr)

    def ACK(self):
        self.sock.sendto(b'\x00\x71', self.adr)

    def run(self):
        print("Thread Ecoute pour serveur object")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0",0))
        sock.settimeout(2)

        #ack
        sock.sendto(b'\x00\x71', self.adr)
        print("Ack send")

        while self.sortit:
            try:
                data = sock.recv(516)
            except EOFError:
                sortit = False
            except socket.timeout:
                continue
            data = [int(hexlify(i),16) for i in data]
            print(data)
            
            #Partit OPCODE pour commande de bases
            self.function[data[1]](data) if self.function.__contains__(data[1]) else None

        sock.close()

Server()
