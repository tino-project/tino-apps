#Tino project by Cédric Couvrat
#Bonjour
#0.11 : on met l'algo principal dans un ordre plus compréhensible ! attention nécessite card2data 0.9
#0.10 : on ajoute la fonction de repère temporel
#0.9 : on sait envoyer des données par serie à l'arduino
#0.8 : utilisation du typage de données pour différencier ce qui est envoyé par arduino
#----- on attend 2 distances pour déclancher la question
#0.7 : on fait des fonctions pour la lisibilité et la réutilisabilité
#0.6 : config dans un seul fichier avec configparser
#0.5 : la base de données permet de catégoriser les cartes (cf card2data.v0.3)
#----- on teste la présence du fichier "donnes"
#----- on sort proprement si la connexion avec Tino n'est pas effectuée
#----- on va chercher le port dans un fichier texte
#0.4 : les prénoms sont stockés dans une base de données (cf card2data)
#0.3 : les prénoms sont dans un tableau
#0.2 : on empêche qu'une carte soit présentée 2 fois de suite


# Import de librairies
#import sys
import configparser
import time
from datetime import datetime
import serial
from serial import SerialException
import os.path
import win32com.client
speaker = win32com.client.Dispatch("SAPI.SpVoice")
import tino_fonctions

# Variables globales
seq = []
vu = False
joined_seq_vu=""
jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
today = jours[time.localtime()[6]]
now = datetime.now()
moment_journee = tino_fonctions.plage_horaire()

# Config
if not os.path.isfile('tino_config.cfg'):
    tino_fonctions.init_config()
    exec(compile(open("select_port.py", "rb").read(), "select_port.py", 'exec'))
cfg = configparser.ConfigParser()
cfg.read('tino_config.cfg')
monport=cfg['Start']['port']
distance=int(cfg['Start']['distance'])
question=cfg['Messages']['question']

# Connexion Arduino
ser = tino_fonctions.connect_tino(monport)

# Initialisation des données cartes
card = tino_fonctions.init_data("card_db")

# On est prêt !      
speaker.Speak("Tino, Module Bonjour  initialisé.")
print ("Il est ",now.hour," h", now.minute)
print (moment_journee)

continuer = 1
i = 0
while continuer:
    for c in ser.read():
        seq.append(chr(c)) # ajout chaque ligne reçue depuis ser.read à notre tableau seq
        joined_seq = ''.join(str(v) for v in seq[:-2]) #fabrique chaine à partir d'un tableau
        if chr(c) == '\n' :
            ser.reset_input_buffer()
            if joined_seq.startswith("c:"):
                #c'est une carte
                for key in card.keys():
                    idcard = joined_seq[2:len(joined_seq)]# on enlève les 2 premiers caractères
                    if idcard == key and joined_seq_vu!=joined_seq:
                        print(card[key]['nom'])
                        dire = card[key]['nom']
                        if card[key]['cat']=="prenom":
                            dire = "Bonjour",card[key]['nom']
                        elif card[key]['nom']=="triste":
                            ser.write(b'triste\n')
                            dire = ""
                        elif card[key]['nom']=="neutre":
                            ser.write(b'neutre\n')
                            dire = ""
                        elif card[key]['nom']=="sourir":
                            ser.write(b'sourir\n')
                            dire = ""
                        elif card[key]['nom']=="bee":
                            ser.write(b'bee\n')
                            dire = ""
                        elif card[key]['cat']=="jour":
                            if card[key]['nom']==today:
                                dire = "Nous sommes",card[key]['nom']
                            else:
                                dire = "Nous ne sommes pas",card[key]['nom']
                        else:
                            dire = card[key]['nom']
                        speaker.Speak(dire)
                        joined_seq_vu=joined_seq
                        vu = False
            if joined_seq.startswith("d:"):
                #c'est une distance
                dist = joined_seq[2:len(joined_seq)]
                if int(dist,16) < distance and not vu:
                    i += 1
                    if i > 1:
                        ser.write(b'vu\n')
                        print (question)
                        speaker.Speak(question)
                        joined_seq_vu=""
                        vu=True
                else:
                    i = 0
            seq = [] #on vide le tableau
