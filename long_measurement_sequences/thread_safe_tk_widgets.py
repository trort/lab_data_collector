import Tkinter
import Queue

class ThreadSafeLabel(Tkinter.Label):
    def __init__(self, master, **options):
        #self.Variable = Tkinter.StringVar()
        #self.Variable.set(u"Hello !")
        Tkinter.Label.__init__(self, master, **options)
        self.next_value = None
        self.update_me()
    def write(self, line):
        self.next_value = str(line)
    def update_me(self):
        if self.next_value != None:
            self.config(text = self.next_value)
            self.next_value = None
            self.update_idletasks()
        self.after(100, self.update_me)
        
class ThreadSafeText(Tkinter.Text):
    def __init__(self, master, **options):
        Tkinter.Text.__init__(self, master, **options)
        self.queue = Queue.Queue()
        self.update_me()
    def write(self, line):
        self.queue.put(line)
    def update_me(self):
        try:
            while 1:
                line = self.queue.get_nowait()
                #self['state'] = 'normal'
                self.insert('end', line + '\n')
                self.delete('1.0', 'end -30 lines')
                #self['state'] = 'disabled'
                self.update_idletasks()
        except Queue.Empty:
            pass
        self.after(100, self.update_me)