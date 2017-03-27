import os.path
import pickle
import serial
from serial import SerialException
import time
import sys
import glob
import configparser

def wait_card():
    # ici on se connect à l'arduino et on récupère un UID de carte rfid
    ser = serial.Serial(
        port='COM4',\
        baudrate=9600,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=0)
    joined_seq_vu=""
    continuer = 1
    seq = []
    while continuer:
        for c in ser.read():
            seq.append(chr(c))
            joined_seq = ''.join(str(v) for v in seq[:-2])
            if chr(c) == '\n' :
                if joined_seq.startswith("c:") and joined_seq_vu!=joined_seq:
                    idcard = joined_seq[2:len(joined_seq)]
                    print (idcard)
                    joined_seq_vu=joined_seq
                seq = []
                continuer = False
                break
    ser.close()
    return idcard

def wait_distance():
    #ici tout le code qui dire si la distance est inférieure à x cm
    # TO DO
    distance = True

def connect_tino(p):
    # ici on se connect à l'arduino
    # todo : tester la version de tinocore (que l'arduino enverrait à l'initialisation)
    try:
        c = serial.Serial(
            port=p,\
            baudrate=9600,\
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
            timeout=0)
    except SerialException:
        print ("Communication avec Tino non effectuée")
        time.sleep(5)
        sys.exit()
    print("Connecté à Tino sur : " + c.portstr)
    return c

def list_serial_ports():
    # retourne la liste des noms des ports series disponibles sur le système
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Système non supporté')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def init_config():
    # fonction que l'on appelle si le fichier tino_config.cfg n'existe pas
    cfg = configparser.ConfigParser()
    cfg.add_section('Start')
    cfg.add_section('Messages')
    cfg.add_section('Horaires')
    S = 'Start'
    cfg.set(S, 'port', 'COMX')
    cfg.set(S, 'distance', '10')
    S = 'Messages'
    cfg.set(S, 'question', 'Que veux-tu ?')
    S = 'Horaires'
    cfg.set(S, 'debut_classe', '830')
    cfg.set(S, 'fin_classe', '1600')
    cfg.set(S, 'debut_recree', '1000')
    cfg.set(S, 'fin_recree', '1020')
    cfg.set(S, 'debut_midi', '1200')
    cfg.set(S, 'fin_midi', '1330')
    cfg.set(S, 'debut_recree_am', '1500')
    cfg.set(S, 'fin_recree_am', '1520')
    cfg.write(open('tino_config.cfg','w'))
    #pas besoin de fermer car ConfigParser le fait tout seul (je crois)

def plage_horaire():
    # établit le moment de la journée, dans la variable dis_moment
    heure_courante = int(time.strftime("%H%M"))
    cfg = configparser.ConfigParser()
    cfg.read('tino_config.cfg')
    debut_classe = int(cfg['Horaires']['debut_classe'])
    fin_classe = int(cfg['Horaires']['fin_classe'])
    debut_recree = int(cfg['Horaires']['debut_recree'])
    fin_recree = int(cfg['Horaires']['fin_recree'])
    debut_midi = int(cfg['Horaires']['debut_midi'])
    fin_midi = int(cfg['Horaires']['fin_midi'])
    debut_recree_am = int(cfg['Horaires']['debut_recree_am'])
    fin_recree_am = int(cfg['Horaires']['fin_recree_am'])
    if heure_courante > debut_classe and heure_courante < debut_recree :
        moment_journee = "Nous sommes le matin, avant la récréation"
    elif heure_courante >= debut_recree and heure_courante < fin_recree :
        moment_journee = "C'est la récréation"
    elif heure_courante >= fin_recree and heure_courante < debut_midi :
        moment_journee = "Nous sommes le matin, après la récréation"
    elif (debut_midi - heure_courante) < 60 and (debut_midi - heure_courante) > 0 :
        moment_journee = "Il est presque midi"
    elif heure_courante >= debut_midi and heure_courante < fin_midi :
        moment_journee = "C'est l'heure de la pause de midi"
    elif heure_courante >= fin_midi and heure_courante < debut_recree_am :
        moment_journee = "Nous sommes l'après-midi, avant la récréation"
    elif heure_courante >= debut_recree_am and heure_courante < fin_recree_am :
        moment_journee = "C'est la récréation"
    elif heure_courante >= fin_recree_am and heure_courante < fin_classe :
        moment_journee = "Nous sommes l'après-midi, après la récréation"
    elif (fin_classe - heure_courante) < 60 and (fin_classe - heure_courante) > 0 :
        moment_journee = "La journée de classe est presque terminée"
    else :
        moment_journee = "Ce n'est pas le moment de l'école"
    return moment_journee

def init_data(d):
    #initialisation d'un fichier de base de données serialisée avec pickle
    c = {}
    if os.path.isfile(d):
        if os.path.getsize(d) == 0:
            with open(d, 'wb') as fichier:
                mon_pickler = pickle.Pickler(fichier)
                mon_pickler.dump(c)
        with open(d, 'rb') as fichier:
            mon_depickler = pickle.Unpickler(fichier)
            c = mon_depickler.load()
            fichier.close()
    else:
        file = open(d, "w")
        print('fichier', d ,'créé')
        with open(d, 'wb') as fichier:
            mon_pickler = pickle.Pickler(fichier)
            mon_pickler.dump(c)
            fichier.close()
    return c
