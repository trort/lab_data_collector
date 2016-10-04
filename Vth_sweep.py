from datetime import datetime
import time
import visa

FILENAME = "IGZO_0.12_new_sample_overnight_run";
I_LIMIT = 0.001;
rm = visa.ResourceManager();
device = rm.open_resource("GPIB0::20");
power_source = rm.open_resource("GPIB0::5");
V_DS = 80;

time_list = [10, 30, 100, 300, 1000, 3000, 10000] #time points to check Vth

t0 = time.time();
t_offset = 0;

def Init():
    #device.write("smua.reset()");
    device.write("smub.source.limiti = " + str(I_LIMIT)); # b for gate
    device.write("smua.source.levelv = " + str(V_DS)); # a for measurement
    power_source.write("OUTPut:STATe OFF");

def Turn_On_LED():
    global t_offset
    power_source.write("OUTPut:STATe ON");
    t_offset = time.time()-t0

def Turn_Off_LED():
    global t_offset
    power_source.write("OUTPut:STATe OFF");
    t_offset = time.time()-t0

def Read_Leakage():
    return device.ask("print(smub.measure.i())").strip()

def Set_Voltage(v):
    device.write("smub.source.levelv = " + str(v));

def Read_Current():
    return device.ask("print(smua.measure.i())").strip()

def End():
    power_source.write("OUTPut:STATe OFF");
    print "Program done!"
    
def Gate_Sweep(min_bias = -40, max_bias = 80, interval = 1, wait_time = 0.00):
    bias_points = range(0, min_bias, -interval) + range(min_bias, max_bias, interval) + range(max_bias, min_bias, -interval) + range(min_bias, interval, interval)
    output = open(FILENAME + '_t=' + str(time.time()-t0) + '.txt',"a");
    print 'Sweeping at t = ' + str(time.time()-t0)
    for v in bias_points:
        Set_Voltage(v);
        time.sleep(wait_time);
        leakage = Read_Leakage();
        ans = Read_Current();
        line = str(time.time()-t0-t_offset) + "\t" + str(v) + "\t" + str(leakage) + "\t" + str(ans) + "\t" + str(datetime.now()) + "\n";
        print str(v) + "\t" + ans;
        output.write(line);
    output.close()
    Set_Voltage(0)
    print 'Sweeping finished'

# main sequence
Init()
Gate_Sweep()

Turn_On_LED()

idx = 0;
last_call = t0
while idx < len(time_list):
    next_call = max(last_call + time_list[idx] + t_offset, time.time())
    idx += 1
    time.sleep(max(0, next_call - time.time()))
    Gate_Sweep()

Turn_Off_LED()

idx = 0;
last_call = t0
while idx < len(time_list):
    next_call = max(last_call + time_list[idx] + t_offset, time.time())
    idx += 1
    time.sleep(max(0, next_call - time.time()))
    Gate_Sweep()

End();
