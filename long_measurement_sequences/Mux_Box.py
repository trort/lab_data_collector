from datetime import datetime
import visa

class Mux_Box:
    def __init__(self, device):
        self.device = device
        
    def Init(self):
        pass
        
    def Set_Sample(self, idx):
        for i in range(4):
            self.device.write("AUXV %i,%.3f" % (i+1, 5 if (idx-1) & (1<<i) else 0))
        self.device.write("AGAN")
        
    def Read(self):
        [a,b] = self.device.ask("SNAP?1,2").strip().split(',')
        line = a + "\t" + b
        return line
