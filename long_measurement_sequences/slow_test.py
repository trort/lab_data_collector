from datetime import datetime
import time
import logging
import Tkinter
import sched

#from Mux_Box import Mux_Box

class slow_test:
    def __init__(self, sample_list, lock_in_addr, INTERVAL = 60, WAIT_TIME = 3, testname = 'longlong_slow',
                 print_ch = 'console', Tk_output = None, Tk_status = None):
        self.name_prefix = testname
        self.sample_list = sample_list # index of ALL samples to measure
        #self.box = Mux_Box(lock_in_addr,WAIT_TIME)
        self.output_files = {}
        self.intervals = [INTERVAL] * 17
        
        self.print_ch = print_ch
        self.Tk_output = Tk_output
        self.Tk_status = Tk_status
        self._to_stop = True

    def initialize(self):
        if self.print_ch == 'console':
            print 'Initializing slow measurement...'
        elif self.print_ch == 'Tk':
            self.Tk_status.set('Initializing slow measurement...')
        #for sample in self.sample_list:
            #self.box.Set_Sample(sample)
        self.t0 = time.clock();
        self.idx_to_ignore = 0
        self.scheduler = sched.scheduler(time.time, time.sleep)
        logging.basicConfig(filename = 'slow_test_errors.log', level=logging.ERROR)
        
    def add_one_sample(self, sample):
        filename = ('%s_sample%i_%s.txt' % (self.name_prefix, sample, str(datetime.now()).replace(':','-')))
        self.output_files[sample] = open(filename,'a')
        self.output_files[sample].write('t\tCH1\tCH2\ttimestamp\n')
        self.scheduler.enter(0,1,self.do_one_measurement,(sample,))
    
    def remove_one_sample(self, sample):
        self.output_files[sample].flush()
        self.output_files[sample].close()
    
    def do_one_measurement(self, sample):
        if self._to_stop:
            while not self.scheduler.empty():
                self.scheduler.cancel(self.scheduler.queue[0])
            return
        
        self.scheduler.enter(self.intervals[sample], 1, self.do_one_measurement, (sample,))
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
            self.Tk_status.set('Measuring sample %i' % sample)
        try:
            #self.box.Set_Sample(sample)
            #result = self.box.Read(sample)
            result = str(time.time())
            line = str(time.clock()-self.t0) + "\t" + result
            if self.print_ch == 'console': print line
            elif self.print_ch == 'Tk':
                self.Tk_output['state'] = 'normal'
                self.Tk_output.insert('end', str(sample) + '\t' + line + '\n')
                self.Tk_output.delete('1.0', 'end -20 lines')
                self.Tk_output['state'] = 'disabled'
            self.output_files[sample].write(line + '\t' + str(datetime.now()) + '\n')
            self.output_files[sample].flush()
        except:
            self._to_stop = True
            logging.exception('Stopped when trying to measure %i at %s' % (sample, datetime.now()))

    def main_test_loop(self):
        if self.print_ch == 'console':
            print 'Slow measurement running...'
        elif self.print_ch == 'Tk':
            self.Tk_status.set('Slow measurement running...')
            
        for sample in self.sample_list:
            self.add_one_sample(sample)
        
        self.scheduler.run()
        self.wrap_up()

    def wrap_up(self):
        if self.print_ch == 'console':
            print 'Wrapping up slow measurement...'
        elif self.print_ch == 'Tk':
            self.Tk_status.set('Wrapping up slow measurement...')
        for sample in self.sample_list:
            self.remove_one_sample(sample)
        if self.print_ch == 'Tk':
            self.Tk_status.set('Idle...')

if __name__ == "__main__":
    test = slow_test([2,3,4], "GPIB1::11::INSTR", INTERVAL = 15)
    test.initialize()
    test._to_stop = False
    test.main_test_loop()
