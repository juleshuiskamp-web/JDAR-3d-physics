import tkinter as tk

Root = tk.Tk()
width= Root.winfo_screenwidth() 
height= Root.winfo_screenheight()
Root.geometry("%dx%d" % (width, height))

class Elemn():
    def __init__(self,typeR = "Label" ,ouder=Root, action=None, picture=None, duration=0, available= True, properties={}):
        self.parent = ouder
        self.action = action
        self.type = typeR
        self.picture = picture
        self.active = False
        self.available = True
        self.properties = properties
        self.actionDuration = duration
        self.object = None
        self.children = []
    
    def __eq__(self, other):
        if isinstance(other, Elemn):
            if other.parent == self.parent:
                return True
            else:
                return False
        else:
            return "unavailable"

    def initialize(self):

        self.object = getattr(tk, self.type)(master=self.parent)
        self.object.pack(expand=True,fill=self.properties['fill'],side=self.properties['side'])
    
    def activate(self):
        self.active = True
        self.available = False
        done = self.action()
        if done:
            self.active = False
            self.available = True


weergave = Elemn('Frame', properties = {'expand':True,'fill':'both','side':'left'})
weergave.initialize()

Root.mainloop()