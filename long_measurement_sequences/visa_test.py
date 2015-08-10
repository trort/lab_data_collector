import time

class TimeOutError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Device:
    def __init__(self,addr,freq = 43, sense = 20):
        self.addr = addr
        self.freq = freq
        self.sense = sense
        self.timeout = 25000
        
        self.t0 = time.clock();
        
    def ask(self, cmd):
        if cmd == 'FREQ?': return str(self.freq)
        if cmd == 'SENS?': return str(self.sense)
        
        t = float(time.clock()-self.t0)
        CH1 = 0.05
        CH2 = 0
        if cmd == 'OUTP?1':
            return str(CH1)
        if cmd == 'SNAP?1,2':
            return '%f,%f' % (CH1,CH2)
        
    def write(self, cmd):
        if cmd.startswith('FREQ '):
            self.freq = float(cmd[5:])
        if cmd.startswith('SENS '):
            self.sense = int(cmd[5:])
            
    def read(self):
        time.sleep(self.timeout/1000)
        raise TimeOutError(self.timeout)

class ResourceManager:
    def __init__(self):
        pass
        
    def open_resource(self,addr):
        device = Device(addr)
        return device