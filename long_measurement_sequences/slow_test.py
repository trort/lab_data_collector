from datetime import datetime
import time
import visa
import logging

from Mux_Box import Mux_Box

class slow_test:
    def __init__(self, sample_list, lock_in_addr, INTERVAL = 60, WAIT_TIME = 3, testname = 'longlong_slow'):
        self.name_prefix = testname
        self.SAMPLES = sample_list # index of ALL samples to measure
        rm = visa.ResourceManager();
        lockin = rm.open_resource(lock_in_addr);
        self.box = Mux_Box(lockin,INTERVAL,WAIT_TIME)

    def initialize(self):
        print 'Initializing slow measurement...'
        self.output_files = {}
        for sample in self.SAMPLES:
            filename = ('%s_sample%i_%s.txt' % (self.name_prefix, sample, str(datetime.now()).replace(':','-')))
            self.output_files[sample] = open(filename,'a')
            self.output_files[sample].write('t\tCH1\tCH2\ttimestamp\n')
        for sample in self.SAMPLES:
            self.box.Set_Sample(sample)
        self.t0 = time.clock();
        self.idx_to_ignore = 0
        logging.basicConfig(filename = 'slow_test_errors.log')

    def main_test_loop(self):
        print 'Slow measurement running...'
        while True:
            try:
                for sample in self.SAMPLES:
                    # check whether this sample should be ignored
                    try:
                        config_file = open('in_fast_mode.ini','r')
                        self.idx_to_ignore = int(config_file.readline())
                        config_file.close()
                    except IOError:
                        pass
                    if sample == self.idx_to_ignore:
                        continue
                    # actually set and measure the sample
                    print ('Measuring sample %i' % sample),
                    self.box.Set_Sample(sample)
                    result = self.box.Read(sample)
                    line = str(time.clock()-self.t0) + "\t" + result
                    print line
                    self.output_files[sample].write(line + '\t' + str(datetime.now()) + '\n')
                    self.output_files[sample].flush()
            except (KeyboardInterrupt, SystemExit):
                self.wrap_up()
            except:
                self.wrap_up()
                logging.exception('')

    def wrap_up(self):
        print 'Wrapping up slow measurement...'
        for sample in self.SAMPLES:
            self.output_files[sample].flush()
            self.output_files[sample].close()       

if __name__ == "__main__":
    test = slow_test([2,3,4], "GPIB1::11::INSTR", INTERVAL = 15)
    test.initialize()
    test.main_test_loop()
