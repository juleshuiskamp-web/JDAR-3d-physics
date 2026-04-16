"""
JDAR 3D Physics Engine - 2D Viewport
"""

import tkinter as tk
import math as m

class MainWindow():
    """
    creates an instance of the gui window with a visualized virtual room
    """
    def __init__(self):
        self.zoom = 1
        self.worldCenter = Position2D(0,0,root=self)
        self.lastMousePos = Position2D(0,0,root=self)
        self.dragging = False

        self.window = tk.Tk()
        self.window.title("2d physics")

        self.screenSize = Position2D(self.window.winfo_screenwidth(),self.window.winfo_screenheight(),root=self)
        self.screenCenter = Position2D(self.screenSize.x/2,self.screenSize.y/2,root=self)
        self.window.geometry(f"{self.screenSize.x}x{self.screenSize.y}")
        
        self.options = tk.Frame(self.window, height=int(self.screenSize.x/8),bg="lightgray")
        self.options.pack(side="top", fill="x")
        self.canvas = tk.Canvas(self.window,bg="lightblue",bd="0",highlightthickness=0)
        self.canvas.pack(side="left", fill="both",expand=True)
        self.canvasCenter = Position2D(self.canvas.winfo_width(),self.canvas.winfo_height(),root=self)

        self.toggleEditor = tk.Frame(self.window, width=0,bg="purple")
        self.toggleEditor.pack_propagate(False)
        self.toggleEditor.pack(side="left",fill="y")

        self.buttons = []
        self.objects = []

        self.window.bind("<Motion>",self.draggin)
        self.window.bind("<ButtonPress-3>",self.rightClick)
        self.window.bind("<ButtonRelease-3>",self.rightRelease)
        self.window.bind("<MouseWheel>",self.zooming)
        self.LineSet = [[],[]]
        self.LineSet = self.createLineSet()

    def draw(self):
        """refreshes al to draw objects and visual refrenses"""
        self.canvas.delete("all")
        self.LineSet = self.createLineSet()
        for thing in self.objects:
            thing.place()

        for i in range(10):
            for j in range(10):
                point = Position2D(i*100,j*100,root=self)
                x = (i*100-self.worldCenter.x)/self.zoom+self.screenSize.x/2
                y = (j*100-self.worldCenter.y)/self.zoom+self.screenSize.y/2
                size = 5 / self.zoom
                self.canvas.create_oval(x-size, y-size, x+size, y+size, fill="white")

    def draggin(self,event):
        """updates screencenter based on mouse movement"""
        if not self.dragging:
            return
        event = Position2D(event.x,event.y,root=self)
        delta = event - self.lastMousePos
        self.worldCenter.update(*((self.worldCenter-delta).pack()))
        self.lastMousePos = Position2D(event.x, event.y,root=self)
        self.draw()
    
    def rightClick(self,event):
        """code for the event of mouse right click on the mainwindow canvas"""
        self.dragging = True
        self.lastMousePos = Position2D(event.x, event.y,root=self)
    
    def rightRelease(self,event):
        """code for the event of mouseClick release"""
        self.dragging = False
    
    def zooming(self,event):
        """code for resizing the virtual world on the screen based on scroll wheel movement"""
        factor = 1.1 if event.delta > 0 else 0.9
        self.zoom *= factor
        self.draw()

    def start(self):
        """starts the visual aspect of the class"""
        self.window.mainloop()

    def renderButtons(self):
        """initializes all show buttons"""
        self.buttons = [tk.Button(self.options,text="refresh points",command=self.edito,width=5)for _ in range(8)]
        for i,button in enumerate(self.buttons):
            button.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            self.options.grid_columnconfigure(i, weight=1)

    def edito(self):
        """opens the edit menu for creating new objects"""
        if not self.toggleEditor.winfo_ismapped():
            self.toggleEditor.pack(side="right", fill="y")
            current = 0
            crop = False
        else: 
           current = self.toggleEditor.winfo_width()
           crop = current >= int(self.window.winfo_screenwidth() / 6)
        
        step = [0]
        stepsSize = max(1, self.window.winfo_screenwidth() // 180)
        maxWidhetSize = int(self.window.winfo_screenwidth() / 3)
        target = 0 if crop else maxWidhetSize
        total_steps = max(1, abs(target - current) // stepsSize)

        def expand():
            if step[0] < total_steps:
                step[0] += 1
                direction = -1 if crop else 1
                new_width = current + (step[0] * stepsSize * direction)
                new_width = max(0, min(maxWidhetSize, new_width))
                self.toggleEditor.config(width=new_width)
                self.window.after(4, expand)
            else:
                self.toggleEditor.config(width=target)
                if crop:
                    self.toggleEditor.pack_forget()
        
        expand()
    
    def addObject(self,Object):
        """this is for adding objects all objects which need to be drawn"""
        self.objects.append(Object)

    def createLineSet(self):
        """creates a line set for reference points on the screen"""
        def getGridStep():
            """returns a grid point which is closest to the  point"""
            raw_step = 100 * self.zoom
            exponent = m.floor(m.log10(raw_step))
            base = [1 if (raw_step / (10 ** exponent))<3 else 10]
            return base[0] * (10 ** exponent)

        def roundToGrid(value, step):
            return round(value / step) * step
        for group in self.LineSet:
            for line in group:
                self.canvas.delete(line)
        bigLineDist = getGridStep()
        smallLineDist = bigLineDist/2
        ohoek = Position2D(0,0,root=self).convertToWorld()
        lhoek = self.screenSize.convertToWorld()
        oohoek = Position2D(roundToGrid(ohoek.x,smallLineDist),roundToGrid(ohoek.y,smallLineDist),root=self)
        llhoek = Position2D(roundToGrid(lhoek.x,smallLineDist),roundToGrid(lhoek.y,smallLineDist),root=self)
        vertLineSet = [oohoek.x + smallLineDist * i for i in range(int((llhoek.x-oohoek.x)/smallLineDist))]
        horLineSet = [oohoek.y + smallLineDist * i for i in range(int((llhoek.y-oohoek.y)/smallLineDist))]
        lineSetNew = []
        for z in vertLineSet:
            p1 = Position2D(x=z, y=ohoek.y,root=self).convertToScreen()
            p2 = Position2D(x=z, y=lhoek.y,root=self).convertToScreen()
            lineSetNew.append(self.canvas.create_line(p1.x, p1.y, p2.x, p2.y, fill="red", width=1))
        for z in horLineSet:
            p1 = Position2D(x=ohoek.x, y=z,root=self).convertToScreen()
            p2 = Position2D(x=lhoek.x, y=z,root=self).convertToScreen()

            lineSetNew.append(self.canvas.create_line(p1.x, p1.y, p2.x, p2.y, fill="red", width=1))
        
        return [lineSetNew]

# class Frame(tk.Frame):
#     def __init__(self):
#         super().__init__()

class Position2D():
    """
    This class is a modified version of the class positio2d in engine.py to be usable in the gui
    I mainly added functions for point conversion to other numbers and acces to variables from the mainWindow
    
    """
    def __init__(self, x: float, y: float, root = "root"):
        self.x = x
        self.y = y
        self.root = root

    def __sub__(self, other) -> Position2D:
        if not isinstance(other, Position2D):
            return NotImplemented
        x = self.x - other.x
        y = self.y - other.y
        del self
        return Position2D(x, y,root=root)
    
    def __add__(self, other) -> Position2D:
        if not isinstance(other, Position2D):
            return NotImplemented
        x = self.x + other.x
        y = self.y + other.y
        del self
        return Position2D(x, y,root=self.root)

    def __str__(self):
        return str(self.pack())
    
    def __mul__(self, other) -> Position2D:
        if not isinstance(other, (float, int)):
            return NotImplemented
        x = self.x * other
        y = self.y * other
        del self
        return Position2D(x, y,root=self.root)
    
    def __truediv__(self, other) -> Position2D:
        if not isinstance(other, (float, int)):
            return NotImplemented
        x = self.x / other
        y = self.y / other
        del self
        return Position2D(x, y,root=self.root)

    def pack(self) -> tuple[float, float]:
        """returns the x and y in an tuple"""
        return (self.x, self.y)

    def update(self, x: float, y: float) -> None:
        """takes to new values to change the objects coordinates to"""
        self.x = x
        self.y = y

    def normalize(self) -> Position2D:
        x = 1 if self.x > 0 else -1 if self.x < 0 else 0
        y = 1 if self.y > 0 else -1 if self.y < 0 else 0
        del self
        return Position2D(x, y,root=self.root)
    
    def copy(self):
        return Position2D(self.x, self.y,root=self.root)
    
    def convertToScreen(self):
        x = (self.x-self.root.worldCenter.x)/self.root.zoom + self.root.screenCenter.x
        y = (self.y-self.root.worldCenter.y)/self.root.zoom + self.root.screenCenter.y
        return Position2D(x,y,root=self.root)
    
    def convertToWorld(self):
        x = (self.x - self.root.screenCenter.x)*self.root.zoom + self.root.worldCenter.x
        y = (self.y - self.root.screenCenter.y)*self.root.zoom + self.root.worldCenter.y
        return Position2D(x,y,root=self.root)

class Object2D():
    """
    Parameters:
    root (Engine2D): Root of this Object
    Point1 (Position2D): Corner one of the Object
    Point2 (Position2D): Corner opposite to Point1 of the Object
    mass (float, optional): Mass of the object. Defaults to 1
    """
    def __init__(self,pointList:list ,mass: float=1,root="root",bg="purple"):
        self.bg = bg
        self.root = root
        self.pointList = pointList
        self.Middle = Position2D(sum(point.x for point in self.pointList)/2, sum(point.y for point in self.pointList)/2,root=self.root) # Average of X and Y: middle of the object
        self.root.addObject(self)

    def __str__(self):
        return str(point.pack() for point in self.pointList)

    def place(self):
        windowPoints = [point.convertToScreen() for point in self.pointList]
        self.root.canvas.create_polygon([coord for point in windowPoints for coord in point.pack()],fill=self.bg)

if __name__ == "__main__":
    root = MainWindow()
    root.renderButtons()
    hallo = Object2D(pointList = [Position2D(20,200,root=root),Position2D(1000,200,root=root),Position2D(1000,1000,root=root),Position2D(200,1000,root=root)],root=root)
    Gitta = Object2D(pointList= [Position2D(50,300, root=root),Position2D(900,400,root=root),Position2D(50,500,root=root),Position2D(900,500,root=root),Position2D(333,222,root=root)],root=root,bg="green")
    root.start()