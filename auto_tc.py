from datetime import datetime
import time
import visa
import math

FILENAME = "IGZO_130408_off5_4pt.txt"
output = open(FILENAME,"a");
LIA1 = visa.instrument("GPIB0::12");

i = 0;
CH1 = list();
CH2 = list();
t = list();
t0 = time.clock();
TT = "\t";

def TakeData():
    global i,t0,TT;
    t.append(time.clock()-t0);
    CH1.append(float(LIA1.ask("OUTP ? 1")));
    CH2.append(float(LIA1.ask("OUTP ? 2")));
    output.write(str(i)+TT+str(t[i])+TT+str(CH1[i])+TT+str(CH2[i])+"\n");

def Init():
    global i;
    output.write("STARTED AT " + str(datetime.now()) +"\n");
    output.write("i\ttime\tCH1\tCH2\n");
    for i in range(0, 50):
        time.sleep(1);
        TakeData();
        print str(i)+TT+str(t[i])+TT+str(CH1[i])+TT+str(CH2[i]);
    print "turn on LEDs!";
    for i in range(50, 250):
        TakeData();

def Vari_Time():
    global i;
    y1 = 0;
    y2 = 0;
    t1 = 0;
    t2 = 0;
    for j in range(0,4):
        y1 += CH1[i-4-j];
        t1 += t[i-4-j];
        y2 += CH1[i-j];
        t2 += t[i-j];
    if t2-t1 != 0 and y2-y1 != 0:
        slope = abs((y2-y1)/(t2-t1));
        interval = (CH1[i]/slope)/2000;
    else:
        interval = t[i]-t[i-1];
    if interval > 30:
        interval = 30;
    if interval > 0.035:
        time.sleep(interval - 0.035);
    i += 1;
    TakeData();

def End():
    output.close();
    print "Program done!";

Init();
while t[i] < 4000:
    Vari_Time();
    if t[i]-t[i-1] > 0.1:
        print str(i)+TT+str(t[i])+TT+str(CH1[i])+TT+str(CH2[i]);
End();
