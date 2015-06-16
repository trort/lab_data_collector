from datetime import datetime
import time
import visa

from Mux_Box import Mux_Box

TESTNAME = "longlong_slow"
SAMPLES = [1,2,3] # index of samples to measure
INTERVAL = 2 #in sec
rm = visa.ResourceManager();
lockin = rm.open_resource("GPIB1::11::INSTR");
box = Mux_Box(lockin);

### initialize ###
box.Init()
output = {}
for i in SAMPLES:
    filename = ('%s_sample%i_%s.txt' % (TESTNAME, i, str(datetime.now()).replace(':','-')))
    output[i] = open(filename,'a')
t0 = time.clock();

### measurements ###
while True:
    try:
        for i in SAMPLES:
            box.Set_Sample(i)
            time.sleep(INTERVAL)
            result = box.Read()
            line = str(time.clock()-t0) + "\t" + result
            print str(i) + '\t' + line
            output[i].write(line + '\t' + str(datetime.now()) + '\n')
            output[i].flush()
    except (KeyboardInterrupt, SystemExit):
        break

### wrap up ###
for i in SAMPLES:
    output[i].flush()
    output[i].close()       
