import tkinter as tk,time, random
firstclassObjects = []
state = [False]
firstclassObjects = []
screenpoints = []
center = [0,0]
new = [0,0]
old = [0,0]
zoom = [1]
points = [[0,0],[0,100],[200,100],[200,0]]
screenpoints = [((x - center[0]) * zoom[0],(y - center[1]) * zoom[0])for x, y in points]
flat = [coord for point in screenpoints for coord in point]


dragging = [False]

def scrolling(event):
    global zoom, center, flat
    if event.delta > 0:
        zoom = [zoom[0] / 1.1]
    elif event.delta < 0: 
        zoom = [zoom[0] / 0.9]
    print(event.delta)
    screenpoints = [((x - center[0]) * zoom[0],(y - center[1]) * zoom[0])for x, y in points]
    flat = [coord for point in screenpoints for coord in point]
    canvas.delete("all")
    rectangle.visualize()

def rightPress(event):
    global old, new
    new = [event.x,event.y]
    dragging[0] = True

def rightRelease(event):
    dragging[0] = False

def draggin(event):
    global old, new, center , flat
    if dragging[0]:
        print(event.x,event.y)
        old = new.copy()
        new = [event.x,event.y]
        delta =[old[0]-new[0],old[1]-new[1]]
        center = [center[0]+delta[0],center[1]+delta[1]]
        print(center)
        screenpoints = [((x - center[0]) * zoom[0],(y - center[1]) * zoom[0])for x, y in points]
        flat = [coord for point in screenpoints for coord in point]
        canvas.delete("all")
        rectangle.visualize()
        print(screenpoints)

class mainRoot():
    def __init__(self):
        self.zoom = 0
        self.center = [0,0]
        self.children = []

    def addObject(self,other):
        if isinstance(other,Elemn):
            self.children.append(other)

class objectc():
    def __init__(self,points,colour = 'purple',master = 'canvas'):
        self.points = points
        self.color = colour
        firstclassObjects.append(self)
        self.parent = master
    
    def visualize(self):
        self.parent.create_polygon(
            flat,
            fill=self.color,
            outline="black"
        )


class Elemn():
    def __init__(self,typeR = "Label" ,ouder='Root', action=None, picture=None, duration=0, available= True, properties={}):
        self.parent = ouder
        self.action = action
        self.type = typeR
        self.picture = picture
        self.active = False
        self.available = True
        self.properties = properties
        self.actionDuration = duration
        self.object = None
        self.childeren = []
    
    def __equal__(self, other):
        if other.isinstance(Elemn):
            if other.parent == self.parent:
                return True
            else:
                return False
        else:
            return "unavailable"

    def initialize(self):
        self.object = tk.type(master=self.parent,**properties)
        (self.parent).childeren.add(self)
    
    def activate(self):
        self.active = True
        self.available = False
        done = self.action()
        if done:
            self.active = False
            self.available = True


def openEdit(target=0.3):
    state[0] = not state[0]

    RootSize = Root.winfo_screenwidth()
    target_width = int(RootSize * target)
    duration = 1000
    steps = 100
    stepSize = target_width / steps

    if state[0]:
        configure_screen.pack(side='right', fill='y')
        configure_screen.pack_propagate(False)
    else:
        # for item in childElements:
        #   item.pack_forget()
        pass  # we'll pack_forget at the end of animation

    def animate(current_step=0):
        if current_step > steps:
            if not state[0]:
                configure_screen.pack_forget()
            return
            # for item in childElements:
            #   item.pack(*item.arguments)
        if state[0]:
            new_width = int(current_step * stepSize)
        else:
            new_width = int(target_width - current_step * stepSize)
        configure_screen.config(width=new_width)
        Root.after(int(duration/steps), lambda: animate(current_step + 1))

    animate()

Root = tk.Tk()
width= Root.winfo_screenwidth() 
height= Root.winfo_screenheight()
Root.geometry("%dx%d" % (width, height))
# canvas = tk.Canvas(master=Root,height='300',width="400", bg='red')
toolbar = tk.Frame(master=Root, height="20")
toolbar.pack(side="top", fill="x")

Root.bind("<MouseWheel>", scrolling)
Root.bind("<Motion>", draggin)
Root.bind("<ButtonPress-3>", rightPress)
Root.bind("<ButtonRelease-3>", rightRelease)

# weergave = Elemn('Frame', properties = {'expand':True,'fill':'both','side':'left'})
# weergave.activate()
weergave = tk.Frame(Root)
weergave.pack(fill="both",expand=True,side="left")

configure_screen = tk.Frame(master=Root, bg='red', width=0)
configure_screen.pack(side="right", fill="y")
configure_screen.pack_propagate(False) 
introtext = tk.Label(master=configure_screen,text="hello,\nthis is the so convenietly placed user input \nfor adding objects\n for now it's just objects with four sides", justify='center', padx=5, bg='red')
introtext.pack(side='top')

canvas = tk.Canvas(master= weergave, bg="lightgray" )
canvas.pack(fill="both", expand=True, side='left')
rectangle = objectc(master = canvas,points = [[0,0],[0,100],[200,100],[200,0]])
rectangle.visualize()

for i in range(10):
    toolbar.grid_columnconfigure(i, weight=1)

# Click handler
def on_click(i):
    print(f"Clicked icon {i}")

# Add 10 "icons" (buttons for now)
button = []
for i in range(10):
    btn = tk.Button(master=toolbar, text=f"{i}", command=lambda i=i: on_click(i))
    btn.grid(row=0, column=i, sticky='ns',)
    btn.configure(width=btn.winfo_height()*2)
    button.append(btn)
button[-1].config(command= openEdit)






# Root.columnconfigure

# canvas.create_rectangle(0,0,100,100,fill="blue")
# canvas.pack()
# frame = tk.Frame(master=Root, bg="lightblue", width=200, height=100, bd=3, relief=tk.RIDGE)
# frame.pack(padx=20, pady=20)
# Root.attributes('-fullscreen', True)
Root.title("main")
Root.configure(bg="blue")
# Root.resizable(width=True,height=True)
# ab = tk.Label(master = Root, text = 'maby next time',fg = "gray")
# ab.pack()

Root.mainloop()

# class Root():
#     __init__(self,width,height):

# create top menu



# create drop down menu for optinions

# create input Root to create square opjects

# create functionallity for scrolling and resizing

