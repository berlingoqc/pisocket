# -*- coding: utf-8 -*-
import newgpio
import pwm
import messagebox
#import spi
#import mycam
import gpioqueue
import event
import hc
import trame
import socket
import struct
import sys
from threading import Thread
from binascii import hexlify

def Object_GPIO(args, kargs):
    listClass = {"pwm": pwm.PWM, "spi": None, "queue": gpioqueue.Queue, "hc": hc.HC, "event": event.Event}
    x = [newgpio.GPIO]
    x += [listClass[i] for i in args if listClass.__contains__(i)]
    #Return the instant of a object with the chosen class and with the pins to initialize in kargs
    return type("GPIO", tuple(x), dict())(kargs)

class Server(Thread):

    def __init__(self):
        print("Jecoute sur le port 1995")
        self.listObject = {}
        Thread.__init__(self)
        self.start()
        self.i = 0

    def id_obj(self):
        self.i += 1
        return self.i

    def run(self):
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
                indice = self.id_obj()
                print("Demarre ServerObject avec handle : {0}".format(indice))
                self.listObject[indice] = ServerObject(tramedec[1], tramedec[2], retour[1], indice)
            elif tramedec[0] == 97:
                print("Reconnection object {0}".format(tramedec[1]))
                #Demande au serveur object d'envoyer un msg au client pour qu'il sache le port
                if self.listObject.__contains__(tramedec[1]):
                    self.listObject[tramedec[1]].adr = (retour[1][0],1996)
                    self.listObject[tramedec[1]].ACK()
                else:
                    #Handle pas dans le dictionnaire
                    sock.sendto(b'\x00\x72',retour[1])
            elif tramedec[0] == 99:
                #erreur dans le opcode de la  trame
                print("fermeture serveur")
                sortit = False
                sock.sendto(b'\x00\x71',(retour[1][0],1996))
                for k,v in self.listObject.items():
                    if v.is_alive():
                        print("closing a thread handle {}".format(k))
                        v.sortit = False
        sock.close()
        
        
class ServerObject(Thread):

    def __init__(self, listclasse, dictPin, adr, idobj):
        print(dictPin)
        print("handle : {}".format(idobj))
        self.sortit = True
        self.MB = messagebox.MessageBox()
        self.ClientConnect = [True, idobj]
        self.dictpwm = {}
        self.gpio = newgpio.GPIO(dictPin)
        self.event = event.Event()
        #self.objectgpio = Object_GPIO(listclasse, dictPin)
        self.adr = (adr[0], 1996)
        self.function = {1:self.write,2:self.read,3:self.setup,5:self.spi,\
                         4:self.unexport,7:self.start_pwm,\
        8:self.stop_pwm,17:self.start_event,18:self.get_event_detected,19:self.stop_event,97:self.fermeture_client,98:self.stop_server}
        Thread.__init__(self)
        self.start()

    def finish(self):
        self.sortit = False

    def Get_Bind_Adr(self):
        return self.sock.getsockname()

    def CloseThreadPwm(self, pin):
        if self.dictpwm.__contains__(pin):
            self.dictpwm[pin].Stop_Thread()
            return 0
        else:
            # handle invalide
            return 1

    def write(self, data):
        print("Write")
        retour = trame.dec_op_WR(data)
        self.gpio.Set_Value(retour[1],retour[2])
        self.ACK()

    def read(self, data):
        print("read")
        retour = trame.dec_op_WR(data)
        valeur = self.gpio.Get_Value(retour[1])
        #opcode de retour de valeur de pin
        self.sock.sendto(b'\x00\x51' + (b'\x01' if valeur == "1" else b'\x00'), self.adr)

    def setup(self, data):
        print("Setup")
        retour = trame.dec_op_ModifPin(data)
        print(retour)
        self.gpio.Setup({retour[1]:[retour[2],retour[3]]})
        self.ACK()

    def spi(self, data):
        retour = trame.dec_op_SPI(data)
        #option = [None, self.objectgpio.ReadPotentiometer, self.objectgpio.Read_Analog, self.objectgpio.Get_Voltage]
        #valeur = option[retour[2]](retour[1])
        valeur = 1024
        self.sock.sendto(b'\x00\x52' + struct.pack(">H", valeur), self.adr)

    def unexport(self, data):
        print("Unexport")
        self.gpio._unexport(data[2])
        self.ACK()
        
    def start_pwm(self, data):
        print("Start PWM")
        retour = trame.dec_op_Pwm(data)
        self.dictpwm[retour[1]] = pwm.PWM(retour[1],retour[2],retour[3])
        #Demarre la thread
        self.dictpwm[retour[1]].Start_Thread()
        #Renvoit le retour au client avec le handle pour refermer le pwm
        self.ACK()

    def stop_pwm(self, data):
        print("Fermeture thread pwm")
        #Op code pour refermer une thread pwm
        if self.CloseThreadPwm(data[2]) == 0:
            print("Thread Fermer")
            self.ACK()
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
            else:
                self.sock.sendto(b'\x00\x50',self.adr)
        elif retour[0] == 78:
            if self.event.Event_Detected_Spi():
                self.sock.sendto(b'\x00\x56',self.adr)
            else:
                self.sock.sendto(b'\x00\x50',self.adr)



    def stop_event(self, data):
        retour = trame.dec_op_StopEvent(data)
        if retour[0] == 77:
            event.Delete_Event(retour[1])
            self.ACK()
        elif retour[0] == 78:
            event.Delete_Event(retour[1])
            self.ACK()

    def stop_server(self, data):
        print("fin de la communication")
        self.ACK()
        sortit = False
        self.gpio.Clean_All()

    def fermeture_client(self, data):
        #Le client se ferme donc maintenant impossible de le rejoindre sur son port
        #donc on doit mettre les alertes des events et autres dans la message box
        self.ClientConnect[0] = False
        a = b'\x00\x71' + struct.pack(">b",self.ClientConnect[1])
        self.sock.sendto(a,self.adr)


    def OpCodeNonValide(self):
        #Renvoye message au client pour dire que l'opcode n'est pas valide
        
        pass
    
    def NACK(self):
        sock.sendto(b'\x00\x72', self.adr)

    def ACK(self):
        self.sock.sendto(b'\x00\x71', self.adr)

    def run(self):
        print("Thread Ecoute pour serveur object")
        print(self.adr)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0",0))
        self.sock.settimeout(2)
        self.ACK()

        while self.sortit:
            try:
                data = self.sock.recv(516)
            except EOFError:
                sortit = False
            except socket.timeout:
                continue
            if type(data[0]) is not int:
                data = [int(hexlify(i),16) for i in data]
            print(data)
            if self.function.__contains__(data[1]):
                print(self.function[data[1]])
                #Partit OPCODE pour commande de bases
                self.function[data[1]](data)
            else:
                print(" OPCODE de la commande recu est invalide")
        self.sock.close()
        print("Object Terminer")

monserver = Server()
monserver.join()
