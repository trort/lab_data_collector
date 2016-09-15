from datetime import datetime
import time
import visa
import numpy as np

FILENAME = "sweep.txt";
I_LIMIT = 0.0001;
device = visa.instrument("GPIB0::14");
START = -2;
END = 2;
STEP = 0.1;
INTERVAL = 0.5; #in sec
#lockin = visa.instrument("GPIB0::8");

output = open(FILENAME,"a");
t0 = time.clock();

def Init():
    #device.write("smua.reset()");
    device.write("smua.source.limiti = " + str(I_LIMIT));

def set_voltage(v):
    device.write("smua.source.levelv = " + str(v));

def read_voltage(v):
    ans = device.ask("print(smua.measure.i())") #+ "\t" + lockin.ask("OUTP?1");
    line = str(time.clock()-t0) + "\t" + str(v) + "\t" + ans + "\t" + str(datetime.now()) + "\n";
    print str(v) + "\t" + ans;
    output.write(line);

def End():
    output.close();
    print "Program done!"

Init();

for i in np.linspace(START, END, abs(END - START)/STEP + 1, endpoint=True):
    set_voltage(i);
    time.sleep(INTERVAL);
    read_voltage(i);

End();
    
