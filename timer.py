from datetime import datetime
import time

FILENAME = "test.txt"
output = open(FILENAME,"w");
t0 = time.clock();


def TakeData():
    reading = "0.000,0.000";
    t = time.clock() - t0;
    line = str(t) + " " + reading + " " + str(datetime.now()) + "\n";
    output.write(line);

def End():
    output.close();
    print "Program done!"

for i in range(10000):
    TakeData();
    time.sleep(0.00001);

End();
    
