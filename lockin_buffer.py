from datetime import datetime
import time
import visa
import math

FILENAME = "buffer.txt"
output = open(FILENAME,"w");
LIA1 = visa.instrument("GPIB0::12",values_format = visa.ascii);

def TakeData():
    t0 = time.clock();
    result = "Test started at " + str(datetime.now()) + "\n";

    LIA1.write("STRT");
    #LIA1.write("STRD"); #start scan after 0.5 sec
    t = time.clock() - t0;
    result += "Scan started at t = " + str(t) + "\n";

    time.sleep(5); #30s max
    LIA1.write("PAUS"); #pause
    t = time.clock() - t0;
    result += "Scan ended at t = " + str(t) + "\n";
    LIA1.ask("SPTS ?");
    num = LIA1.ask("SPTS ?"); #number of points
    result += "There are " + num + " points\n";
    t = time.clock() - t0;
    result += "Transfer started at t = " + str(t) + "\n";

    LIA1.values_format = visa.single;
    BIN1 = LIA1.ask("TRCL ? 1,0," + num);
    BIN2 = LIA1.ask("TRCL ? 2,0," + num);
    t = time.clock() - t0;
    result += "Transfer ended at t = " + str(t) + "\n";
    
    BIN1 = list(BIN1);
    BIN2 = list(BIN2);
    for i in range(0,int(num)):
        mantissa = ord(BIN1[4*i+1])*256+ord(BIN1[4*i]);
        if mantissa >= 32768:
            mantissa -= 65536;
        CONV1 = math.ldexp(mantissa, ord(BIN1[4*i+2])-124);

        mantissa = ord(BIN2[4*i+1])*256+ord(BIN2[4*i]);
        if mantissa >= 32768:
            mantissa -= 65536;
        CONV2 = math.ldexp(mantissa, ord(BIN2[4*i+2])-124);
            
        result += str(CONV1) + "\t" + str(CONV2) + "\n";

    t = time.clock() - t0;
    result += "Evrything ended at t = " + str(t) + "\n";

    output.write(result);
    print result;

def Init():
    LIA1.write("REST"); #reset
    LIA1.write("SRAT 13"); #sample rate = 512Hz
    LIA1.write("SEND 1"); #1 shot mode
    LIA1.write("TSTR 0"); #auto start off
    LIA1.write("FAST 0"); #fast mode

def End():
    #reset lock_in
    LIA1.write("REST"); #reset
    LIA1.write("SRAT 14"); #sample rate = trigger
    LIA1.write("SEND 0"); #loop mode
    LIA1.write("TSTR 1"); #auto start on
    LIA1.write("FAST 0"); #normal mode
    LIA1.write("STRT"); #start
    LIA1.write("TRIG"); #trigger - extramely important!
    
    output.close();
    print "Program done!"

Init();
TakeData();
End();
    
