#parameters for users
OUTPUT_FILENAME = "sweep.txt"
ADDRESS = "GPIB0::14"

### DO NOT CHANGE ANYTHING BELOW ###

# libs
from datetime import datetime
import time
import visa

# init
output = open(OUTPUT_FILENAME,"w");
device = visa.instrument("GPIB0::14");
