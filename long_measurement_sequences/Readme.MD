Data collection program for the **Modular Time Division Multiplexer** unit
=================================
The design and details of the **Modular Time Division Multiplexer (MTDM)** unit can be found in our paper in production for *Review of Scientific Instruments*.

This program assumes that data is collected from two SRS830 lock-in amplifiers. The main executable is the `longlong_test_GUI.pyw`, with a GUI for setting up and monitoring the measurement. Alternatively, one can run the program in console from the dedicated mode script `fast_test.py` and multiplexed mode script `slow_test.py`. Note that the console mode requires modifying the script to change the configurations. Other files are:
* `open_file_and_plot.py` Simply plot one colume of the file as a function of the first colume. Modify the colume number to the one you need.
* `Mux_Box.py` Used by the multiplexed mode script `slow_test.py`.
* `thread_safe_tk_widgets.py` Called by the main executable `longlong_test_GUI.pyw` to enable data collection faster than `tk` GUI refresh rate.
* `visa_test.py` Only for debugging the program without the need of connecting the lock-ins.
* `plot_test.py` An attempt to plot the data during measurements. Only works when data collection rate is not higher than the maximum refresh rate of the interface (not working for fast initial transients!).