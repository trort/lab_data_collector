import Tkinter
import ttk
import threading
import logging

import thread_safe_tk_widgets
import fast_test
import slow_test

class fast_frame(Tkinter.Frame):
    def __init__(self, parent, fast_sample_Variable):
        Tkinter.Frame.__init__(self, parent, bd=10)
        self.parent = parent
        self.parent_fast_sample_Variable = fast_sample_Variable
        self.initialize()

    def initialize(self):
        # GUI part
        self.grid()
        
        captain_line = Tkinter.Label(self, text='Fast Measurement', font=("Helvetica", 16), anchor="w")
        captain_line.grid(column=0,row=0,columnspan=10)
        
        self.output_box = thread_safe_tk_widgets.ThreadSafeText(self, undo = False, wrap='none',
                          width = 60, height = 34)
        self.output_box.grid(column=0,row=1,columnspan=10,sticky='EW')
        
        initial_interval_Label = Tkinter.Label(self, text='Initial interval (sec):',anchor='e')
        initial_interval_Label.grid(column=0,row=5)
        self.initial_interval_Variable = Tkinter.StringVar()
        self.interval_select_box = ttk.Combobox(self, textvariable=self.initial_interval_Variable, state='readonly', width=10)
        self.interval_select_box.grid(column=1,row=5,sticky='EW')
        self.interval_select_box['values'] = ['0.01','0.05','0.1','0.3','1','3']
        self.initial_interval_Variable.set('0.01')
        
        sample_select_Label = Tkinter.Label(self, text='Fast mode sample:',anchor='e')
        sample_select_Label.grid(column=2,row=5)
        self.sample_select_Variable = Tkinter.StringVar()
        self.sample_select_box = ttk.Combobox(self, textvariable=self.sample_select_Variable, state='readonly', width=6)
        self.sample_select_box.grid(column=3,row=5,sticky='EW')
        self.sample_select_box['values'] = [str(i) for i in range(17)]
        self.sample_select_Variable.set('0')
        
        self.auto_tc_Var = Tkinter.IntVar()
        self.auto_tc_Var.set(1)
        auto_tc_button = Tkinter.Checkbutton(self, text='Auto interval and frequency', variable=self.auto_tc_Var)
        auto_tc_button.grid(column=0,row=6,columnspan=2,sticky='W')
        
        self.start_button_Variable = Tkinter.StringVar()
        self.start_button = ttk.Button(self,textvariable=self.start_button_Variable,command=self.OnButtonClick)
        self.start_button.grid(column=9,row=5,rowspan=2,sticky='EWNS')
        self.start_button_Variable.set('START')
        
        self.status_bar = thread_safe_tk_widgets.ThreadSafeLabel(self,text="Hello!",anchor="w",fg="white",bg="blue")
        self.status_bar.grid(column=0,row=7,columnspan=10,sticky='EW')
        
        # logic part
        self.test = fast_test.fast_test(0, "GPIB1::9::INSTR", print_ch = 'Tk',
                                        Tk_output = self.output_box, Tk_status = self.status_bar)
        self.auto_tc_Var.trace('w',self.OnAutoTcChange)
        self.is_running = False
        
    def OnButtonClick(self):
        self.start_button.state(['disabled'])
        if not self.is_running: # not running, then start
            self.start_button_Variable.set('STOP') #1
            self.sample_select_box.state(['disabled']) #2
            self.interval_select_box.state(['disabled']) #3
            self.is_running = True #4
            self.test._to_stop = False #5
            self.test.sample_no = int(self.sample_select_Variable.get())
            self.parent_fast_sample_Variable.set(self.sample_select_Variable.get()) #6
            self.test.interval = float(self.initial_interval_Variable.get())
            self.test.initialize()
            self.test_thread = threading.Thread(target = self.test.main_test_loop)
            self.test_thread.start()
        else: # already running, then stop
            self.test._to_stop = True #5
            self.test_thread.join()
            self.parent_fast_sample_Variable.set('0') #6
            self.is_running = False #4
            self.interval_select_box.state(['!disabled']) #3
            self.sample_select_box.state(['!disabled']) #2
            self.start_button_Variable.set('START') #1
        self.start_button.state(['!disabled'])
        
    def OnAutoTcChange(self,*args):
        self.test._auto_tc = bool(self.auto_tc_Var.get())
        
class slow_frame(Tkinter.Frame):
    def __init__(self, parent):
        Tkinter.Frame.__init__(self, parent, bd=10)
        self.parent = parent
        self.initialize()

    def initialize(self):
        # GUI part
        self.grid()
        
        captain_line = Tkinter.Label(self, text='Slow Measurement', font=("Helvetica", 16))
        captain_line.grid(column=0,row=0,columnspan=10)
        
        self.output_box = thread_safe_tk_widgets.ThreadSafeText(self, undo = False, wrap='none',
                          width = 60, height = 31)
        self.output_box.grid(column=0,row=1,columnspan=10,sticky='EW')
        
        initial_interval_Label = Tkinter.Label(self, text='Initial interval (sec):',anchor='e')
        initial_interval_Label.grid(column=0,row=4)
        self.initial_interval_Variable = Tkinter.StringVar()
        self.interval_select_box = ttk.Combobox(self, textvariable=self.initial_interval_Variable, state='readonly', width=10)
        self.interval_select_box.grid(column=1,row=4,sticky='EW')
        self.interval_select_box['values'] = ['15','30','60','150','300','600']
        self.initial_interval_Variable.set('30')
        
        wait_time_Label = Tkinter.Label(self, text='Stabilize time (sec):',anchor='e')
        wait_time_Label.grid(column=2,row=4)
        self.wait_time_Variable = Tkinter.StringVar()
        self.wait_time_select_box = ttk.Combobox(self, textvariable=self.wait_time_Variable, state='readonly', width=6)
        self.wait_time_select_box.grid(column=3,row=4,sticky='EW')
        self.wait_time_select_box['values'] = ['1','3','5','10','30']
        self.wait_time_Variable.set('3')
        
        self.sample_select_box = Tkinter.LabelFrame(self, text='Slow mode samples')
        self.sample_select_box.grid(column=0,row=5,columnspan=3,sticky='W')
        
        self.selected_Var = [Tkinter.IntVar() for i in range(17)]
        for i in range(1,5):
            self.selected_Var[i].set(1)
        select_buttons = [None]*17
        for i in range(1,17):
            select_buttons[i] = Tkinter.Checkbutton(self.sample_select_box, text=str(i), variable=self.selected_Var[i], command=self.OnSampleSelect)
            select_buttons[i].grid(column=(i-1)%8,row=(i-1)//8)

        self.auto_tc_Var = Tkinter.IntVar()
        self.auto_tc_Var.set(1)
        auto_tc_button = Tkinter.Checkbutton(self, text='Auto interval', variable=self.auto_tc_Var)
        auto_tc_button.grid(column=3,row=5,sticky='W')
        
        self.start_button_Variable = Tkinter.StringVar()
        self.start_button = ttk.Button(self,textvariable=self.start_button_Variable,command=self.OnButtonClick)
        self.start_button.grid(column=9,row=4,rowspan=2,sticky='EWNS')
        self.start_button_Variable.set('START')
        
        self.status_bar = thread_safe_tk_widgets.ThreadSafeLabel(self,text="Hello!",anchor="w",fg="white",bg="blue")
        self.status_bar.grid(column=0,row=6,columnspan=10,sticky='EW')
        
        # logic part
        initial_sample_list = set([i for i in range(1,17) if int(self.selected_Var[i].get())==1])
        self.test = slow_test.slow_test(initial_sample_list, "GPIB1::11::INSTR", print_ch = 'Tk',
                                        Tk_output = self.output_box, Tk_status = self.status_bar)
        self.wait_time_Variable.trace('w',self.OnWaitTimeChange)
        self.initial_interval_Variable.trace('w',self.OnInitialInvervalChange)
        self.auto_tc_Var.trace('w',self.OnAutoTcChange)
        self.is_running = False
        
    def OnButtonClick(self):
        self.start_button.state(['disabled'])
        if not self.is_running: # not running, then start
            self.start_button_Variable.set('STOP') #1
            self.test.interval = [float(self.initial_interval_Variable.get())] * 17
            #self.test.box.wait = float(self.wait_time_Variable.get())
            self.test._to_stop = False #4
            self.is_running = True #5
            self.test.initialize()
            self.test_thread = threading.Thread(target = self.test.main_test_loop)
            self.test_thread.start()
        else: # already running, then stop
            self.test._to_stop = True #4
            self.test_thread.join()
            self.is_running = False #5
            self.start_button_Variable.set('START') #1
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
            
    def OnWaitTimeChange(self,*args):
        self.test.wait_time = float(self.wait_time_Variable.get())
        
    def OnInitialInvervalChange(self,*args):
        self.test.default_interval = float(self.initial_interval_Variable.get())
    
    def OnAutoTcChange(self,*args):
        self.test._auto_tc = bool(self.auto_tc_Var.get())
            
class main_window(Tkinter.Tk):
    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.initialize()
        
    def initialize(self):
        self.fast_sample_Variable = Tkinter.StringVar()
        self.left_frame = fast_frame(self,self.fast_sample_Variable)
        self.left_frame.grid(row=0, column=0)
        self.right_frame = slow_frame(self)
        self.right_frame.grid(row=0, column=1)
        self.title('Multiplexer Measurements')
        self.resizable(False,False)
        
        self.fast_sample_Variable.trace('w',self.OnFastSampleChange)
        
    def OnFastSampleChange(self,*args):
        self.right_frame.test.idx_to_ignore = int(self.fast_sample_Variable.get())

if __name__ == "__main__":
    logging.basicConfig(filename = 'window_errors.log', level=logging.WARNING)
    root = main_window(None)
    root.mainloop()
