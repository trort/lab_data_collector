from datetime import datetime
import time
import visa

### basic parameters ###
TESTNAME = "longlong_fast"
INTERVAL = 0.1 #in sec
rm = visa.ResourceManager();
lockin = rm.open_resource("GPIB1::11::INSTR");

### initialize ###
FILENAME = TESTNAME + '_' + str(datetime.now()).replace(':','-') + ".txt"
output = open(FILENAME,'a')
t0 = time.clock();

### measurements ###
def measurement(i):
    t = float(time.clock()-t0)
    result = lockin.ask("OUTP?1").strip()
    line = str(t) + "\t" + result
    return line

### main loop ###
while True:
    try:
        line = measurement(1)
        print line
        output.write(line + "\t" + str(datetime.now()) + '\n')
        time.sleep(INTERVAL)
    except:  # stop with ^C
        break

### wrap up ###
output.flush()
output.close() 
