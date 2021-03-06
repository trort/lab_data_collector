﻿# -*- coding: utf-8-sig -*-
from datetime import datetime
import time
from collections import deque
import numpy
import logging
import sched

from Mux_Box import Mux_Box

MAX_SLOW_INTERVAL = 600

class slow_test:
    def __init__(self, sample_list, lock_in_addr, INTERVAL = 60, WAIT_TIME = 3, FREQ = 1.3, testname = 'longlong_slow',
                 print_ch = 'console', Tk_output = None, Tk_status = None, DMM_addr = None):
        self.name_prefix = testname
        self.sample_list = set(sample_list)
        self.wait_time = WAIT_TIME
        self.default_interval = INTERVAL
        self.box = Mux_Box(lock_in_addr,DMM_addr,WAIT_TIME)
        self.output_files = [None] * 17
        self.intervals = [None] * 17
        self.next_call = [None] * 17
        self.idx_to_ignore = 0
        self.freq = FREQ
        self.t0 = None
        
        self.print_ch = print_ch
        self.Tk_output = Tk_output
        self.Tk_status = Tk_status
        self._to_stop = True
        self._auto_tc = True
        
        self.time_queue = [deque()] * 17
        self.result_queue = [deque()] *17

        self.scheduler = sched.scheduler(time.time, time.sleep)

    def initialize(self):
        if self.print_ch == 'console':
            print 'Initializing slow measurement...'
        elif self.print_ch == 'Tk':
            self.Tk_status.write('Initializing slow measurement...')
            self.Tk_output.write('++++++++++++++++++++++++++++++++')
        self.box.Set_Freq(self.freq)
        for sample in self.sample_list:
            if self.print_ch == 'Tk':
                self.Tk_status.write('Setting up sample %i' % sample)
            self.box.Set_Sample(sample)
        for sample in range(1,17):
            self.time_queue[sample].clear()
            self.result_queue[sample].clear()
        self.t0 = time.clock();
        
    def add_one_to_measurement(self, sample):
        self.sample_list.add(sample) #1
        if self.output_files[sample] == None:
            filename = ('%s_sample%i_%s.txt' % (self.name_prefix, sample, str(datetime.now()).replace(':','-')))
            self.output_files[sample] = open(filename,'a') #2
            self.output_files[sample].write('t\tTEMP\tCH1\tCH2\ttimestamp\n')
        if self.next_call[sample] == None:
            self.next_call[sample] = self.scheduler.enter(0,1,self.do_one_measurement,(sample,)) #3
        if self.intervals[sample] == None:
            self.intervals[sample] = self.default_interval #4
        if self.print_ch == 'Tk':
            self.Tk_status.write('Sample %i added' % sample)
    
    def remove_one_from_measurement(self, sample):
        if self.next_call[sample] != None:
            self.scheduler.cancel(self.next_call[sample])
            self.next_call[sample] = None #3
        self.intervals[sample] = None #4
        self.time_queue[sample].clear()
        self.result_queue[sample].clear()
        self.sample_list.remove(sample) #1
        if self.print_ch == 'Tk':
            self.Tk_status.write('Sample %i removed' % sample)
    
    def do_one_measurement(self, sample):
        # stop measurement
        if self._to_stop:
            if self.print_ch == 'console':
                print 'Stopping slow measurement...'
            elif self.print_ch == 'Tk':
                self.Tk_status.write('Stopping slow measurement...')
            self.next_call[sample] = None
            for i in self.sample_list:
                if self.next_call[i] != None:
                    self.scheduler.cancel(self.next_call[i])
                    self.next_call[i] = None
            return

        # print status
        if self.print_ch == 'console':
            print ('Measuring sample %i...' % sample)
        elif self.print_ch == 'Tk':
            self.Tk_status.write('Measuring sample %i...' % sample)
        
        # check list
        if sample in self.sample_list:
            self.next_call[sample] = self.scheduler.enter(self.intervals[sample], 1, self.do_one_measurement, (sample,))
        else:
            self.next_call[sample] = None
        
        # check whether to ignore
        if self.print_ch == 'console':
            try:
                config_file = open('in_fast_mode.ini','r')
                self.idx_to_ignore = int(config_file.readline())
                config_file.close()
            except IOError:
                pass
        elif self.print_ch == 'Tk':
            pass # handled in the GUI logic
        if sample == self.idx_to_ignore:    # do ignore
            self.time_queue[sample].clear()
            self.result_queue[sample].clear()

            # only measure temperature
            try:
                temperature = self.box.Read_temp()
            except:
                temperature = 0
            t = float(time.clock()-self.t0)
            timestamp = datetime.now()
            line = "Sample %i: t = %g, T = %g, v = N/A (%s)" % (sample,t,temperature,timestamp.time())
            if self.print_ch == 'console': print line
            elif self.print_ch == 'Tk': self.Tk_output.write(line)
            self.output_files[sample].write("%g\t%g\t0\t0\t%s\n" % (t,temperature,timestamp))
            self.output_files[sample].flush()
            return
            
        # actually set and measure the sample
        try:
            self.box.Set_Sample(sample)
            CH1,CH2 = self.box.Read(sample)
            temperature = self.box.Read_temp()
            #time.sleep(self.wait_time)
            #result = float(time.time())
            t = float(time.clock()-self.t0)
            timestamp = datetime.now()
            line = "Sample %i: t = %g, T = %g, v = %g,%g (%s)" % (sample,t,temperature,CH1,CH2,timestamp.time())
            if self.print_ch == 'console': print line
            elif self.print_ch == 'Tk': self.Tk_output.write(line)
            self.output_files[sample].write("%g\t%g\t%g\t%g\t%s\n" % (t, temperature, CH1,CH2,timestamp))
            self.output_files[sample].flush()
        except:
            self._to_stop = True
            logging.exception('Stopped when trying to measure %i at %s' % (sample, datetime.now()))
            return
        
        # auto_tc
        self.time_queue[sample].append(t)
        self.result_queue[sample].append(CH1)
        if len(self.time_queue[sample]) > 20:
            self.time_queue[sample].popleft()
            self.result_queue[sample].popleft()
            if self._auto_tc and self.intervals[sample] < MAX_SLOW_INTERVAL:
                slope, intersect = numpy.polyfit(self.time_queue[sample],self.result_queue[sample],1)
                new_interval = min(abs(CH1 * 0.0001 / slope), MAX_SLOW_INTERVAL)
                if new_interval > self.intervals[sample]:
                    self.intervals[sample] = min(self.intervals[sample] * 1.05, new_interval)
        
        # wait for next
        if self.print_ch == 'Tk':
            self.Tk_status.write('Waiting for next query in queue...')

    def main_test_loop(self):
        self.initialize()
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
                self.output_files[sample] = None #2
        for sample in range(1,17):
            if self.intervals[sample] != None:
                self.intervals[sample] = None
        self.t0 = None
        if self.print_ch == 'Tk':
            self.Tk_status.write('Idle...')
            self.Tk_output.write('===============================')

if __name__ == "__main__":
    logging.basicConfig(filename = 'slow_test_errors.log', level=logging.ERROR)
    test = slow_test(set([2,3,4]), "GPIB0::11::INSTR", INTERVAL = 15)
    test.initialize()
    test._to_stop = False
    test.main_test_loop()
