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
        self.objectgpio = Object_GPIO(listclasse, dictPin)
        self.adr = (adr[0], 1996)
        Thread.__init__(self, name="Thread Serveur object {0}".format(adr[0]))

    def finish(self):
        self.sortit = False

    
    def run(self):
        print("Thread Ecoute pour serveur object")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
            #trame.dec_Message(data)
            if data[1] < 7:
                if data[1] == 1:
                    print("Write")
                    retour = trame.dec_op_WR(data)
                    self.objectgpio.Set_Value(retour[1],retour[2])
                    sock.sendto(b'\x00\x71',self.adr)
                elif data[1] == 2:
                    print("read")
                    retour = trame.dec_op_WR(data)
                    valeur = self.objectgpio.Get_Value(retour[1])
                    #opcode de retour de valeur de pin
                    sock.sendto(b'\x00\x51' + (b'\x01' if valeur == "1" else b'\x00'), self.adr)
                elif data[1] == 3:
                    print("Setup")
                    retour = trame.dec_op_ModifPin(data)
                    print(retour)
                    self.objectgpio.Setup({retour[1]:[retour[2],retour[3]]})
                    sock.sendto(b'\x00\x71',self.adr)
                elif data[1] == 5:
                    print("SPI")
                    retour = trame.dec_op_SPI(data)
                    #option = [None, self.objectgpio.ReadPotentiometer, self.objectgpio.Read_Analog, self.objectgpio.Get_Voltage]
                    #valeur = option[retour[2]](retour[1])
                    valeur = 1024
                    sock.sendto(b'\x00\x52' + struct.pack(">H", valeur), self.adr)
                elif data[1] == 6:
                    print("Unexport")
                    self.objectgpio._unexport(data[2])
                    sock.sendto(b'\x00\x71',self.adr)
                elif data[1] == 7:
                    print("Start PWM")
                    retour = trame.dec_op_Pwm(data)
                    
                
            elif data[1] == 98:
                print("fin de la communication")
                sock.sendto(b'\x00\x71',self.adr)
                sortit = False
                self.objectgpio.Clean_All()
            else:
                sock.sendto(b'\x00\x72',self.adr)
        sock.close()

Server()
