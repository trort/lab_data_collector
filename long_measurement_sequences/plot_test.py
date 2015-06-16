from datetime import datetime
import time
import visa
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

### basic parameters ###
TESTNAME = "longlong_test_plot"
INTERVAL = 1000 #in milisec
MAX_PLOT_PTS = 1000
UPDATE_FREQ = 10
rm = visa.ResourceManager();
lockin = rm.open_resource("GPIB1::11::INSTR");

### initialize ###
FILENAME = TESTNAME + '_' + str(datetime.now()).replace(':','-') + ".txt"
output = open(FILENAME,'w')
t0 = time.clock();

### plot ###
x_data = deque([])
y_data = deque([])
z_data = deque([])
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax1.set_title('Fast Test')

### measurements ###
def measurement(i):
    t = float(time.clock()-t0)
    result = float(lockin.ask("OUTP?1"))
    line = str(t) + "\t" + str(result) + "\t" + str(datetime.now())
    print line
    output.write(line + '\n')
    x_data.append(t)
    if len(x_data) > MAX_PLOT_PTS:
        x_data.popleft()
    y_data.append(result)
    if len(y_data) > MAX_PLOT_PTS:
        y_data.popleft()
    z_data.append(result/2.0)
    output.flush()
    ax1.clear()
    ax1.plot(x_data,y_data,x_data,z_data)

ani = animation.FuncAnimation(fig,measurement,interval = INTERVAL)
plt.show()       
