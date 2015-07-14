from datetime import datetime
import time
#import visa
import logging
import Tkinter

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
        logging.basicConfig(filename = 'fast_test_errors.log', level=logging.ERROR)

    def initialize(self):
        if self.print_ch == 'console':
            print 'Initializing fast measurement...'
            open('in_fast_mode.ini','w').write(str(self.sample_no))
        elif self.print_ch == 'Tk':
            self.Tk_status.set('Initializing fast measurement...')
        FILENAME = ('%s_sample%i_%s.txt' % (self.TESTNAME, self.sample_no, str(datetime.now()).replace(':','-')))
        self.output = open(FILENAME,'a')
        self.output.write('t\tCH1\ttimestamp\n')
        self.t0 = time.clock();

    def do_one_measurement(self):
        t = float(time.clock()-self.t0)
        #result = self.lockin.ask("OUTP?1").strip()
        result = str(time.time())
        line = str(t) + "\t" + result
        if self.print_ch == 'console': print line
        elif self.print_ch == 'Tk':
            self.Tk_output['state'] = 'normal'
            self.Tk_output.insert('end', line + '\n')
            self.Tk_output.delete('1.0', 'end -20 lines')
            self.Tk_output['state'] = 'disabled'
        self.output.write(line + "\t" + str(datetime.now()) + '\n')

    def main_test_loop(self):
        if self.print_ch == 'console':
            print 'Fast measurement running...'
        elif self.print_ch == 'Tk':
            self.Tk_status.set('Fast measurement running...')
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
            self.Tk_status.set('Wrapping up fast measurement...')
        self.output.flush()
        self.output.close()
        if self.print_ch == 'Tk':
            self.Tk_status.set('Idle...')

if __name__ == "__main__":
    test = fast_test(2, "GPIB1::9::INSTR", INTERVAL = 0.2)
    test.initialize()
    test._to_stop = False
    test.main_test_loop()
