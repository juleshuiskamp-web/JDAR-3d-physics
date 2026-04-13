import tkinter as tk,math as m,random as r,_2D_Engine_Test.engineErrors as e

class mainWindow():
    def __init__(self,):
        self.zoom = 1
        self.center = [0,0]
        self.lastMousePos = [0,0]
        self.dragging = False

        self.window = tk.Tk()
        self.window.title("2d physics")
        self.screenWidth = self.window.winfo_screenwidth()
        self.screenHeight = self.window.winfo_screenheight()
        self.window.geometry(f"{self.screenWidth}x{self.screenHeight}")

        self.options = tk.Frame(self.window, height=int(self.screenWidth/8),bg="lightgray")
        self.options.pack(side="top", fill="x")

        self.canvas = tk.Canvas(self.window,bg="lightblue",bd="0",highlightthickness=0)
        self.canvas.pack(side="left", fill="both",expand=True)

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

    def draw(self,):
        self.canvas.delete("all")
        self.LineSet = self.createLineSet()

        for i in range(10):
            for j in range(10):
                x = (i*100-self.center[0])/self.zoom+self.screenWidth/2
                y = (j*100-self.center[1])/self.zoom+self.screenHeight/2
                size = 5 / self.zoom
                self.canvas.create_oval(x-size, y-size, x+size, y+size, fill="white")

    def draggin(self,event):
        if not self.dragging:
            return
        dx = -1*(event.x - self.lastMousePos[0])
        dy = -1*(event.y - self.lastMousePos[1])
        self.center[0] += dx
        self.center[1] += dy
        self.lastMousePos = [event.x, event.y]
        self.draw()
    
    def rightClick(self,event):
        self.dragging = True
        self.lastMousePos = [event.x, event.y]
    
    def rightRelease(self,event):
        self.dragging = False
    
    def zooming(self,event):
        factor = 1.1 if event.delta > 0 else 0.9
        self.zoom *= factor
        self.draw()

    def elements(self):
        pass

    def start(self):
        self.window.mainloop()

    def renderButtons(self):
        self.buttons = [tk.Button(self.options, text="refresh points", command=self.edito, width=5) for _ in range(8)]
        for i,button in enumerate(self.buttons):
            button.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            self.options.grid_columnconfigure(i, weight=1)

    def edito(self):
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
        self.objects.append(Object)

    def createLineSet(self):
        def getGridStep():
            target_pixels = 100  # how far apart lines should be visually

            # world units per pixel
            units_per_pixel = self.zoom

            raw_step = target_pixels * units_per_pixel

            # snap to nice numbers (1, 2, 5, 10, ...)
            exponent = m.floor(m.log10(raw_step))
            base = raw_step / (10 ** exponent)

            if base < 3:
                nice = 1
            else:
                nice = 10

            return nice * (10 ** exponent)
        def virToScreen( x, y):
            sx = (x - self.center[0]) / self.zoom + self.screenWidth / 2
            sy = (y - self.center[1]) / self.zoom + self.screenHeight / 2
            return sx, sy
        for group in self.LineSet:
            for line in group:
                self.canvas.delete(line)
        def roundToSTep(value, step):
            rounded = round(value / step) * step
            return rounded if rounded else 1
        def roundToGrid(value, step):
            return round(value / step) * step
        relScreenSize = "{:.20e}".format(self.screenWidth / self.zoom)
        relScreenSizeS = relScreenSize.split("e")
        power = relScreenSizeS[1]
        power = abs(int(power))
        relScreenSize = float(relScreenSizeS[0])
        bigLineDist = getGridStep()
        smallLineDist = bigLineDist/2
        ohoek = [self.center[0]-(self.screenWidth*self.zoom/2),self.center[1]-(self.screenHeight*self.zoom/2)]
        lhoek = [self.center[0]+(self.screenWidth*self.zoom/2),self.center[1]+(self.screenHeight*self.zoom/2)]
        oohoek = [roundToGrid(ohoek[0],smallLineDist),roundToGrid(ohoek[1],smallLineDist)]
        llhoek = [roundToGrid(lhoek[0],smallLineDist),roundToGrid(lhoek[1],smallLineDist)]
        vertLineSet = [oohoek[0] + smallLineDist * i for i in range(int(llhoek[0]/smallLineDist)-int(oohoek[0]/smallLineDist))]
        horLineSet = [oohoek[1] + smallLineDist * i for i in range(int((llhoek[1]-oohoek[1])/smallLineDist))]
        vertLineSetNew = []
        horLineSetNew = []
        for z in vertLineSet:
            x1, y1 = virToScreen(x=z, y=ohoek[1])
            x2, y2 = virToScreen(x=z, y=lhoek[1])
            vertLineSetNew.append(self.canvas.create_line(x1, y1, x2, y2, fill="red", width=1))
        for z in horLineSet:
            x1, y1 = virToScreen(x=ohoek[0], y=z)
            x2, y2 = virToScreen(x=lhoek[0], y=z)

            horLineSetNew.append(self.canvas.create_line(x1, y1, x2, y2, fill="red", width=1))
        
        return [vertLineSetNew,horLineSetNew]

class Position2D():
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __sub__(self, other) -> Position2D:
        if not isinstance(other, Position2D):
            return NotImplemented
        x = self.x - other.x
        y = self.y - other.y
        del self
        return Position2D(x, y)
    
    def __add__(self, other) -> Position2D:
        if not isinstance(other, Position2D):
            return NotImplemented
        x = self.x + other.x
        y = self.y + other.y
        del self
        return Position2D(x, y)

    def __str__(self):
        return str(self.pack())
    
    def __mul__(self, other) -> Position2D:
        if not isinstance(other, (float, int)):
            return NotImplemented
        x = self.x * other
        y = self.y * other
        del self
        return Position2D(x, y)
    
    def __truediv__(self, other) -> Position2D:
        if not isinstance(other, (float, int)):
            return NotImplemented
        x = self.x / other
        y = self.y / other
        del self
        return Position2D(x, y)

    def pack(self) -> tuple[float, float]:
        return (self.x, self.y)

    def update(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def normalize(self) -> Position2D:
        x = 1 if self.x > 0 else -1 if self.x < 0 else 0
        y = 1 if self.y > 0 else -1 if self.y < 0 else 0
        del self
        return Position2D(x, y)
    
    def copy(self):
        return Position2D(self.x, self.y)

class Object2D():
    def __init__(self, root: mainWindow, Point1: Position2D, Point2: Position2D,pointList:list,colour ,mass: float=1,):
        """
        Parameters:
        root (Engine2D): Root of this Object
        Point1 (Position2D): Corner one of the Object
        Point2 (Position2D): Corner opposite to Point1 of the Object
        mass (float, optional): Mass of the object. Defaults to 1
        """
        self.root = root
        self.pointList = []
        # Check if points are valid
        pointerList = pointList[:]
        for point1 in pointList:
            point1 = pointerList.remove(point1)
            for point in pointerList:
                if point == point1:
                    raise e.InvalidCoordinatesError(f"Point {Point1.pack()} and Point {Point2.pack()} are not opposite corners")
        
        for point in pointList:
            point2D = Position2D(zip(*point))
            self.pointList.append(point2D)
        # if pointsInvalid:
        #     # Points have equal X or Y coordinates
        #     raise e.InvalidCoordinatesError(f"Point {Point1.pack()} and Point {Point2.pack()} are not opposite corners")
        
        # Make sure Point1 is always at the bottom left and Point2 at the top right
        # xCoordinates = (Point1.x, Point2.x)
        # yCoordinates = (Point1.y, Point2.y)
        # Point1.update(x = min(xCoordinates), y = min(yCoordinates))
        # Point2.update(x = max(xCoordinates), y = max(yCoordinates))
        self.Middle = Position2D(sum(point.x for point.x in pointList)/2, sum(point.y for point in pointList)/2) # Average of X and Y: middle of the object
        
        # Create all four corners
        # [bottomLeft, topLeft, topRight, bottomRight]
        # self.corners = [Point1, Position2D(Point1.x, Point2.y), Point2, Position2D(Point2.x, Point1.y)]
        
        # Add to root after creating corners so collisionchecks can actually happen
        root.addObject(self)

    def __str__(self):
        return str(self.pack())

    def place(self,root):
        pointCollection = []
        for point in self.pointList:
            pointCollection.extend([])
        for x in 
        root.canvas.create_polygon(zip(*point.pack()) for point in pointList)

if __name__ == "__main__":
    root = mainWindow()
    root.renderButtons()
    root.start()