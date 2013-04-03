from datetime import datetime
import time
import visa

FILENAME = "sweep.txt";
output = open(FILENAME,"w");
device = visa.instrument("GPIB0::14");
lockin = visa.instrument("GPIB0::8");

t0 = time.clock();

def init():
    device.write("smua.reset()");
    device.write("smua.source.limiti = 0.0001");

def set_voltage(v):
    device.write("smua.source.levelv = " + str(v));

def read_voltage(v):
    ans = device.ask("print(smua.measure.i())") + "\t" + lockin.ask("OUTP?1");
    line = str(time.clock()-t0) + "\t" + str(v) + "\t" + ans + "\t" + str(datetime.now()) + "\n";
    print str(v) + "\t" + ans;
    output.write(line);

def End():
    output.close();
    print "Program done!"

for i in np.linspace(-2,2,100,endpoint=True):
    v = i;
    set_voltage(v);
    time.sleep(0.5);
    read_voltage(v);

End();
    
