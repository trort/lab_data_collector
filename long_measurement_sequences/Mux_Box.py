# -*- coding: utf-8-sig -*-
from datetime import datetime
import visa_test as visa
import time

RANGE_TABLE = [2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9,
               500e-9, 1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6,
               100e-6, 200e-6, 500e-6, 1e-3, 2e-3, 5e-3, 10e-3,
               20e-3, 50e-3, 100e-3, 200e-3, 500e-3, 1]

class Mux_Box:
    def __init__(self, device_addr, DMM_addr = None, stablize_time = 3):
        rm = visa.ResourceManager();
        self.device = rm.open_resource(device_addr);
        self.device.timeout = 1000
        self.sensitivity = {}
        self.wait = stablize_time # in sec
        
        while True:
            try:
                self.device.read()
            except:
                break

        self.last_sense = int(self.device.ask('SENS?'))

        # DMM setup
        self.DMM = rm.open_resource(DMM_addr);
        self.DMM.write(":CONF:FRES")
        self.DMM.write(":FRES:RANG:6e3")
    
    def Set_Freq(self, freq):
        self.device.write("FREQ %f" % freq)

    def Read_temp(self):
        # for some reason, need to repeat the following 2 lines every time to recover from bad measurement data
        self.DMM.write(":CONF:FRES")
        self.DMM.write(":FRES:RANG:6e3")
        res = float(self.DMM.ask(":READ?").strip())
        temp = ((res - 1000)/39.03) * 10
        return temp
            
    def Set_Sample(self, idx):
        for i in range(4):
            self.device.write("AUXV %i,%.3f" % (i+1, 5 if (idx-1) & (1<<i) else 0))
        # change range
        if idx in self.sensitivity:
            if self.last_sense != self.sensitivity[idx]:
                self.device.write('SENS %i' % self.sensitivity[idx])
                self.last_sense = self.sensitivity[idx]
            time.sleep(self.wait)
        else:
            self.sensitivity[idx] = self.last_sense
        
    def Read(self, idx):
        # take data
        a,b = self.device.ask("SNAP?1,2").strip().split(',')
        #line = a + "\t" + b
        
        ## adjust range
        sense_range = RANGE_TABLE[self.sensitivity[idx]]
        if abs(float(a)) > 0.95*sense_range and self.sensitivity[idx] < 26:
            self.sensitivity[idx] += 1
        elif abs(float(a)) < 0.3*sense_range and self.sensitivity[idx] > 0:
            self.sensitivity[idx] -= 1
        
        return float(a),float(b)

    def find_range(self):
        if self.last_sense == -1:
            sense = int(self.device.ask('SENS?'))
        else:
            sense = self.last_sense
        while True:
            sense_range = RANGE_TABLE[sense]
            time.sleep(self.wait)
            value = abs(float(self.device.ask('OUTP?1')))
            if value > 0.95*sense_range and sense < 26:
                sense += 1
                self.device.write('SENS %i' % sense)
            elif value < 0.3*sense_range and sense > 0:
                sense -= 1
                self.device.write('SENS %i' % sense)
            else:
                break
        self.last_sense = sense
        return sense
