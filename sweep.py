from datetime import datetime
import time
import visa

FILENAME = "sweep.txt";
output = open(FILENAME,"w");
device = visa.instrument("GPIB0::14");

t0 = time.clock();

def init():
    device.write("smua.reset()");
    device.write("smua.source.limiti = 0.0001");

def set_voltage(v):
    device.write("smua.source.levelv = " + str(v));

def read_voltage(v):
    device.write("print(smua.measure.i())");
    ans = device.read();
    line = str(time.clock()-t0) + "\t" + str(v) + "\t" + ans + "\t" + str(datetime.now()) + "\n";
    print str(v) + "\t" + ans;
    output.write(line);

def End():
    output.close();
    print "Program done!"

for i in range(-20, 21, 1):
    v = i/10.0;
    set_voltage(v);
    time.sleep(0.5);
    read_voltage(v);

End();
    
