from datetime import datetime
import time
import logging
import Tkinter
import sched

#from Mux_Box import Mux_Box

class slow_test:
    def __init__(self, sample_list, lock_in_addr, INTERVAL = 60, WAIT_TIME = 3, testname = 'longlong_slow',
                 print_ch = 'console', Tk_output = None, Tk_status = None, Tk_fast_sample = None):
        self.name_prefix = testname
        self.sample_list = set(sample_list)
        #self.box = Mux_Box(lock_in_addr,WAIT_TIME)
        self.output_files = [None] * 17
        self.intervals = [INTERVAL] * 17
        self.next_call = [None] * 17
        
        self.print_ch = print_ch
        self.Tk_output = Tk_output
        self.Tk_status = Tk_status
        self.Tk_fast_sample = Tk_fast_sample
        self._to_stop = True

        self.scheduler = sched.scheduler(time.time, time.sleep)

    def initialize(self):
        if self.print_ch == 'console':
            print 'Initializing slow measurement...'
        elif self.print_ch == 'Tk':
            self.Tk_status.write('Initializing slow measurement...')
        #for sample in self.sample_list:
            #self.box.Set_Sample(sample)
        self.t0 = time.clock();
        
    def add_one_to_measurement(self, sample):
        self.sample_list.add(sample)
        if self.output_files[sample] == None:
            filename = ('%s_sample%i_%s.txt' % (self.name_prefix, sample, str(datetime.now()).replace(':','-')))
            self.output_files[sample] = open(filename,'a')
            self.output_files[sample].write('t\tCH1\tCH2\ttimestamp\n')
        if self.next_call[sample] == None:
            self.next_call[sample] = self.scheduler.enter(0,1,self.do_one_measurement,(sample,))
    
    def remove_one_from_measurement(self, sample):
        if self.next_call[sample] != None:
            self.scheduler.cancel(self.next_call[sample])
            self.next_call[sample] = None
        self.sample_list.remove(sample)
    
    def do_one_measurement(self, sample):
        if self._to_stop:
            self.next_call[sample] = None
            for i in self.sample_list:
                if self.next_call[i] != None:
                    self.scheduler.cancel(self.next_call[i])
                    self.next_call[i] = None
            return
        
        if sample in self.sample_list:
            self.next_call[sample] = self.scheduler.enter(self.intervals[sample], 1, self.do_one_measurement, (sample,))
        else:
            self.next_call[sample] = None
        if self.print_ch == 'console':
            try:
                config_file = open('in_fast_mode.ini','r')
                idx_to_ignore = int(config_file.readline())
                config_file.close()
            except IOError:
                pass
        elif self.print_ch == 'Tk':
            idx_to_ignore = int(self.Tk_fast_sample.get())
        if sample == idx_to_ignore:
            return
            
        # actually set and measure the sample
        if self.print_ch == 'console':
            print ('Measuring sample %i' % sample),
        elif self.print_ch == 'Tk':
            self.Tk_status.write('Measuring sample %i' % sample)
        try:
            #self.box.Set_Sample(sample)
            #result = self.box.Read(sample)
            time.sleep(0.5)
            result = str(time.time())
            line = str(time.clock()-self.t0) + "\t" + result
            if self.print_ch == 'console': print line
            elif self.print_ch == 'Tk':
                self.Tk_output.write(line)
            self.output_files[sample].write(line + '\t' + str(datetime.now()) + '\n')
            self.output_files[sample].flush()
        except:
            self._to_stop = True
            logging.exception('Stopped when trying to measure %i at %s' % (sample, datetime.now()))
        if self.print_ch == 'Tk':
            self.Tk_status.write('Slow measurement running...')

    def main_test_loop(self):
        if self.print_ch == 'console':
            print 'Slow measurement running...'
        elif self.print_ch == 'Tk':
            self.Tk_status.write('Slow measurement running...')

        for sample in self.sample_list:
            self.add_one_to_measurement(sample)
            
        self.scheduler.run()
        self.wrap_up()

    def wrap_up(self):
        if self.print_ch == 'console':
            print 'Wrapping up slow measurement...'
        elif self.print_ch == 'Tk':
            self.Tk_status.write('Wrapping up slow measurement...')
        for sample in range(1,17):
            if self.output_files[sample] != None:
                self.output_files[sample].flush()
                self.output_files[sample].close()
                self.output_files[sample] = None
        if self.print_ch == 'Tk':
            self.Tk_status.write('Idle...')

if __name__ == "__main__":
    logging.basicConfig(filename = 'slow_test_errors.log', level=logging.ERROR)
    test = slow_test(set([2,3,4]), "GPIB1::11::INSTR", INTERVAL = 15)
    test.initialize()
    test._to_stop = False
    test.main_test_loop()
