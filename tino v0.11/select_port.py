#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Tino project
# selection du port com

from tkinter import * 
from tkinter import messagebox
import sys
import os.path
#import glob
#import serial
import time
import configparser
import tino_fonctions


def traitement():
    port = liste.get(ACTIVE)
    if not os.path.isfile('tino_config.cfg'):
        tino_fonctions.init_config()
    cfg = configparser.ConfigParser()
    cfg.read('tino_config.cfg')
    cfg.set('Start', 'port', port)
    cfg.write(open('tino_config.cfg','w'))
    messagebox.showinfo("Enregistré", port, icon="info", parent=fenetre)
    time.sleep(1)
    sys.exit()


fenetre = Tk()
label = Label(fenetre, text="Selectionner le port")
label.pack()
li= tino_fonctions.list_serial_ports()

# liste
liste = Listbox(fenetre)
for index, valeur in enumerate(li):
    liste.insert(index, valeur)
liste.pack()

#mise en place du bouton
btn=Button(fenetre, text="Valider", command=traitement)
btn.pack()

fenetre.mainloop()
