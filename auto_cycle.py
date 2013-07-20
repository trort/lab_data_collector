from datetime import datetime
import time
import visa
import numpy as np

FILENAME = "cycled_auto.txt";
MIN = 0.001325;
MAX = 0.00134;
V_LIMIT = 50;
I_LEVEL = 0.01;
interval = 1;
source = visa.instrument("GPIB0::25");
lockin1 = visa.instrument("GPIB0::10");
lockin2 = visa.instrument("GPIB0::11");
thermistor = visa.instrument("GPIB0::1");

output = open(FILENAME,"a");
t0 = time.clock();

def Init():
    #device.write("smua.reset()");
    #source.write("smua.source.limitv = " + str(V_LIMIT));
    source.write(":SOUR:FUNC CURR");
    source.write(":SENS:VOLT:PROT " + str(V_LIMIT));
    thermistor.write(":CONF:RES");
    output.write("started at " + str(datetime.now()) + "\n");
    output.write("time\tGPIB10CH1\tGPIB10CH2\tGPIB11CH1\tGPIB11CH2\tTemp\ttimestamp\n");

def Led_On():
    global interval;
    #source.write("smua.source.leveli = " + str(I_LEVEL));
    source.write(":SOUR:CURR:LEV " + str(I_LEVEL));
    print "LEDs turned ON at " + str(datetime.now());
    interval = 0.3;

def Led_Off():
    global interval;
    #source.write("smua.source.leveli = -0.001");
    source.write(":SOUR:CURR:LEV -0.00001");
    print "LEDs turned OFF at " + str(datetime.now());
    interval = 1;

def Read():
    line = str(time.clock()-t0) + "\t" + lockin1.ask("OUTP?1") + "\t" + lockin1.ask("OUTP?2") + "\t" + lockin2.ask("OUTP?1") + "\t" + lockin2.ask("OUTP?2") + "\t" + thermistor.ask(":READ?");
    print line;
    output.write(line + "\t" + str(datetime.now()) + "\n");

def Cycle():
    global interval;
    Read();
    value = float(lockin1.ask("OUTP?1"));
    if value > MAX:
        Led_On();
    if value < MIN:
        Led_Off();
    time.sleep(interval);

def End():
    output.close();
    print "Program done!"

# main program
Init();
Led_Off();

while True:
    Cycle();

End();
    
