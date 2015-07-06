from datetime import datetime
import time
import visa

from Mux_Box import Mux_Box

TESTNAME = "longlong_slow"
SAMPLES = [2,3,4] # index of ALL samples to measure
INTERVAL = 20 #in sec
rm = visa.ResourceManager();
lockin = rm.open_resource("GPIB1::11::INSTR");
box = Mux_Box(lockin,INTERVAL,5);

### initialize ###
output_files = {}
for sample in SAMPLES:
    filename = ('%s_sample%i_%s.txt' % (TESTNAME, sample, str(datetime.now()).replace(':','-')))
    output_files[sample] = open(filename,'a')
    output_files[sample].write('t\tCH1\tCH2\ttimestamp\n')
t0 = time.clock();

### measurements ###
while True:
    try:
        for sample in SAMPLES:
            print ('Measuring sample %i' % sample),
            box.Set_Sample(sample)
            result = box.Read(sample)
            line = str(time.clock()-t0) + "\t" + result
            print line
            output_files[sample].write(line + '\t' + str(datetime.now()) + '\n')
            output_files[sample].flush()
    except (KeyboardInterrupt, SystemExit):
        break

### wrap up ###
for sample in SAMPLES:
    output_files[sample].flush()
    output_files[sample].close()       
