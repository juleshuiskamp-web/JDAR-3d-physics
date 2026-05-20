class Position2D():
    """
    This class is a modified version of the class positio2d in engine.py to be usable in the gui
    I mainly added functions for point conversion to other numbers and acces to variables from the mainWindow
    """

    default_root = "root"
    def __init__(self, x: float, y: float, root = False):
        self.x = x
        self.y = y
        self.root = self.default_root if not root else root

    def __getitem__(self, key):
        if not isinstance(key,int):
            return "not integer"
        if key == 0:return self.x
        elif key == 1:return self.y

    def __setitem__(self, key, value):
        assert isinstance(key,int), "key must be an integer"
        if key == 0:self.x = value
        elif key == 1: self.y = value

    def __sub__(self, other) -> Position2D:
        if not isinstance(other, Position2D):
            return NotImplemented
        x = self.x - other.x
        y = self.y - other.y
        return Position2D(x, y,root=self.root)
    
    def __add__(self, other) -> Position2D:
        if not isinstance(other, Position2D):
            return NotImplemented
        x = self.x + other.x
        y = self.y + other.y
        return Position2D(x, y,root=self.root)

    def __str__(self):
        return str(self.pack())
    
    def __mul__(self, other) -> Position2D:
        if not isinstance(other, (float, int)):
            return NotImplemented
        x = self.x * other
        y = self.y * other
        return Position2D(x, y,root= self.root)
    
    def __truediv__(self, other) -> Position2D:
        if not isinstance(other, (float, int)):
            return NotImplemented
        x = self.x / other
        y = self.y / other
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
        return Position2D(x, y,root=self.root)
    
    def copy(self):
        return Position2D(self.x, self.y,root=self.root)
    
    def convertToScreen(self):
        x = (self.x-self.root.worldCenter.x)/self.root.zoom + self.root.canvasCenter.x
        y = (self.y-self.root.worldCenter.y)/self.root.zoom + self.root.canvasCenter.y
        return Position2D(x,y,root=self.root)
    
    def convertToWorld(self):
        x = (self.x - self.root.canvasCenter.x)*self.root.zoom + self.root.worldCenter.x
        y = (self.y - self.root.canvasCenter.y)*self.root.zoom + self.root.worldCenter.y
        return Position2D(x,y,root=self.root)
    
    def covertToCenterScreen(self):
        return Position2D(x=self.x-1920/2,y=self.y-1080/2,root=self.root)
    
    def covertToNormalScreen(self):
        return Position2D(x=self.x+1920/2,y=self.y+1080/2,root=self.root)