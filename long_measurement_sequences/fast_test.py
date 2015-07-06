from datetime import datetime
import time
import visa

### basic parameters ###
sample_no = 2
TESTNAME = "longlong_fast"
INTERVAL = 0 #in sec
rm = visa.ResourceManager();
lockin = rm.open_resource("GPIB1::9::INSTR");

### initialize ###
FILENAME = ('%s_sample%i_%s.txt' % (TESTNAME, sample_no, str(datetime.now()).replace(':','-')))
output = open(FILENAME,'a')
t0 = time.clock();
with open('in_fast_mode.ini','w') as config_file:
    config_file.write(str(sample_no))

### make one measurement ###
def do_measurement(i):
    t = float(time.clock()-t0)
    result = lockin.ask("OUTP?1").strip()
    line = str(t) + "\t" + result
    return line

### main loop ###
next_call = time.time()
while True:
    try:
        line = do_measurement(1)
        print line
        output.write(line + "\t" + str(datetime.now()) + '\n')
        next_call = max(next_call + INTERVAL, time.time())
        time.sleep(max(0, next_call - time.time()))
    except:  # stop with ^C or close window
        break

### wrap up ###
output.flush()
output.close()
with open('in_fast_mode.ini','w') as config_file:
    config_file.write('0')
