import Tkinter
import ttk
import threading
import logging

import fast_test
import slow_test

class fast_frame(Tkinter.Frame):
    def __init__(self, parent):
        Tkinter.Frame.__init__(self, parent, width=500, height=800, bd=10)
        self.parent = parent
        self.initialize()

    def initialize(self):
        # GUI part
        self.grid()
        
        captain_line = Tkinter.Label(self, text='Fast Measurement', font=("Helvetica", 16), anchor="w")
        captain_line.grid(column=0,row=0,columnspan=3)
        
        self.output_box = Tkinter.Text(self, undo = False, wrap='none', state='disabled',
                                 width = 80, height = 22)
        self.output_box.grid(column=0,row=1,columnspan=3,rowspan=4,sticky='EW')
        
        sample_select_Label = Tkinter.Label(self, text='Select fast mode sample:',anchor='e')
        sample_select_Label.grid(column=0,row=5)
        
        self.sample_select_Variable = Tkinter.StringVar()
        self.sample_select_box = ttk.Combobox(self, textvariable=self.sample_select_Variable, state='readonly')
        self.sample_select_box.grid(column=1,row=5,sticky='EW')
        #self.sample_select_box.bind('<<ComboboxSelected>>', self.OnSelectCombobox)
        self.sample_select_box['values'] = [str(i) for i in range(17)]
        self.sample_select_Variable.set('0')
        
        self.start_button_Variable = Tkinter.StringVar()
        self.start_button = ttk.Button(self,textvariable=self.start_button_Variable,command=self.OnButtonClick)
        self.start_button.grid(column=2,row=5)
        self.start_button_Variable.set('START')
        
        self.status_Variable = Tkinter.StringVar()
        status_bar = Tkinter.Label(self,textvariable=self.status_Variable,
                              anchor="w",fg="white",bg="blue")
        status_bar.grid(column=0,row=6,columnspan=3,sticky='EW')
        self.status_Variable.set(u"Hello !")
        
        #self.grid_columnconfigure(0,weight=1)
        #self.grid_rowconfigure(0,weight=1)
        #self.resizable(False,False)
        #self.update()
        #self.geometry(self.geometry())
        
        logging.basicConfig(filename = 'window_errors.log', level=logging.ERROR)
        
        self.test = fast_test.fast_test(0, "GPIB1::9::INSTR", INTERVAL = 0.2,
                                             print_ch = 'Tk', Tk_output = self.output_box, Tk_status = self.status_Variable)
        self.is_running = False
        
    def OnButtonClick(self):
        self.start_button.state(['disabled'])
        if not self.is_running: # not running, then start
            self.start_button_Variable.set('STOP')
            self.sample_select_box.state(['disabled'])
            self.test._to_stop = False
            self.test.sample_no = int(self.sample_select_Variable.get())
            self.test.initialize()
            self.test_thread = threading.Thread(target = self.test.main_test_loop)
            self.test_thread.start()
            self.is_running = True
        else: # already running, then stop
            self.test._to_stop = True
            self.test_thread.join()
            self.is_running = False
            self.start_button_Variable.set('START')
            self.sample_select_box.state(['!disabled'])
        self.start_button.state(['!disabled'])
        
class slow_frame(Tkinter.Frame):
    def __init__(self, parent):
        Tkinter.Frame.__init__(self, parent, width=500, height=800, bd=10)
        self.parent = parent
        self.initialize()

    def initialize(self):
        # GUI part
        self.grid()
        
        captain_line = Tkinter.Label(self, text='Slow Measurement', font=("Helvetica", 16))
        captain_line.grid(column=0,row=0,columnspan=3)
        
        self.output_box = Tkinter.Text(self, undo = False, wrap='none', state='disabled',
                                 width = 80, height = 22)
        self.output_box.grid(column=0,row=1,columnspan=3,rowspan=4,sticky='EW')
        
        self.sample_select_box = Tkinter.LabelFrame(self, text='Slow mode samples')
        self.sample_select_box.grid(column=0,row=5,columnspan=2)
        
        self.selected_Var = [Tkinter.IntVar() for i in range(17)]
        select_buttons = [None]*17
        for i in range(1,17):
            select_buttons[i] = Tkinter.Checkbutton(self.sample_select_box, text=str(i), variable=self.selected_Var[i], command=self.OnSampleSelect)
            select_buttons[i].grid(column=i-1,row=0)
        
        self.start_button_Variable = Tkinter.StringVar()
        self.start_button = ttk.Button(self,textvariable=self.start_button_Variable,command=self.OnButtonClick)
        self.start_button.grid(column=2,row=5)
        self.start_button_Variable.set('START')
        
        self.status_Variable = Tkinter.StringVar()
        status_bar = Tkinter.Label(self,textvariable=self.status_Variable,
                              anchor="w",fg="white",bg="blue")
        status_bar.grid(column=0,row=6,columnspan=3,sticky='EW')
        self.status_Variable.set(u"Hello !")
        
        logging.basicConfig(filename = 'window_errors.log', level=logging.ERROR)
        
        self.test = slow_test.slow_test([2,3,4], "GPIB1::11::INSTR", INTERVAL = 5,
                                             print_ch = 'Tk', Tk_output = self.output_box, Tk_status = self.status_Variable)
        self.is_running = False
        
    def OnButtonClick(self):
        self.start_button.state(['disabled'])
        if not self.is_running: # not running, then start
            self.start_button_Variable.set('STOP')
            self.test._to_stop = False
            self.test.initialize()
            self.test_thread = threading.Thread(target = self.test.main_test_loop)
            self.test_thread.start()
            self.is_running = True
        else: # already running, then stop
            self.test._to_stop = True
            self.test_thread.join()
            self.is_running = False
            self.start_button_Variable.set('START')
        self.start_button.state(['!disabled'])
    
    def OnSampleSelect(self):
        pass

if __name__ == "__main__":
    root = Tkinter.Tk()
    left_frame = fast_frame(root)
    left_frame.grid(row=0, column=0)
    right_frame = slow_frame(root)
    right_frame.grid(row=0, column=1)
    root.title('Multiplexer Measurements')
    root.resizable(False,False)
    root.mainloop()