import Tkinter
import ttk
import tkMessageBox
import threading
import logging
import re
import time

import thread_safe_tk_widgets
import fast_test
import slow_test

FAST_LOCKIN = "GPIB0::9::INSTR"
SLOW_LOCKIN = "GPIB0::11::INSTR"

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
        
        freq_entry_Label = Tkinter.Label(self, text='Initial freq:',anchor='e')
        freq_entry_Label.grid(column=4,row=5)
        vcmd = (self.register(self.EntryValidate),'%P')
        self.freq_Entry = Tkinter.Entry(self, validate="key", validatecommand=vcmd, width=10,state = Tkinter.NORMAL)
        self.freq_Entry.grid(column=5,row=5)
        self.freq_Entry.delete(0,Tkinter.END)
        self.freq_Entry.insert(0,'43')
        
        self.auto_tc_Var = Tkinter.IntVar()
        self.auto_tc_Var.set(0)
        auto_tc_button = Tkinter.Checkbutton(self, text='Auto interval and frequency', variable=self.auto_tc_Var)
        auto_tc_button.grid(column=0,row=6,columnspan=2,sticky='W')
        
        self.last_point_Var = Tkinter.IntVar()
        self.last_point_Var.set(0)
        last_point_button = Tkinter.Checkbutton(self, text='Last Point', variable=self.last_point_Var)
        last_point_button.grid(column=2,row=6,sticky='W')
        
        self.start_button_Variable = Tkinter.StringVar()
        self.start_button = ttk.Button(self,textvariable=self.start_button_Variable,command=self.OnButtonClick)
        self.start_button.grid(column=9,row=5,rowspan=2,sticky='EWNS')
        self.start_button_Variable.set('START')
        
        self.status_bar = thread_safe_tk_widgets.ThreadSafeLabel(self,text="Hello!",anchor="w",fg="white",bg="blue")
        self.status_bar.grid(column=0,row=7,columnspan=10,sticky='EW')
        
        # logic part
        self.test = fast_test.fast_test(0, FAST_LOCKIN, print_ch = 'Tk', init_freq = float(self.freq_Entry.get()),
                                        Tk_output = self.output_box, Tk_status = self.status_bar)
        self.auto_tc_Var.trace('w',self.OnAutoTcChange)
        self.last_point_Var.trace('w',self.OnLastPointChange)
        self.is_running = False
        
    def OnButtonClick(self):
        self.start_button.state(['disabled'])
        if not self.is_running: # not running, then start
            self.start_button_Variable.set('STOP') #1
            self.sample_select_box.state(['disabled']) #2
            self.interval_select_box.state(['disabled']) #3
            self.freq_Entry.configure(state='disabled') #7
            self.is_running = True #4
            self.test._to_stop = False #5
            self.test.sample_no = int(self.sample_select_Variable.get())
            self.parent_fast_sample_Variable.set(self.sample_select_Variable.get()) #6
            self.test.interval = float(self.initial_interval_Variable.get())
            self.test.freq = float(self.freq_Entry.get())
            #self.test.initialize()
            self.test_thread = threading.Thread(target = self.test.main_test_loop)
            self.test_thread.start()
        else: # already running, then stop
            self.test._to_stop = True #5
            self.test_thread.join()
            self.freq_Entry.configure(state='normal') #7
            self.parent_fast_sample_Variable.set('0') #6
            self.is_running = False #4
            self.interval_select_box.state(['!disabled']) #3
            self.sample_select_box.state(['!disabled']) #2
            self.start_button_Variable.set('START') #1
        self.start_button.state(['!disabled'])
        
    def OnAutoTcChange(self,*args):
        self.test._auto_tc = bool(self.auto_tc_Var.get())
        
    def OnLastPointChange(self,*args):
        self.test._last_point = bool(self.last_point_Var.get())
        
    def EntryValidate(self, P):
        # Disallow anything but float number
        valid = bool(re.match(r'^\d\.?\d*$',P))
        if not valid:
            self.bell()
        return valid
        
class slow_frame(Tkinter.Frame):
    def __init__(self, parent, slow_freq_Variable):
        Tkinter.Frame.__init__(self, parent, bd=10)
        self.parent = parent
        self.slow_freq_Variable = slow_freq_Variable
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
        
        freq_entry_Label = Tkinter.Label(self, text='Slow freq:',anchor='e')
        freq_entry_Label.grid(column=4,row=4)
        vcmd = (self.register(self.EntryValidate),'%P')
        self.freq_Entry = Tkinter.Entry(self, textvariable=self.slow_freq_Variable, validate="key", validatecommand=vcmd, width=10)
        self.freq_Entry.grid(column=5,row=4)
        self.freq_Entry.delete(0,Tkinter.END)
        self.freq_Entry.insert(0,'1.3')
        
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

        self.time_Label = Tkinter.Label(self, text = "Current time:\nNot running")
        self.time_Label.grid(column=4,row=5,columnspan=2,sticky='W')
        
        self.start_button_Variable = Tkinter.StringVar()
        self.start_button = ttk.Button(self,textvariable=self.start_button_Variable,command=self.OnButtonClick)
        self.start_button.grid(column=9,row=4,rowspan=2,sticky='EWNS')
        self.start_button_Variable.set('START')
        
        self.status_bar = thread_safe_tk_widgets.ThreadSafeLabel(self,text="Hello!",anchor="w",fg="white",bg="blue")
        self.status_bar.grid(column=0,row=6,columnspan=10,sticky='EW')
        
        # logic part
        initial_sample_list = set([i for i in range(1,17) if int(self.selected_Var[i].get())==1])
        self.test = slow_test.slow_test(initial_sample_list, SLOW_LOCKIN, FREQ = float(self.slow_freq_Variable.get()), print_ch = 'Tk',
                                        INTERVAL = float(self.initial_interval_Variable.get()), WAIT_TIME = float(self.wait_time_Variable.get()),
                                        Tk_output = self.output_box, Tk_status = self.status_bar)
        self.wait_time_Variable.trace('w',self.OnWaitTimeChange)
        self.initial_interval_Variable.trace('w',self.OnInitialInvervalChange)
        self.auto_tc_Var.trace('w',self.OnAutoTcChange)
        self.is_running = False
        self.UpdateTimeLabel()
        
    def OnButtonClick(self):
        self.start_button.state(['disabled'])
        if not self.is_running: # not running, then start
            self.start_button_Variable.set('STOP') #1
            self.test.interval = [float(self.initial_interval_Variable.get())] * 17
            self.test.box.wait = float(self.wait_time_Variable.get())
            self.test.sample_list = set([i for i in range(1,17) if int(self.selected_Var[i].get())==1])
            self.test._to_stop = False #4
            self.is_running = True #5
            self.freq_Entry.configure(state='disabled') #6
            self.test.freq = float(self.slow_freq_Variable.get())
            #self.test.initialize()
            self.test_thread = threading.Thread(target = self.test.main_test_loop)
            self.test_thread.start()
        else: # already running, then stop
            self.test._to_stop = True #4
            self.test_thread.join()
            self.is_running = False #5
            self.freq_Entry.configure(state='normal') #6
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
                #self.output_box.write('add sample %i' % sample)
            for sample in remove_queue:
                self.test.remove_one_from_measurement(sample)
                #self.output_box.write('remove sample %i' % sample)
        for child in self.sample_select_box.winfo_children():
            child.configure(state='normal')
            
    def OnWaitTimeChange(self,*args):
        self.test.wait_time = float(self.wait_time_Variable.get())
        
    def OnInitialInvervalChange(self,*args):
        self.test.default_interval = float(self.initial_interval_Variable.get())
    
    def OnAutoTcChange(self,*args):
        self.test._auto_tc = bool(self.auto_tc_Var.get())
        
    def EntryValidate(self, P):
        # Disallow anything but float number
        valid = bool(re.match(r'^\d\.?\d*$',P))
        if not valid:
            self.bell()
        return valid

    def UpdateTimeLabel(self):
        if self.test.t0 == None:
            self.time_Label.configure(text='Current time:\nNot Running')
        else:
            self.time_Label.configure(text='Current time:\n%fs'%(time.clock()-self.test.t0))
        self.parent.after(1000,self.UpdateTimeLabel)
            
class main_window(Tkinter.Tk):
    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.initialize()
        
    def initialize(self):
        self.fast_sample_Variable = Tkinter.StringVar()
        self.slow_freq_Variable = Tkinter.StringVar()
        self.left_frame = fast_frame(self,self.fast_sample_Variable)
        self.left_frame.grid(row=0, column=0)
        self.right_frame = slow_frame(self,self.slow_freq_Variable)
        self.right_frame.grid(row=0, column=1)
        self.title('Multiplexer Measurements')
        self.resizable(False,False)
        self.lift()
        self.focus_force()
        
        self.protocol("WM_DELETE_WINDOW", self.OnClosingWindow)
        self.fast_sample_Variable.trace('w',self.OnFastSampleChange)
        self.slow_freq_Variable.trace('w',self.OnSlowFreqChange)
        
    def OnFastSampleChange(self,*args):
        self.right_frame.test.idx_to_ignore = int(self.fast_sample_Variable.get())
        
    def OnSlowFreqChange(self,*args):
        self.left_frame.test.SLOW_FREQ = float(self.slow_freq_Variable.get())
        
    def OnClosingWindow(self):
        if self.left_frame.is_running or self.right_frame.is_running:
            tkMessageBox.showerror("Error","Measurement still running")
        else:
            if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
                root.destroy()

if __name__ == "__main__":
    logging.basicConfig(filename = 'window_errors.log', level=logging.WARNING)
    root = main_window(None)
    root.mainloop()
