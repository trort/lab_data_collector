import Tkinter
import time
import threading

def MyThread(window):
    n = 0
    while True:
        window.text.insert(Tkinter.END, window.entryVariable.get()+str(n)+" (You clicked the button)\n")
        n += 1
        time.sleep(0.1)
        window.text.delete("1.0","end -20 lines")
        if n >= 30:
            pass#break

class fast_window(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.grid()
        
        self.text = Tkinter.Text(self,undo = False,wrap=Tkinter.NONE)
        self.text.grid(column=0,row=0,columnspan=2,rowspan=5,sticky='EW')
        
        self.entryVariable = Tkinter.StringVar()
        self.entry = Tkinter.Entry(self,textvariable=self.entryVariable)
        self.entry.grid(column=0,row=5,sticky='EW')
        self.entry.bind("<Return>", self.OnPressEnter)
        self.entryVariable.set(u"Enter text here.")
        
        button = Tkinter.Button(self,text=u"Infinite add",command=self.OnButtonClick)
        button.grid(column=1,row=5)
        
        self.labelVariable = Tkinter.StringVar()
        label = Tkinter.Label(self,textvariable=self.labelVariable,
                              anchor="w",fg="white",bg="blue")
        label.grid(column=0,row=6,columnspan=2,sticky='EW')
        self.labelVariable.set(u"Hello !")
        
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.resizable(True,False)
        self.update()
        self.geometry(self.geometry())
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)
        
    def OnButtonClick(self):
        self.labelVariable.set(self.entryVariable.get()+" (You clicked the button)")
        textThread = threading.Thread(target = MyThread, args = (self,))
        textThread.start()
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)

    def OnPressEnter(self,event):
        self.labelVariable.set(self.entryVariable.get()+" (You pressed ENTER)")
        self.text.insert(Tkinter.END, self.entryVariable.get()+" (You pressed ENTER)\n")
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)

if __name__ == "__main__":
    app = fast_window(None)
    app.title('Fast Measurement')
    app.mainloop()