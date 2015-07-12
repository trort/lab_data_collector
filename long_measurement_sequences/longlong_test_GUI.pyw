import Tkinter
import ttk
import time
import threading
import logging

import fast_test

class fast_window(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        # GUI part
        self.grid()
        
        self.text = Tkinter.Text(self, undo = False, wrap='none', state='disabled',
                                 width = 80, height = 22)
        self.text.grid(column=0,row=0,columnspan=3,rowspan=5,sticky='EW')
        
        comboboxLabel = Tkinter.Label(self, text='Select fast mode sample:',anchor='e')
        comboboxLabel.grid(column=0,row=5)
        
        self.comboboxVariable = Tkinter.StringVar()
        self.combobox = ttk.Combobox(self, textvariable=self.comboboxVariable, state='readonly')
        self.combobox.grid(column=1,row=5,sticky='EW')
        self.combobox.bind('<<ComboboxSelected>>', self.OnSelectCombobox)
        self.combobox['values'] = ('0', '1', '2', '3', '4')
        self.comboboxVariable.set('0')
        
        self.buttonVariable = Tkinter.StringVar()
        self.button = ttk.Button(self,textvariable=self.buttonVariable,command=self.OnButtonClick)
        self.button.grid(column=2,row=5)
        self.buttonVariable.set('START')
        
        self.labelVariable = Tkinter.StringVar()
        label = Tkinter.Label(self,textvariable=self.labelVariable,
                              anchor="w",fg="white",bg="blue")
        label.grid(column=0,row=6,columnspan=3,sticky='EW')
        self.labelVariable.set(u"Hello !")
        
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.resizable(False,False)
        self.update()
        self.geometry(self.geometry())
        
        logging.basicConfig(filename = 'window_errors.log', level=logging.ERROR)
        
        self.fast_test = fast_test.fast_test(0, "GPIB1::9::INSTR", INTERVAL = 1,
                                             print_ch = 'Tk', Tk_window  = self)
        self.fast_running = False
        
    def OnButtonClick(self):
        self.button.state(['disabled'])
        if not self.fast_running: # not running, then start
            self.fast_test._to_stop = False
            self.fast_test.sample_no = int(self.comboboxVariable.get())
            self.fast_test.initialize()
            self.test_thread = threading.Thread(target = self.fast_test.main_test_loop)
            self.test_thread.start()
            self.fast_running = True
            self.buttonVariable.set('STOP')
            self.combobox.state(['disabled'])
        else: # already running, then stop
            self.fast_test._to_stop = True
            self.test_thread.join()
            self.fast_running = False
            self.buttonVariable.set('START')
            self.combobox.state(['!disabled'])
        self.button.state(['!disabled'])
        
    def OnSelectCombobox(self,event):
        pass

if __name__ == "__main__":
    app = fast_window(None)
    app.title('Fast Measurement')
    app.mainloop()