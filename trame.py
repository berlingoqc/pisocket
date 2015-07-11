# -*- coding: utf-8 -*-
from newgpio import listPinExport, GetDirection
from binascii import hexlify
"""

*** devrait faire un function static qui retourne liste des pins export


#Doit ajouter une classe serveur qui attend une connection de la tablette qui entre en mode controle pour utiliser
#les composants du rasberry pi
#protocol pour init communication : -2 bytes pour les classes ( chaque bit egale une classe pwm, hc, etc... )
									-le reste ces pour toute les pins 1 bytes
#									 6 bits pour le numero de la pin et le 7ieme pour la direction et 8ieme genre pwm ?

	2- Le pi repond un ack ou un nack si nack vient avec code d'erreur
		la reponse du pi va etre sur un port dynamique avec lequel l'application communiquera
						
	3- Par la suite l'application peux envoyer des commandes au pi avec la structure suivant:
								(Reste pour la camera et pour les sensors specifique)first bit: == 1 : Op ecriture sur une pin

				

						   == 2 : Op lecture sur une pin
						   == 3 : Op ecriture sur une pin PWM
						   == 4 : Op lecture sur port SPI 0/1
						   == 5 : Op ajouter item liste queue
						   == 6 : Op retourner item liste queue
						   == 7 : Op dequeue "x" item liste queue
						   == 8 : Op setter un event 
						   == 9 : Op retourner liste item
						   == 10 : Op supprimer un event
									

"""
indicepwm = 0

def _channelorpin(data,retour):
    if (data[2] & 63) > 0:
        #Pin
        return (retour[0], data[2] & 63)
    elif (data[2] & 192) in [64,128,192]:
        #Spi
        if (data[2] & 64) == 64 and (data[2] & 128) == 0:
            return(retour[1], 0)
        elif (data[2] & 64) == 0 and data[2] & 128) == 128:
            return(retour[1], 1)
    pass
def incpwm():
    indicepwm += 1
    return indicepwm

def dec_op_WR(trame):
    #si le deuxieme bytes == 1 wrq ==2 rrq
    #doit rajouter fonction validation pour savoir si la pin est bonne direction
    if trame[1] == 0x01:
        return (1, trame[2] & 63, "1" if trame[2] & 64 == 64 else "0") #if trame[2] & 63 in listPinExport() else 99
    elif trame[1] == 0x02:
        return (2, trame[2] & 63) #if trame[2] & 63 in listPinExport() else 1

def dec_op_ModifPin(trame):
    print(listPinExport)
    print(trame[2]&63)
    return (3, trame[2] & 63, "in" if trame[2] & 64 == 0 else "out", "1" if trame[2] & 128 == 128 else "0") #if trame[2] & 63 in listPinExport() else 1

def dec_op_Pwm(trame):
    # OP CODE , PIN # , FREQUENCE (short), DUTYCYCLE 
    #Retourne le classique et a la fin un handle pour eteindre la thrad
	return (7, trame[2], (trame[3]<<8)+trame[4], trame[5],incpwm()) if trame[2] < 40 else 0

def dec_op_SPI(trame):
    #Retour la valeur du SPI sur le channel 0 ou 1 avec une choix d'option de fonction pour les 7 premier bits 
    # 0 0 0 0  0 0 0 0 bits 0 == channel, bits 1 == Valeur Potentiometre bits 2 == Valeur Analog bits 3 == voltage ..
    a = 1
    for i in range(2,7):
        if (trame[2] & 254) == (1 << i):
            break
        a += 1

    return (5,trame[2]&1,a) else 1


def dec_op_StartEvent(trame):

    # Deux premiers bytes op code
    # troisieme : valeur event ( 0: None 1: Falling 2: rising 3: both) 2 bits
    #            3: 0 == arreter event apres premier execution 1 == continuer ...
    #            si 3 bits sont eteints event sur spi veut dire que ces un
    #            event sur le SPI attend la valeur donné selon le mode choisit
    #
    #
    # Apres suite de commande qui seront execute lorsque l'evenement
    # arrivera chaque commande est separée par x00xFF
    retour = None
    modeEdge = ["none","falling","rising","both"]
    #indice pour demarrer la liste de commande a exectuer
    startindice = 0
    if trame[2] < 4:
        #Event sur une pin
        # retour [0] 0:opcode 1:pin 2: mode(string) 3: continue, 3 ???
        retour = 0, trame[2], modeEdge[trame[3]], True if trame[3]&16==16 else False,3 
    else:
        #Event sur SPI
        #retour [0] 0:opcode, 1:(0:Opcode 1:Channel 2:indice Function ), value sur deux bytes, endvalue
        retour = 1 , dec_op_SPI(trame[3:6]), (trame[7] << 8) + trame[8],
    #Retourne une list de list de commande contenu dans la trame    
    listcommande = dec_ListCommande(trame[startindice:])
    #Construit un dict avec le opcode de la commande et le tuple du retour en valeur
    listFunction = { 1:dec_op_WR,2:dec_op_WR,3:dec_op_ModifPin,5:dec_op_SPI,7:dec_op_Pwm}
    # retour [0] 0:opcode 1:pin 2: mode(string) 3: continue
    return retour, dict([ (cmd[1], listFunction[cmd[1]](cmd)) for cmd in listcommande if listFunction.__contains__(cmd[1]) else (cmd[1], None)])

def dec_op_EventDetected(trame):
    return _channelorpin(trame, (77,78))

def dec_op_StopEvent(trame):
    return _channelorpin(trame, (79,80))

def dec_ListCommande(trame):
    a = []
    l = []
    for i, b in emumerate(trame):
        if b == 255 and trame[i-1] == 0: 
            l.append(a)
            a = []
            continue
        a.append[i]
    return l

def dec_op_GetEventStatus(trame):
    return _channelorpin(trame, (81,82))
def dec_op_DeleteEvent(trame):
    return _channelorpin(trame, (83,84))

def dec_trameInitial(trame):
    if trame[0] != 170 or trame[0] != 0:
        trame = [int(hexlify(i),16) for i in trame]
    classe = ("pwm","spi","queue","event","cam","hc")
    masque = [1,2,4,8,16,32]
    erreurcode = 0
    listclasse = None
    dictPin = None
    #Somme bits = 63
    #liste des classes valides ( position dans le tableau sont egales au bytes qu'il faut allume )
    #Valide si les deux premiers bytes sont AA AA

    if trame[0] == 170 and trame[1] == 170 and trame[3] < 63:
        #Ajoute les classes selons les bytes allumes
        #listclasse = [classe[i] for i in range(len(classe)) if trame[3] & masque[i] == masque[i]]
        listclasse = []
        for i,k in enumerate(masque):
            if trame[3]& k == k:
                listclasse.append(classe[i])
        #Cree dict avec les pin et leurs directions
        #Et verification si la pin n'est pas deja export
        #listpin = tuple(newgpio.listPinExport())
        dictPin = dict((trame[i]&63, ["in" if trame[i]&64 == 64 else "out","1" if trame[i]&128 == 128 else "0"]) for i in range(4, len(trame)) if trame[i]&63 in range(40))
    elif trame[1] == 113:
        erreurcode = 98
    elif trame[0] == 170 and trame[1] == 186:
        #Reconnection au serveur renvoit l'adresse et le port de la thread
        erreurcode == 97
    else:
        erreurcode = 99
    return erreurcode, listclasse, dictPin
