from datetime import datetime
import time
import visa
from collections import deque
import numpy
import logging

MAX_FAST_INTERVAL = 3
MAX_FAST_FREQ = 3

RANGE_TABLE = [2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9,
               500e-9, 1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6,
               100e-6, 200e-6, 500e-6, 1e-3, 2e-3, 5e-3, 10e-3,
               20e-3, 50e-3, 100e-3, 200e-3, 500e-3, 1]

class fast_test:
    def __init__(self, sample, lock_in_addr, INTERVAL = 0, init_freq = 43, testname = 'longlong_fast',
                 print_ch = 'console', Tk_output = None, Tk_status = None):
        self.sample_no = sample
        self.TESTNAME = testname
        self.interval = INTERVAL #in sec
        self.freq = init_freq
        rm = visa.ResourceManager();
        self.lockin = rm.open_resource(lock_in_addr);
        self.lockin.timeout = 1000
        self.print_ch = print_ch
        self.Tk_output = Tk_output
        self.Tk_status = Tk_status
        self.SLOW_FREQ = 1.3
        self._to_stop = True
        self._auto_tc = False
        self._last_point = False
        
        self.time_queue = deque()
        self.result_queue = deque()
        
        self.sense = -1

    def initialize(self):
        if self.print_ch == 'console':
            print 'Initializing fast measurement...'
            open('in_fast_mode.ini','w').write(str(self.sample_no))
        elif self.print_ch == 'Tk':
            self.Tk_status.write('Initializing fast measurement...')
            self.Tk_output.write('++++++++++++++++++++++++++++++++')
        self.lockin.write("FREQ %f" % self.freq)
        time.sleep(2)
        FILENAME = ('%s_sample%i_%s.txt' % (self.TESTNAME, self.sample_no, str(datetime.now()).replace(':','-')))
        self.output = open(FILENAME,'a')
        self.output.write('t\tCH1\tCH2\tfreq\ttimestamp\n')
        
        self.time_queue.clear()
        self.result_queue.clear()
        
        while True:
            try:
                self.lockin.read()
            except:
                break
        
        self.t0 = time.clock();

    def do_one_measurement(self):
        if self.interval < 0.05:
            CH1 = self.lockin.ask("OUTP?1").strip()
            CH2 = 0
        else:
            result = self.lockin.ask("SNAP?1,2").strip()
            CH1,CH2 = result.split(',')
        #CH1 = float(time.time())
        #CH2 = 0
        t = float(time.clock()-self.t0)
        CH1 = float(CH1)
        CH2 = float(CH2)
        #result = self.lockin.ask("OUTP?1").strip()
        #result = math.exp(-(t/1E4)**(0.5)) + 10
        timestamp = datetime.now()
        line = "t = %g, v = %g,%g (%s)" % (t,CH1,CH2,timestamp.time())
        if self.print_ch == 'console': print line
        elif self.print_ch == 'Tk': self.Tk_output.write(line)
        self.output.write("%g\t%g\t%g\t%g\t%s\n" % (t,CH1,CH2,self.freq,timestamp))
        
        # auto tc and freq
        self.time_queue.append(t)
        self.result_queue.append(CH1)
        if len(self.time_queue) > 100:
            self.time_queue.popleft()
            self.result_queue.popleft()
            if self._auto_tc and (self.interval < MAX_FAST_INTERVAL or self.freq > MAX_FAST_FREQ):
                slope, intersect = numpy.polyfit(self.time_queue,self.result_queue,1)
                tau = CH1 / slope
                new_interval = min(abs(tau * 0.00003),MAX_FAST_INTERVAL)
                if new_interval > self.interval:
                    self.interval = min(self.interval * 1.001, new_interval)
                new_freq = max(3 / self.interval, MAX_FAST_FREQ)
                if new_freq < self.freq: #change freq
                    self.freq = max(self.freq * 0.999, new_freq)
                    self.lockin.write("FREQ %f" % self.freq)
            
                self.Tk_status.write('interval is %g, freq is %g, tau is %gs' % (self.interval,self.freq,tau))
        else:
            self.Tk_status.write('interval is %g, freq is %g, tau is unknown' % (self.interval,self.freq))
        
        # auto sense
        if self.interval > 0.5:
            if self.sense == -1:
                self.sense = int(self.lockin.ask('SENS?'))
            sense_range = RANGE_TABLE[self.sense]
            if CH1 > 0.95*sense_range and self.sense < 26:
                self.sense += 1
                self.lockin.write('SENS %i' % self.sense)
            elif CH1 < 0.3*sense_range and self.sense > 0:
                self.sense -= 1
                self.lockin.write('SENS %i' % self.sense)

    def main_test_loop(self):
        self.initialize()
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
        if self._last_point:
            self.lockin.write('FREQ %f' % self.SLOW_FREQ)
            time.sleep(6/self.SLOW_FREQ)
            self.do_one_measurement()
            self.lockin.write('FREQ %f' % self.freq)
        
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
