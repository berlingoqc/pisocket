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
    return (5,trame[1]&1,(trame[1]&254)/2) if trame[1]&254 in [4,8,26,32,64,128] else 1

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
    else:
        erreurcode = 99
    return erreurcode, listclasse, dictPin
