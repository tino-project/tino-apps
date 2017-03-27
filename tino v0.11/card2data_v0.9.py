#Tino project by Cédric Couvrat
#card2data
#permet d'assigner une fonction et un nom aux cartes RFID
#--------------------------------------------------------
#0.8 : on remet de l'odre dans l'algo ! compatble avec bonjour >= 0.11
#0.7 : on utilise des fonctions pour la lisibilité et la réutilisabilité
#0.6 : config dans un seul fichier avec configparser
#0.5 : on verifie si le fichier port existe
#0.4 : on va chercher le port dans un fichier de config (port.txt)
#0.3 : on propose de classer les cartes par catégories
#------au départ on teste en plus si le fichier est vide
#------on sort proprement si la connexion avec Tino n'est pas effectuée
#0.2 : prévient si une carte est déjà enregistré 

# Import des bibliothèques
import sys
import time
import configparser
import pickle #pour ecrire des objets dans un fichier
import os.path #pour la gestion des fichiers et des répertoires
import serial #serial pour lire et communiquer avec Arduino
from serial import SerialException
import tino_fonctions

# Variables globales

# Config
if not os.path.isfile('tino_config.cfg'):
    tino_fonctions.init_config()
    exec(compile(open("select_port.py", "rb").read(), "select_port.py", 'exec'))
cfg = configparser.ConfigParser()
cfg.read('tino_config.cfg')
monport=cfg['Start']['port']  

# Connexion Arduino
ser = tino_fonctions.connect_tino(monport)

# Initialisation des données cartes
card = tino_fonctions.init_data("card_db")

okPourLire = 1;
while okPourLire == 1:
    print ("Présentez une carte")
    ser.reset_input_buffer()
    seq = []
    readSer=True
    while readSer:
        for c in ser.read():
            seq.append(chr(c)) #append ajoute chaque ligne reçue par ser.read au tableau seq
            joined_seq = ''.join(str(v) for v in seq) #fabrique la chaine (joined_seq) à partir du tableau (seq)
            if chr(c) == '\n':
                if joined_seq.startswith("c:"):
                    idcard = joined_seq[2:len(joined_seq)]# on enlève les 2 premiers caractères
                    idcard = idcard[:-2]
                    print ("Le n° de la carte est : ", idcard)
                    with open('card_db', 'rb') as fichier:
                        ma_list = pickle.Unpickler(fichier)
                        n = ma_list.load()
                        if idcard in n:
                            print("- cette carte existe")
                            print("- nom :", n[idcard]['nom'])
                            print("- catégorie :", n[idcard]['cat'])
                        else:
                            print("- nouvelle carte")
                    nom = input("Entrez un nom : ")
                    cat = input("Entrez une catégorie (ex:prenom)(peut être vide) : ")
                    maj = {'nom':nom,'cat':cat}
                    #print (maj)
                    with open('card_db', 'wb') as fichier:
                        mon_pickler = pickle.Pickler(fichier)
                        card[idcard]=maj
                        mon_pickler.dump(card)
                        fichier.close()
                        with open('card_db', 'rb') as fichier:
                            ma_list = pickle.Unpickler(fichier)
                            n = ma_list.load()
                            #print("- Données enregistrées : ", n)
                            print("- Données enregistrées.")
                        suite = input("- q pour quitter, autre touche pour continuer: ")
                        if suite == "q":
                            okPourLire = 0;
                            ser.close()
                            print("C'est fini, vous pouvez fermer cette fenêtre")
                        else:
                            okPourLire = 1;
                    readSer=False
                seq = []
