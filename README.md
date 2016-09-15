Data collection scripts for the transport lab
======
This intends to be an archieve of the common scripts used in data collection. The code should be intuitive enough that you can edit it to make the code for your only measurements.

The subfolder `long_measurement_sequences` contains the scripts used specifically for the MTDM unit. Check the folder for details.

This folder includes:
* `simple_sweep.py` The most simple script. Just sweeping one variable  *v* in the desired range and record another variable *ans* during the sweep. For simple data recording, you can sweep time from 0 to a large number.
* `auto_tc.py` Collects time transient data. Also adjusts the time interval between measurements automatically according to the transient slope. Mostly used for transient photoconductivity measurements.
* `lockin_buffer.py` Used only when you need to read data from SRS830 lock-in buffer with the binary mode. Check the SR830 manual for storing data in the buffer. This mode can transfer data at ~2ms/query, while normal rate is ~17ms/query.
* `bin_verify.py` Just verifies the binary mode functions of `lockin_buffer.py` by comparing the data transfered with the binary mode and ASCII mode.
* `cycled.py` Used to measure the repeated transient when LED is turned on and off repeatedly with fixed intervals. 
* `auto_cycle.py` Also used for measurements when LED is turned on and off repeatedly, but not with fixed time intervals. LED is toggled when the measured value reaches the threshold maximum or minimum.

The text file `device controls.txt` contains the common GPIB commands for all data collection instruments in our lab. Use this file to create script for new measurements.

-------------

All scripts rely on [PyVisa](https://pyvisa.readthedocs.io/) to communicate with the GPIB interface. Note that GPIB driver needs to be installed, either using the NI version or the Agilent version.
To test if PyVisa work properly, simply type "import visa" in Python prompt. An error message will appear if PyVisa is not installed properly.
