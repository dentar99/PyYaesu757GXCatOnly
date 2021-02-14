#!/usr/bin/python3
#
# Author: Tom N4LSJ -- EXPERIMENTAL CODE ONLY FOR TINKERING
#                   -- USE AT YOUR OWN RISK ONLY
#                   -- AUTHOR ASSUMES NO LIABILITY
# 
# Yaesu FT757-GX-1 program
# 
# This program works for the FT-757GX -MARK 1- only.  The MK2 programming is
# not quite the same, so don't be surprised if this doesn't work as expected
# on the MK2
# 
# I used a USB-to-RS232 serial hooked to an RS232-to-TTL which hooked to 
# the Rig.  Look out, DCE vs. DTE -might- mean you wire RX to RX instead of
# TX to RX on the TTL side.  I had to wire RX to RX.  Do not wire RS-232 
# straight to the rig. The rig needs TTL level signaling, meaning 2.7 to 5 V
# and no more.
#
# You can also use the Pi's GPIO pins, which is what I switched to later on.
# They appear to safely drive the Yaesu, despite their supposedly being
# only 3.3v
#

# DATA BYTE:
# | START BIT | D0 | D1 | D2 | D3 | D4 | D5 | D6 | D7 | STOP BIT | STOP BIT |

# 5 BYTE BLOCK COMMAND
# | PARM 4 (LSD) | PARM 3 | PARM 2 | PARM 1 | INSTRUCTION (MSD) |

import datetime
DEBUGTS=datetime.datetime.utcnow()

import time
import serial

from tkinter import *
from tkinter.simpledialog import askstring
from tkinter.simpledialog import askinteger
from tkinter.simpledialog import askfloat
from tkinter.simpledialog import messagebox

from os.path import expanduser
from os import path
from time import sleep

global ee
global ser
global geom
global configfn
global qqsy
global serport

global spinning
global afspinid
global spinning_id
global spinny
global spinspeed

#global spinningt
#global spinning_idt
#global spinnyt
#global spinspeedt

global curspinny
global clock_id


global SPLIT
global MRVFO
global VTOM
global DLOCK
global VFOAB
global MTOV
global BANDUP
global BANDDN
global CLAR
global FREQ
global VMSWAP

SPLIT=1
MRVFO=2
VTOM=3
DLOCK=4
VFOAB=5
MTOV=6
BANDUP=7
BANDDN=8
CLAR=9
FREQ=10
VMSWAP=11

ee = 0
spinning=0
afspinid=0
spinny=['|','/','-','\\']
curspinny=0
tuning=0
tuning_idt=''

################################# YOU SET THESE
serport='/dev/ttyAMA0'        # PORT TO TALK TO RIG
mycall='CHANGEME'        # EMPTY ON PURPOSE
wpm="13"            # WPM TO USE IF NO CONFIG FILE (FIX THIS)
################################# END OF YOU SET THESE

qqsy = [
    ("lb","160M"),
    ("bb","<F> (EAG)" , "1.8","green"),
    ("bb","<F> (EAG)" , "2","green"),
    ("sep","x"),
    ("lb","80M"),
    ("bb","<F> (E)" , "3.5","red"),
    ("bb","<F> (EAGnt)" , "3.525","red"),
    ("bb","<F> (E)" , "3.6","yellow"),
    ("bb","<F> (EA)" , "3.7","green"),
    ("bb","<F> (EAG)" , "3.8","green"),
    ("bb","<F> (EAG)" , "4","green"),
    ("sep","x"),
    ("lb","60M"),
    ("bb","<F> (EAG)" , "5.332","red"),
    ("bb","<F> (EAG)" , "5.348","red"),
    ("bb","<F> (EAG)" , "5.3585","red"),
    ("bb","<F> (EAG)" , "5.373","red"),
    ("bb","<F> (EAG)" , "5.405","red"),
    ("sep","x"),
    ("lb",""),
    ("bb","<F> (EAG)" , "5.3305","green"),
    ("bb","<F> (EAG)" , "5.3465","green"),
    ("bb","<F> (EAG)" , "5.357","green"),
    ("bb","<F> (EAG)" , "5.3715","green"),
    ("bb","<F> (EAG)" , "5.4035","green"),
    ("sep","x"),
    ("lb","40M"),
    ("bb","<F> (E)","7","red"),
    ("bb","<F> (AGnt)","7.025","red"),
    ("bb","<F> (EA)","7.125","yellow"),
    ("bb","<F> (EAG)","7.175","green"),
    ("bb","<F> (EAG)","7.3","green"),
    ("sep","x"),
    ("lb","30M"),
    ("bb","<F> (EAG)","10.1","red"),
    ("bb","<F> (EAG)","10.150","red"),
    ("sep","x"),
    ("lb","20M"),
    ("bb","<F> (E)","14","red"),
    ("bb","<F> (EAG)","14.025","red"),
    ("bb","<F> (E)","14.15","yellow"),
    ("bb","<F> (EA)","14.175","green"),
    ("bb","<F> (EAG)","14.225","green"),
    ("bb","<F> (EAG)","14.350","green"),
    ("sep","x"),
    ("lb","17M"),
    ("bb","<F> (EAG)","18.068","red"),
    ("bb","<F> (EAG)","18.11","yellow"),
    ("bb","<F> (EAG)","18.168","green"),
    ("sep","x"),
    ("lb","15M"),
    ("bb","<F> (E)","21","red"),
    ("bb","<F> (EAGnt)","21.025","red"),
    ("bb","<F> (E)","21.2","yellow"),
    ("bb","<F> (EA)","21.225","green"),
    ("bb","<F> (EAG)","21.275","green"),
    ("bb","<F> (EAG)","21.45","green"),
    ("sep","x"),
    ("lb","12M"),
    ("bb","<F> (EAG)","24.89","red"),
    ("bb","<F> (EAG)","24.93","yellow"),
    ("bb","<F> (EAG)","24.99","green"),
    ("sep","x"),
    ("lb","10M"),
    ("bb","<F> (EAGNT)","28","red"),
    ("bb","<F> (EAGNT)","28.3","yellow"),
    ("bb","<F> (EAG)","28.5","green"),
    ("bb","<F> (EAG)","29.7","green"),
    ("sep","x"),
    ("lb","TIME"),
    ("dd","W1AW", "1.8175", "3.5815", "7.0475", "14.0475", "18.0975", "21.0675", "28.0675"),
    ("dd","WWV", "2.5", "5", "10", "15", "20"),
    ("dd","CHU", "7.335", "7.85", "14.67"),
    ("sep","x"),
    ("lb","VOA"),
    ("dd","VOA", "0.909", "1.296", "1.530", "1.575", "4.930", "4.960", "5.925", "5.930", "6.080","6.195","7.270","7.325","7.375","9.815","12.030","13.590","15.460","15.580","15.715","17.530","17.530","17.790"),
    ("sep","x"),
    ("lb","CW"),
    ("dd","SKCC", "3.53","3.55","7.055","7.120","10.120","14.050","14.114","18.080","21.050","21.114","24.910","28.050","28.114"),

]

configfn=str(expanduser("~"))+"/.yaesuft757gxcat.conf"

def hovertxt(txt):
    hlabel.config(text=txt)

def hover(widg,txt):
    widg.bind("<Enter>",lambda evt, tt=txt: hovertxt(tt))
    widg.bind("<Leave>",lambda evt, tt="": hovertxt(tt))

def SYNC_RADIO_VFOS_TO_DISPLAY():
    CHFREQ('r',float(ifreq.get()))
    SIMPLECMD(VFOAB)
    CHFREQ('t',float(itfreq.get()))
    SIMPLECMD(VFOAB)

def SHOWSPLIT():

    if (itfreq.get() != "" and ifreq.get() != ""):

        diffreq = round(round(float(itfreq.get()) - float(ifreq.get()), 7) * 1000,7)

        sstr = "(no split)"

        if (diffreq < -0.0000001):
            sstr = "down " + str('%5.2f' % (diffreq)) + " kHz"

        if (diffreq > 0.0000001):
            sstr = "up " + str('%5.2f' % (diffreq)) + " kHz"

        spllb.config(text=sstr)

def ITF(frq):
    if (itfreq['state'] == 'disabled'):
        itfreq['state'] = 'normal'
        itfreq.delete(0,END)
        itfreq.insert(0,frq)
        itfreq['state'] = 'disabled'
    else:
        itfreq.delete(0,END)
        itfreq.insert(0,frq)

def SPL(dir,*args):
    print ("in SPL WITH DIR "+str(dir))
    if VFOSLINKED():
        print ("VFOS linked .. not splitting...")
        return False
    else:
        print ("VFOS not linked, adjusting...")
        tmpvfo=float(itfreq.get())
        tmpvfo = round(tmpvfo + dir,7)

        ITF(str('%7.5f' % (tmpvfo)))
        SYNC_RADIO_VFOS_TO_DISPLAY()

def SPLD(val, *args):
    SPL(-.00025)

def SPLU(val, *args):
    SPL(.00025)

def TWEAKT(val, *args):
    SPL(val)

def MAKESPLBUTSET(torf):
    if (torf == False):
        itfreq.config(bg='white')
    if (torf == True):
        itfreq.config(bg='grey')
    SPLBUTSET()

def SPLBUTSET(*args):

    if (VFOSLINKED() == True):
        itfreq.config(bg='white')
        spld.config(fg='black')    
        splu.config(fg='black')    
        splsd.config(fg='black')    
        splsu.config(fg='black')    
        spld['state']='normal'
        splu['state']='normal'
        splsd['state']='normal'
        splsu['state']='normal'
        itfreq['state']='normal'
        vspl.config(text='Link')
        messagebox.showinfo('Cat',"Check that the SPLT indicator is on.")
    else:
        itfreq.config(bg='grey')
        spld.config(fg='grey')    
        splu.config(fg='grey')    
        splsd.config(fg='grey')    
        splsu.config(fg='grey')    
        spld['state']='disabled'
        splu['state']='disabled'
        splsd['state']='disabled'
        splsu['state']='disabled'
        itfreq['state']='disabled'
        vspl.config(text='Unlink')

def VSPL(*args):

    # if VFOS are linked then unlink them
    if (VFOSLINKED() == True):
        vspl.config(text='Link')
        SIMPLECMD(SPLIT)
    else:
        itfreq['state']='normal'
        itfreq.delete(0,END)
        itfreq.insert(0,ifreq.get())
        SYNC_RADIO_VFOS_TO_DISPLAY()
        SIMPLECMD(SPLIT)

    SPLBUTSET()
        

def numonly(val):
    for ch in val:
        if (not ch in {'1','2','3','4','5','6','7','8','9','0','.'}):
            return False
    return True


def startspinning(val):
    global spinspeed
    global spinning
    global afspinid
    spinspeed=500
    spinning = 1
    root.after_cancel(afspinid)
    spinknob(val)

def VFOSLINKED():
    lnkcol=itfreq.cget('bg')
    if (lnkcol == 'grey'):
        return True
    else:
        return False

def afterspinsync(*args):
    global afspinid
    if (afspinid != ''):
        print("after spin "+ str(afspinid))
        if VFOSLINKED():
            ITF(ifreq.get())
        SYNC_RADIO_VFOS_TO_DISPLAY()
        SHOWSPLIT()

def stopspinning(*args):
    global afspinid
    global spinning
    global spinning_id
    global spinspeed
    spinning = 0
    spinspeed=500
    spinnything.configure(text="")
    root.after_cancel(spinning_id)
    afspinid=root.after(500,afterspinsync,'')
#    if VFOSLINKED():
#        ITF(ifreq.get())

#    SYNC_RADIO_VFOS_TO_DISPLAY()
#    SHOWSPLIT()

def spinknob(val):
    global curspinny
    global spinny
    global spinning
    global spinning_id
    global spinspeed
    curspinny = (curspinny + (1 if val > 0 else -1)) % 4
    spinnything.configure(text=spinny[curspinny])
    tmpvfo = float(ifreq.get())
    tmpvfo = round(tmpvfo + val,5);
    if (tmpvfo > 29.99999):
        tmpvfo = .5
    if (tmpvfo < .5):
        tmpvfo = 29.99999
    CHFREQ('r',tmpvfo)
    if (spinning == 1):
        spinning_id=root.after(spinspeed,spinknob,val)
        spinspeed = 17 if (spinspeed==34) else spinspeed
        spinspeed = 34 if (spinspeed==67) else spinspeed
        spinspeed = 67 if (spinspeed==125) else spinspeed
        spinspeed = 125 if (spinspeed==250) else spinspeed
        spinspeed = 250 if (spinspeed==500) else spinspeed

def spinknobt(val):
    global spinnyt
    global spinningt
    global spinning_idt
    global spinspeedt
    global thatvfo
    thatvfo = round(thatvfo + val,7);
    if (thatvfo > 29.99999):
        thatvfo = .5
    if (thatvfo < .5):
        thatvfo = 29.99999
    ITF(str('%7.5f' % (thatvfo)))
    if (spinningt == 1):
        spinning_idt=root.after(spinspeedt,spinknobt,val)
        spinspeedt = 17 if (spinspeedt==34) else spinspeedt
        spinspeedt = 34 if (spinspeedt==67) else spinspeedt
        spinspeedt = 67 if (spinspeedt==125) else spinspeedt
        spinspeedt = 125 if (spinspeedt==250) else spinspeedt
        spinspeedt = 250 if (spinspeedt==500) else spinspeedt

def startclock(*args):
    global clock_id
    putdate()
    clock_id=root.after(500,startclock,'')

def putdate():
    now = str(datetime.datetime.utcnow())
    datelab.config(text=now[0:16]+" UTC")
    if (now[18] in {'0','2','4','6','8'}):
        datelab.config(bg='#00ff00')
    else:
        datelab.config(bg='#005500')

def WriteCfg():
    global serport
    global configfn

    fh=open(configfn,'w+')
    fh.write('ifreq='+str(ifreq.get())+"\n")
    sx=root.geometry().replace('+',' ').split()[1]
    sy=root.geometry().replace('+',' ').split()[2]
    fh.write("geom=+"+sx+"+"+sy+"\n")
    fh.write("serport="+serport+"\n")
    #if (ifreq.get() != itfreq.get()):
    #    SIMPLECMD(SPLIT)

    print("Saved config to "+configfn)


def QSY(*args):
    if VFOSLINKED():
        ITF(ifreq.get())

    SYNC_RADIO_VFOS_TO_DISPLAY()
    

def QUICKQSY(string):
    ifreq.delete(0,END)
    ifreq.insert(0,string)
    QSY()

def ReadCfg():
    global serport
    global geom
    global configfn
    global ee
    global ser

    if (not path.exists(configfn)):
        root.iconify()
        tmpvfo=askfloat("Frequency","Enter the frequency to go to the first time you start.",minvalue=.5,maxvalue=29.99999)
        serport=askstring("Serial Port","Serial Port for CAT, e.g. /dev/ttyUSBx").strip()
        ifreq.delete(0,END)
        ifreq.insert(0,str('%7.5f' % (tmpvfo)))
        itfreq.insert(0,str('%7.5f' % (tmpvfo)))
        WriteCfg()

    if (path.exists(configfn)):
        rr = 1
        cc = 1
        fh=open(configfn,'r')
        cfglines = fh.readlines()
        fh.close()
        for thing in ('serport','ifreq','geom'):
            print ("thing should be "+thing)
            for cfgline in cfglines:
                items=cfgline.split('=')
                if (items[0] == "ifreq" and items[0] == thing):
                    ifreq.delete(0,END)
                    ifreq.insert(0,items[1].strip())
                    itfreq.delete(0,END)
                    itfreq.insert(0,items[1].strip())
                if (items[0] == "geom" and items[0] == thing):
                    geom=items[1].strip()
                    root.geometry(geom)
                if (items[0] == "serport" and items[0] == thing):
                    serport=items[1].strip()
                    ser = serial.Serial(
                        port=serport,
                        baudrate=4800,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_TWO,
                        bytesize=serial.EIGHTBITS,
                        timeout=1,
                        xonxoff=0,
                        rtscts=0,
                        dsrdtr=0
                    )

        if (ifreq.get() == itfreq.get()):
            print("equal")
            MAKESPLBUTSET(False)

        if (ifreq.get() != itfreq.get()):
            print("not equal")
            MAKESPLBUTSET(True)

        return True
    else:
        return None

def Quitter(*args):
    WriteCfg()
    root.destroy()

def Send(p4,p3,p2,p1,co):
    global ser

    ser.write(bytes([p4,p3,p2,p1,co]))
    ser.flush()

    #print ("Sent "+str(p4)+" "+str(p3)+" "+str(p2)+" "+str(p1)+" "+str(co))
    time.sleep(.03)

def SIMPLECMD(byt):
    global thisvfo
    bandstops = [ 0, 1.5, 3.5, 7, 10, 14, 18, 21, 24.5, 28, 30 ]
    #
    # RADIO QUIRK:
    # The 160M band IS correct and mimics the radio when band
    # down is pressed. 2.49999 then BAND DOWN on the radio 
    # results in being put in the 10M band.
    #
    # Other quirk:
    # When going up 500k on front panel button:
    # 29.49999 becomes 29.99999
    # 29.50000 becomes 00.50000
    # When going down 500k on front panel button:
    # 00.50000 becomes 29.50000
    # 00.99999 becomes 29.99999
    bands = [
        [ 1.5, 2.49999 ],
        [ 3.5, 3.99999 ],
        [ 7.0, 7.49999 ],
        [ 10.0, 10.49999 ],
        [ 14.0, 14.49999 ],
        [ 18.0, 18.49999 ],
        [ 21.0, 21.49999 ],
        [ 24.5, 24.99999 ],
        [ 28.0, 29.99999 ]
        ]

    if (byt == 17 or byt == 18):
        if (byt == 17):
            if (thisvfo >= 29.5):
                thisvfo = round(thisvfo -29,5)
            else:
                thisvfo = round(thisvfo + .5,5)

        if (byt == 18):
            if (thisvfo <= 0.99999):
                thisvfo = round(thisvfo + 29,5)
            else:
                thisvfo = round(thisvfo - .5,5)

        CHFREQ('r',thisvfo)

    elif (byt == 7 or byt == 8):
        mhz = int(thisvfo)
        hun = int(int(thisvfo * 10) - (mhz * 10))
        submhz = float(mhz)
        if (hun >= 5):
            submhz = submhz +float(5/10)
        remmhz = thisvfo - submhz
        nn = 0
        jmpband=float(0)
        for xx in bands:
            if (thisvfo < bands[nn][0]):
                print("You're below the "+str(bands[nn])+" band ")
                if (byt == 7):
                    jmpband = float(bands[(nn)%9][0]);
                if (byt == 8):
                    jmpband = float(bands[(nn - 1)%9][0]);
                break

            if (bands[nn][0] <= thisvfo <= bands[nn][1]):
                print("You're in the "+str(bands[nn])+" band ")
                if (byt == 7):
                    jmpband = float(bands[(nn + 1)%9][0]);
                if (byt == 8):
                    jmpband = float(bands[(nn - 1)%9][0]);
                break
            else:
                nn = nn + 1

        thisvfo = round(float(jmpband + remmhz),5)
        CHFREQ('r',thisvfo)

    elif (byt == 10):
        print ("DO NOT USE 10 FOR SIMPLECMD - USE CHFREQ INSTEAD")
    else:
        Send(0,0,0,0,byt)

def CHFREQ(txrx,xfo):

    freq=(str(xfo).strip())
    try:
        dec = freq.index('.')
    except:
        freq = freq + '.'

    if (xfo >= 10.00000):
        freq = "0" + freq + "00000"
    else:
        freq = "00" + freq + "00000"

    b1=int((freq[0:2]),16)
    b2=int((freq[2]+freq[4]),16)
    b3=int((freq[5:7]),16)
    b4=int((freq[7:9]),16)
    # 12.345.67 becomes hex 67|45|23|01|0B 
    co=int('0B',16)
    Send(b4,b3,b2,b1,10)

    if (txrx == 'r'):
        ifreq.delete(0,END)
        ifreq.insert(0,str('%7.5f' % (xfo)))

    if (txrx == 't'):
        itfreq.delete(0,END)
        itfreq.insert(0,str('%7.5f' % (xfo)))

    if (spinning == 0):
        SHOWSPLIT()

root=Tk()

butframe=Frame(root,borderwidth=2,relief="groove")
qsyframe=Frame(root,borderwidth=2,relief="groove")
quickqsyframe=Frame(root,borderwidth=2,relief="groove")
helpframe=Frame(root,borderwidth=2,relief="groove")
ifreqframe=Frame(root,borderwidth=2,relief="groove")
dialbutframe=Frame(root,borderwidth=2,relief="groove")

root.bind("<Escape>",Quitter)
root.bind("<Control-w>",Quitter)
root.protocol("WM_DELETE_WINDOW", Quitter)
root.title("Yaesu FT-757GX (MK1)")

#HELP
hlabel=Label(helpframe,text="")

ifreq = Entry(ifreqframe, font="Helvetica 44 bold", justify="center", width=9, validate="key")
ifreq['validatecommand']=(ifreq.register(numonly),'%P')

ifreq.bind("<Return>",QSY)
ifreq.bind("<KP_Enter>",QSY)

itfreq = Entry(ifreqframe, font="Helvetica 14 bold", justify="center", width=9, bg='grey', validate="key")
itfreq['validatecommand']=(itfreq.register(numonly),'%P')

#itfreq.bind("<Button-1>",lambda: TWEAKT(float(0))
#itfreq.bind("<ButtonRelease-1>",lambda: TWEAKT(float(0))
itfreq.bind("<Return>",lambda x: TWEAKT(float(0)))
itfreq.bind("<KP_Enter>",lambda x: TWEAKT(float(0)))

splu = Button(ifreqframe, text="+ 250", justify="center", width=6, command=lambda: TWEAKT(float(.00025)), fg='grey')
vspl = Button(ifreqframe, text="Unlink",  justify="center", width=6, command=VSPL)
spld = Button(ifreqframe, text="- 250", justify="center", width=6, command=lambda: TWEAKT(float(-.00025)), fg='grey')
splsu = Button(ifreqframe, text=">>", justify="center", width=2, command=lambda: TWEAKT(float(.00001)),fg='grey')
splsd = Button(ifreqframe, text="<<", justify="center", width=2, command=lambda: TWEAKT(float(-.00001)),fg='grey')
spllb = Label(ifreqframe, text="(tx freq)")

SPLIT=1
MRVFO=2
VTOM=3
DLOCK=4
VFOAB=5
MTOV=6
BANDUP=7
BANDDN=8
CLAR=9
FREQ=10
VMSWAP=11

# RADIO BUTTONS 
split = Button(butframe,text="SPLIT", command=lambda: SIMPLECMD(SPLIT), width=11) #1
mrvfo = Button(butframe,text="MR/VFO", command=lambda: SIMPLECMD(MRVFO), width=11) #2
vtom = Button(butframe,text="V -> M", command=lambda: SIMPLECMD(VTOM), width=11) #3
dlock = Button(dialbutframe,text="D LOCK", command=lambda: SIMPLECMD(DLOCK), width=11) #4
vfoab = Button(butframe,text="VFO A/B", command=lambda: SIMPLECMD(VFOAB), width=11) #5
mtov = Button(butframe,text="M -> V", command=lambda: SIMPLECMD(MTOV), width=11) #6
bandup = Button(butframe,text="BAND UP", command=lambda: SIMPLECMD(BANDUP), width=11) #7
banddn = Button(butframe,text="BAND DN", command=lambda: SIMPLECMD(BANDDN), width=11) #8
clar = Button(dialbutframe,text="CLAR", command=lambda: SIMPLECMD(CLAR), width=11) #9
freq = Button(dialbutframe,text="QSY", command=QSY , width=11) #10
vmswap = Button(butframe,text="V<>M", command=lambda: SIMPLECMD(VMSWAP), width=11) #11
datelab = Label (butframe, font="Helvetica 12 bold", text="YYYY-MM-DDDD HH:MM", width=23)
up500k = Button(butframe,text="500k ^", command=lambda: SIMPLECMD(17), width=11) #17 (made up)
dn500k = Button(butframe,text="500k v", command=lambda: SIMPLECMD(18), width=11) #18 (made up)

# VFO SPINNERS
u1000 = Button(qsyframe,text=">1000>", width=5)
u500 = Button(qsyframe,text=">500>", width=5)
u100 = Button(qsyframe,text=">100>", width=5)
u10 = Button(qsyframe,text=">10>", width=5)
spinnything = Label (qsyframe,text=" ",font="Helvetica 16 bold", width=3)
d10 = Button(qsyframe,text="<10<", width=5)
d500 = Button(qsyframe,text="<500<", width=5)
d100 = Button(qsyframe,text="<100<", width=5)
d1000 = Button(qsyframe,text="<1000<", width=5)

#@splsu.bind('<ButtonRelease-1>',lambda evt, val = float(.00001): TWEAKT(val))
#splsd.bind('<ButtonRelease-1>',lambda evt, val = float(-.00001): TWEAKT(val))

u1000.bind('<Button-1>',lambda evt, val = float(.001): startspinning(val))
u1000.bind('<ButtonRelease-1>',stopspinning)
u500.bind('<Button-1>',lambda evt, val = float(.0005): startspinning(val))
u500.bind('<ButtonRelease-1>',stopspinning)
u100.bind('<Button-1>',lambda evt, val = float(.0001): startspinning(val))
u100.bind('<ButtonRelease-1>',stopspinning)
u10.bind('<Button-1>',lambda evt, val = float(.00001): startspinning(val))
u10.bind('<ButtonRelease-1>',stopspinning)
d10.bind('<Button-1>',lambda evt, val = float(-.00001): startspinning(val))
d10.bind('<ButtonRelease-1>',stopspinning)
d100.bind('<Button-1>',lambda evt, val = float(-.0001): startspinning(val))
d100.bind('<ButtonRelease-1>',stopspinning)
d500.bind('<Button-1>',lambda evt, val = float(-.0005): startspinning(val))
d500.bind('<ButtonRelease-1>',stopspinning)
d1000.bind('<Button-1>',lambda evt, val = float(-.001): startspinning(val))
d1000.bind('<ButtonRelease-1>',stopspinning)

rr = 2
cc = 1
qqsym={}
qqmen={}
qqsv={}
dummy=""
quickqsyframeleg=Frame(quickqsyframe)
quickqsyframeleg.grid(row=1,column=1,columnspan=10)
Label(quickqsyframeleg, text="Quick QSY, E/Extra, A/Advanced, G/General, T/Tech, t/Tech CW Only, N/Novice, n/Novice CW Only").grid(row=1,column=1)
Label(quickqsyframeleg, text="CW", bg="red").grid(row=1,column=2)
Label(quickqsyframeleg, text="end CW / begin Phone", bg="yellow").grid(row=1,column=3)
Label(quickqsyframeleg, text="Phone", bg="green").grid(row=1,column=4)

hover(quickqsyframeleg,"This area is the legend for Quick QSY.  Hopefully, it closely mimics the band plan.")

# QUICK QSY buttons construction
for qq in qqsy:
    if (qq[0] == "dd"):
        qqsv[qq[1]]=StringVar(quickqsyframe)
        qqsv[qq[1]].set(qq[1])
        qqsym[qq[1]]=OptionMenu(quickqsyframe,qqsv[qq[1]],qq[1])
        qqsym[qq[1]].grid(row=rr,column=cc)
        hover(qqsym[qq[1]],"Press and hold to choose one of the frequencies in the list.")
        cc = cc + 1
        qqmen[qq[1]]=qqsym[qq[1]].children["menu"]
        for qfreq in qq:
            if (qfreq == qq[0] or qfreq == qq[1]):
                continue
            zz=lambda mkr=qfreq: QUICKQSY(mkr)
            qqmen[qq[1]].add_command(label=qfreq, command=zz)

    if (qq[0] == "bb"):
        bb=Button(quickqsyframe,\
        text=qq[1].replace('<F>',str('%6.4f' % float(qq[2]))), \
        command=lambda mkr = qq[2]: QUICKQSY(mkr), \
        width=14, pady=0 , bg=qq[3]
        )
        bb.grid(row=rr,column=cc)
        hover(bb,"Press to QSY to "+bb['text'])
        cc = cc + 1
    if (qq[0] == "lb"):
        ll=Label(quickqsyframe,\
        text=qq[1])
        ll.grid(row=rr,column=cc)
        hover(ll,"This is just a band label.  It's not very interesting.")
        cc = cc + 1
    if (qq[0] == "sep"):
        rr = rr + 1
        cc = 1
    

d1000.pack(side=LEFT)
d500.pack(side=LEFT)
d100.pack(side=LEFT)
d10.pack(side=LEFT) 
spinnything.pack(side=LEFT)
u1000.pack(side=RIGHT)
u500.pack(side=RIGHT)
u100.pack(side=RIGHT)
u10.pack(side=RIGHT)

hover(u1000,"Press to change frequency, or hold to spin the knob.")
hover(u500,"Press to change frequency, or hold to spin the knob.")
hover(u100,"Press to change frequency, or hold to spin the knob.")
hover(u10,"Press to change frequency, or hold to spin the knob.")
hover(d1000,"Press to change frequency, or hold to spin the knob.")
hover(d500,"Press to change frequency, or hold to spin the knob.")
hover(d100,"Press to change frequency, or hold to spin the knob.")
hover(d10,"Press to change frequency, or hold to spin the knob.")


ifreqframe.grid(row=1,column=1,columnspan=3)

ifreq.grid(row=1,rowspan=3,column=1,columnspan=2)
itfreq.grid(row=2,column=3,columnspan=2)
splu.grid(row=1,column=5)
vspl.grid(row=2,column=5)
spld.grid(row=3,column=5)
splsd.grid(row=3,column=3)
splsu.grid(row=3,column=4)
spllb.grid(row=1,column=3,columnspan=2)

butframe.grid(row=1,column=4,rowspan=3)
dialbutframe.grid(row=2,column=1,columnspan=3)

clar.grid(    row=1,column=1,rowspan=1)
freq.grid(    row=1,column=2,rowspan=1)
dlock.grid(   row=1,column=3,rowspan=1)

hover(ifreq,"You can enter frequency in MHz here, then hit the QSY button to go there.")
hover(itfreq,"You can enter frequency in MHz here, then hit the QSY button to go there.")
hover(freq,"This button sends the above frequency to the radio.")
hover(butframe,"This is a group of the Yaesu Radio buttons.")
hover(clar,"This lets you turn on the CLAR on the radio, but the program doesn't track its status.")
hover(dlock,"This locks ONLY the physical knob on the radio to prevent accidental QSY.")
hover(vspl,"Unbind transmit VFO from main VFO (fake split)")
hover(splu,"Transmit up 1KHz when unbound (fake split)")
hover(spld,"Transmit down 1KHz when unbound (fake split)")

# FRAMES LAYOUT
qsyframe.grid(row=3,column=1,columnspan=3,sticky='EW')
quickqsyframe.grid(row=7,column=1,columnspan=4,sticky='EW')
helpframe.grid(row=8,column=1,columnspan=4,sticky='EW')

# HELP LABEL
hlabel.grid(row=1,column=1)

# UPPER RIGHT RADIO BUTTONS
vfoab.grid(   row=1,column=2,rowspan=1)
split.grid(   row=1,column=3,rowspan=1)
mrvfo.grid(   row=1,column=4,rowspan=1)
vmswap.grid(  row=2,column=2,rowspan=1)
vtom.grid(    row=2,column=3,rowspan=1)
mtov.grid(    row=2,column=4,rowspan=1)
banddn.grid(   row=3,column=3,rowspan=1)
bandup.grid(   row=3,column=4,rowspan=1)
dn500k.grid(   row=4,column=3,rowspan=1)
up500k.grid(   row=4,column=4,rowspan=1)
datelab.grid( row=5,column=1,columnspan=4)

hover(vfoab,"Switch between VFO A and B on the radio.  Program won't know the radio's frequency at this point.")
hover(split,"Transmit on the other VFO, whichever it is.  Program won't know the radio's frequency at this point.")
hover(mrvfo,"Switch between VFO and MEM on the radio.  Program won't know the radio's frequency at this point.")
hover(vmswap,"Swap the contents of VFO and MEM on the radio.  Program won't know the radio's frequency at this point.")
hover(vtom,"Write VFO into current MEM on the radio.  Program won't know the radio's frequency at this point.")
hover(mtov,"Write MEM into Current VFO on the radio.  Program won't know the radio's frequency at this point.")
hover(banddn,"Go down to the next ham band.  Position of 500k step switch does not matter.")
hover(bandup,"Go up to the next ham band.  Position of 500k step switch does not matter.")
hover(dn500k,"Go down 500 KHz.  Position of 500k step switch does not matter.")
hover(up500k,"Go up 500 KHz.  Position of 500k step switch does not matter.")

hover(qsyframe,"This is the VFO area.")
hover(quickqsyframe,"This area has the Quick QSY buttons.  Radio will immediately go there.")
hover(helpframe,"This area is for helpful help message hovering.")

ReadCfg()
SYNC_RADIO_VFOS_TO_DISPLAY()

root.geometry(geom)
root.deiconify()
startclock()

root.mainloop()

