from datetime import datetime
import time
#import visa
from collections import deque
import numpy
import math
import logging

SLOW_FREQ = 1.3
MAX_FAST_INTERVAL = 3
MAX_FAST_FREQ = 3

class fast_test:
    def __init__(self, sample, lock_in_addr, INTERVAL = 0, testname = 'longlong_fast',
                 print_ch = 'console', Tk_output = None, Tk_status = None):
        self.sample_no = sample
        self.TESTNAME = testname
        self.interval = INTERVAL #in sec
        #rm = visa.ResourceManager();
        #self.lockin = rm.open_resource(lock_in_addr);
        self.print_ch = print_ch
        self.Tk_output = Tk_output
        self.Tk_status = Tk_status
        self._to_stop = True
        self._auto_tc = True
        
        self.time_queue = deque()
        self.result_queue = deque()

    def initialize(self):
        if self.print_ch == 'console':
            print 'Initializing fast measurement...'
            open('in_fast_mode.ini','w').write(str(self.sample_no))
        elif self.print_ch == 'Tk':
            self.Tk_status.write('Initializing fast measurement...')
            self.Tk_output.write('++++++++++++++++++++++++++++++++')
        FILENAME = ('%s_sample%i_%s.txt' % (self.TESTNAME, self.sample_no, str(datetime.now()).replace(':','-')))
        self.output = open(FILENAME,'a')
        self.output.write('t\tCH1\tfreq\ttimestamp\n')
        #self.freq = float(self.lockin.ask("FREQ?"))
        self.freq = 37.0
        self.t0 = time.clock();
        
        self.time_queue.clear()
        self.result_queue.clear()

    def do_one_measurement(self):
        t = float(time.clock()-self.t0)
        #result = self.lockin.ask("OUTP?1").strip()
        result = math.exp(-(t/1E4)**(0.5)) + 10
        timestamp = datetime.now()
        line = "t = %f, v = %f (%s)" % (t,result,timestamp.time())
        if self.print_ch == 'console': print line
        elif self.print_ch == 'Tk': self.Tk_output.write(line)
        self.output.write("%f\t%f\t%f\t%s\n" % (t,result,self.freq,timestamp))
        
        self.time_queue.append(t)
        self.result_queue.append(result)
        if len(self.time_queue) > 5:
            self.time_queue.popleft()
            self.result_queue.popleft()
            if self._auto_tc and self.interval < MAX_FAST_INTERVAL:
                slope, intersect = numpy.polyfit(self.time_queue,self.result_queue,1)
                new_interval = abs(result * 0.00001 / slope)
                self.interval = max(self.interval, min(new_interval,MAX_FAST_INTERVAL))
                new_freq = max(5 / self.interval, MAX_FAST_FREQ)
                if new_freq < self.freq: #change freq
                    self.freq = max(self.freq * 0.98, new_freq)
                    #self.device.write("FREQ %f" % self.freq)
            
                self.Tk_status.write('interval is %f, freq is %f' % (self.interval,self.freq))

    def main_test_loop(self):
        if self.print_ch == 'console':
            print 'Fast measurement running...'
        elif self.print_ch == 'Tk':
            self.Tk_status.write('Fast measurement running...')
        next_call = time.time()
        while not self._to_stop:
            try:
                self.do_one_measurement()
                next_call = max(next_call + self.interval, time.time())
                time.sleep(max(0, next_call - time.time()))
            except:  # stop with ^C or close window
                self._to_stop = True
                logging.exception('Stopped when trying to measure at %s' % str(datetime.now()))
        self.wrap_up()

    def wrap_up(self):
        if self.print_ch == 'console':
            print 'Wrapping up fast measurement...'
            open('in_fast_mode.ini','w').write('0')
        elif self.print_ch == 'Tk':
            self.Tk_status.write('Wrapping up fast measurement...')
        
        # last point at slow frequency
        #self.device.write('FREQ %f' % SLOW_FREQ)
        time.sleep(6/SLOW_FREQ)
        self.do_one_measurement()
        
        self.output.flush()
        self.output.close()
        if self.print_ch == 'Tk':
            self.Tk_status.write('Idle...')
            self.Tk_output.write('===============================')

if __name__ == "__main__":
    logging.basicConfig(filename = 'fast_test_errors.log', level=logging.ERROR)
    test = fast_test(2, "GPIB1::9::INSTR", INTERVAL = 0.2)
    test.initialize()
    test._to_stop = False
    test.main_test_loop()
