import Tkinter
import ttk
import threading
import logging

import fast_test
import slow_test

class fast_frame(Tkinter.Frame):
    def __init__(self, parent, fast_sample_Variable):
        Tkinter.Frame.__init__(self, parent, bd=10)
        self.parent = parent
        self.fast_sample_Variable = fast_sample_Variable
        self.initialize()

    def initialize(self):
        # GUI part
        self.grid()
        
        captain_line = Tkinter.Label(self, text='Fast Measurement', font=("Helvetica", 16), anchor="w")
        captain_line.grid(column=0,row=0,columnspan=5)
        
        self.output_box = Tkinter.Text(self, undo = False, wrap='none', state='disabled',
                                 width = 60, height = 35)
        self.output_box.grid(column=0,row=1,columnspan=5,sticky='EW')
        
        initial_interval_Label = Tkinter.Label(self, text='Initial interval (sec):',anchor='e')
        initial_interval_Label.grid(column=0,row=5)
        self.initial_interval_Variable = Tkinter.StringVar()
        self.interval_select_box = ttk.Combobox(self, textvariable=self.initial_interval_Variable, state='readonly')
        self.interval_select_box.grid(column=1,row=5,sticky='EW')
        self.interval_select_box['values'] = ['0','0.05','0.1','0.3','1','3']
        self.initial_interval_Variable.set('0')
        
        sample_select_Label = Tkinter.Label(self, text='Fast mode sample:',anchor='e')
        sample_select_Label.grid(column=2,row=5)
        self.sample_select_box = ttk.Combobox(self, textvariable=self.fast_sample_Variable, state='readonly')
        self.sample_select_box.grid(column=3,row=5,sticky='EW')
        self.sample_select_box['values'] = [str(i) for i in range(17)]
        self.fast_sample_Variable.set('0')
        
        self.start_button_Variable = Tkinter.StringVar()
        self.start_button = ttk.Button(self,textvariable=self.start_button_Variable,command=self.OnButtonClick)
        self.start_button.grid(column=4,row=5)
        self.start_button_Variable.set('START')
        
        self.status_Variable = Tkinter.StringVar()
        status_bar = Tkinter.Label(self,textvariable=self.status_Variable,
                              anchor="w",fg="white",bg="blue")
        status_bar.grid(column=0,row=6,columnspan=5,sticky='EW')
        self.status_Variable.set(u"Hello !")
        
        logging.basicConfig(filename = 'window_errors.log', level=logging.ERROR)
        
        self.test = fast_test.fast_test(0, "GPIB1::9::INSTR",
                                        print_ch = 'Tk', Tk_output = self.output_box, Tk_status = self.status_Variable)
        self.is_running = False
        
    def OnButtonClick(self):
        self.start_button.state(['disabled'])
        if not self.is_running: # not running, then start
            self.start_button_Variable.set('STOP')
            self.sample_select_box.state(['disabled'])
            self.interval_select_box.state(['disabled'])
            self.is_running = True
            self.test._to_stop = False
            self.test.sample_no = int(self.fast_sample_Variable.get())
            self.test.interval = float(self.initial_interval_Variable.get())
            self.test.initialize()
            self.test_thread = threading.Thread(target = self.test.main_test_loop)
            self.test_thread.start()
        else: # already running, then stop
            self.test._to_stop = True
            self.test_thread.join()
            self.is_running = False
            self.fast_sample_Variable.set('0')
            self.start_button_Variable.set('START')
            self.interval_select_box.state(['!disabled'])
            self.sample_select_box.state(['!disabled'])
        self.start_button.state(['!disabled'])
        
class slow_frame(Tkinter.Frame):
    def __init__(self, parent, fast_sample_Variable):
        Tkinter.Frame.__init__(self, parent, bd=10)
        self.parent = parent
        self.fast_sample_Variable = fast_sample_Variable
        self.initialize()

    def initialize(self):
        # GUI part
        self.grid()
        
        captain_line = Tkinter.Label(self, text='Slow Measurement', font=("Helvetica", 16))
        captain_line.grid(column=0,row=0,columnspan=5)
        
        self.output_box = Tkinter.Text(self, undo = False, wrap='none', state='disabled',
                                 width = 60, height = 31)
        self.output_box.grid(column=0,row=1,columnspan=5,sticky='EW')
        
        initial_interval_Label = Tkinter.Label(self, text='Initial interval (sec):',anchor='e')
        initial_interval_Label.grid(column=0,row=4)
        self.initial_interval_Variable = Tkinter.StringVar()
        self.interval_select_box = ttk.Combobox(self, textvariable=self.initial_interval_Variable, state='readonly')
        self.interval_select_box.grid(column=1,row=4,sticky='EW')
        self.interval_select_box['values'] = ['15','30','60','150','300']
        self.initial_interval_Variable.set('30')
        
        wait_time_Label = Tkinter.Label(self, text='Stabilize time (sec):',anchor='e')
        wait_time_Label.grid(column=2,row=4)
        self.wait_time_Variable = Tkinter.StringVar()
        self.wait_time_select_box = ttk.Combobox(self, textvariable=self.wait_time_Variable, state='readonly')
        self.wait_time_select_box.grid(column=3,row=4,sticky='EW')
        self.wait_time_select_box['values'] = ['1','3','5','10','30']
        self.wait_time_Variable.set('3')
        
        self.sample_select_box = Tkinter.LabelFrame(self, text='Slow mode samples')
        self.sample_select_box.grid(column=0,row=5,columnspan=4,sticky='W')
        
        self.selected_Var = [Tkinter.IntVar() for i in range(17)]
        for i in range(1,5):
            self.selected_Var[i].set(1)
        select_buttons = [None]*17
        for i in range(1,17):
            select_buttons[i] = Tkinter.Checkbutton(self.sample_select_box, text=str(i), variable=self.selected_Var[i], command=self.OnSampleSelect)
            select_buttons[i].grid(column=(i-1)%8,row=(i-1)//8)
        
        self.start_button_Variable = Tkinter.StringVar()
        self.start_button = ttk.Button(self,textvariable=self.start_button_Variable,command=self.OnButtonClick)
        self.start_button.grid(column=4,row=5,sticky='EWNS')
        self.start_button_Variable.set('START')
        
        self.status_Variable = Tkinter.StringVar()
        status_bar = Tkinter.Label(self,textvariable=self.status_Variable,
                              anchor="w",fg="white",bg="blue")
        status_bar.grid(column=0,row=6,columnspan=5,sticky='EW')
        self.status_Variable.set(u"Hello !")
        
        logging.basicConfig(filename = 'window_errors.log', level=logging.ERROR)

        initial_sample_list = set([i for i in range(1,17) if int(self.selected_Var[i].get())==1])
        self.test = slow_test.slow_test(initial_sample_list, "GPIB1::11::INSTR", INTERVAL = 3, print_ch = 'Tk',
                                        Tk_output = self.output_box, Tk_status = self.status_Variable, Tk_fast_sample = self.fast_sample_Variable)
        self.is_running = False
        
    def OnButtonClick(self):
        self.start_button.state(['disabled'])
        if not self.is_running: # not running, then start
            self.start_button_Variable.set('STOP')
            self.interval_select_box.state(['disabled'])
            self.wait_time_select_box.state(['disabled'])
            self.test._to_stop = False
            self.test.interval = [float(self.initial_interval_Variable.get())] * 17
            #self.test.box.wait = float(self.wait_time_Variable.get())
            self.test.initialize()
            self.test_thread = threading.Thread(target = self.test.main_test_loop)
            self.test_thread.start()
            self.is_running = True
        else: # already running, then stop
            self.test._to_stop = True
            self.test_thread.join()
            self.is_running = False
            self.start_button_Variable.set('START')
            self.interval_select_box.state(['!disabled'])
            self.wait_time_select_box.state(['!disabled'])
        self.start_button.state(['!disabled'])
    
    def OnSampleSelect(self):
        for child in self.sample_select_box.winfo_children():
            child.configure(state='disable')
        new_sample_list = set([i for i in range(1,17) if int(self.selected_Var[i].get())==1])
        if self.is_running:
            add_queue = new_sample_list - self.test.sample_list
            remove_queue = self.test.sample_list - new_sample_list
            for sample in add_queue:
                self.test.add_one_to_measurement(sample)
            for sample in remove_queue:
                self.test.remove_one_from_measurement(sample)
        for child in self.sample_select_box.winfo_children():
            child.configure(state='normal')
            
class main_window(Tkinter.Tk):
    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.initialize()
        
    def initialize(self):
        self.fast_sample_Variable = Tkinter.StringVar()
        self.left_frame = fast_frame(self,self.fast_sample_Variable)
        self.left_frame.grid(row=0, column=0)
        self.right_frame = slow_frame(self,self.fast_sample_Variable)
        self.right_frame.grid(row=0, column=1)
        self.title('Multiplexer Measurements')
        self.resizable(False,False)

if __name__ == "__main__":
    root = main_window(None)
    root.mainloop()
