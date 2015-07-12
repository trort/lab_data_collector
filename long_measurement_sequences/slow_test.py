from datetime import datetime
import time
import visa
import logging
import Tkinter
import sched

from Mux_Box import Mux_Box

class slow_test:
    def __init__(self, sample_list, lock_in_addr, INTERVAL = 60, WAIT_TIME = 3, testname = 'longlong_slow',
                 print_ch = 'console', Tk_window  = None):
        self.name_prefix = testname
        self.SAMPLES = sample_list # index of ALL samples to measure
        rm = visa.ResourceManager();
        lockin = rm.open_resource(lock_in_addr);
        self.box = Mux_Box(lockin,INTERVAL,WAIT_TIME)
        self.print_ch = print_ch
        self.window = Tk_window
        self._to_stop = True

    def initialize(self):
        if self.print_ch == 'console':
            print 'Initializing slow measurement...'
        elif self.print_ch == 'Tk':
            self.window.labelVariable.set('Initializing slow measurement...')
        self.output_files = {}
        for sample in self.SAMPLES:
            filename = ('%s_sample%i_%s.txt' % (self.name_prefix, sample, str(datetime.now()).replace(':','-')))
            self.output_files[sample] = open(filename,'a')
            self.output_files[sample].write('t\tCH1\tCH2\ttimestamp\n')
        for sample in self.SAMPLES:
            self.box.Set_Sample(sample)
        self.t0 = time.clock();
        self.idx_to_ignore = 0
        self.scheduler = sched.scheduler(time.time, time.sleep)
        logging.basicConfig(filename = 'slow_test_errors.log', level=logging.ERROR)
    
    def do_one_measurement(self, sample):
        if self._to_stop: return
        
        self.scheduler.enter(self.box.interval, 1, self.do_one_measurement, (sample,))
        try:
            config_file = open('in_fast_mode.ini','r')
            self.idx_to_ignore = int(config_file.readline())
            config_file.close()
        except IOError:
            pass
        if sample == self.idx_to_ignore:
            return
            
        # actually set and measure the sample
        if self.print_ch == 'console':
            print ('Measuring sample %i' % sample),
        elif self.print_ch == 'Tk':
            self.window.labelVariable.set('Measuring sample %i at %s' % sample, str(datetime.now()))
        try:
            self.box.Set_Sample(sample)
            result = self.box.Read(sample)
            line = str(time.clock()-self.t0) + "\t" + result
            if self.print_ch == 'console': print line
            elif self.print_ch == 'Tk':
                self.window.text['state'] = 'normal'
                self.window.text.insert('end', str(sample) + '\t' + line + '\n')
                self.window.text.delete('1.0', 'end -20 lines')
                self.window.text['state'] = 'disabled'
            self.output_files[sample].write(line + '\t' + str(datetime.now()) + '\n')
            self.output_files[sample].flush()
        except:
            self._to_stop = True
            logging.exception('Stopped when trying to measure %i' % sample)

    def main_test_loop(self):
        if self.print_ch == 'console':
            print 'Slow measurement running...'
        elif self.print_ch == 'Tk':
            self.window.labelVariable.set('Slow measurement running...')
            
        for sample in self.SAMPLES:
            self.scheduler.enter(0,1,self.do_one_measurement,(sample,))
        self.scheduler.run()
        self.wrap_up()

    def wrap_up(self):
        if self.print_ch == 'console':
            print 'Wrapping up slow measurement...'
        elif self.print_ch == 'Tk':
            self.window.labelVariable.set('Wrapping up slow measurement...')
        for sample in self.SAMPLES:
            self.output_files[sample].flush()
            self.output_files[sample].close()
        if self.print_ch == 'Tk':
            self.window.labelVariable.set('Idle...')

if __name__ == "__main__":
    test = slow_test([2,3,4], "GPIB1::11::INSTR", INTERVAL = 15)
    test.initialize()
    test._to_stop = False
    test.main_test_loop()
