from datetime import datetime
import time
import visa

FILENAME = "buffer.txt"
output = open(FILENAME,"w");
LIA1 = visa.instrument("GPIB0::12");

def TakeData():
    t0 = time.clock();
    result = "Test started at " + str(datatime.now()) + "\n";

    #LIA1.write("STRT");
    LIA1.write("STRD"); #start scan after 0.5 sec
    t = time.clock() - t0;
    result += "Scan started at t = " + str(t+0.5) + "\n";

    time.sleep(30); #30s
    LIA1.write("PAUS"); #pause
    t = time.clock() - t0;
    result += "Scan ended at t = " + str(t) + "\n";
    num = LIA1.ask("SPTS ?"); #number of points
    result += "There are " + num + " points\n";
    CH1 = LIA1.ask_for_values("TRCA ? 1,0," + num);
    CH2 = LIA1.ask_for_values("TRCA ? 2,0," + num);
    t = time.clock() - t0;
    result += "Transfer ended at t = " + str(t) + "\n";
    
    for i in range(0,int(num)):
        result += str(i) + "\t" + CH1[i] + "\t" + CH2[i] + "\n";

    output.write(result);
    t = time.clock() - t0;
    result += "Evrything ended at t = " + str(t) + "\n";

def Init():
    LIA1.write("REST"); #reset
    LIA1.write("SRAT 13"); #sample rate = 512Hz
    LIA1.write("SEND 1"); #1 shot mode
    LIA1.write("TSTR 0"); #auto start off
    LIA1.write("FAST 2"); #fast mode

def End():
    output.close();
    print "Program done!"

Init();
TakeData();
End();
    
