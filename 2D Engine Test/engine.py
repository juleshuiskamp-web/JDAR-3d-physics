from __future__ import annotations # Makes circular references possible
import engineErrors as e

class Position2D():
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    def pack(self) -> tuple[float, float]:
        return (self.x, self.y)
    def update(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

class Vector2D():
    def __init__(self, origin: Position2D, target: Position2D, force: float):
        """
        Parameters:
        origin (Position2D): Origin of the force
        target (Position2D): Target of the force
        force (float): Force from the Origin to the Target
        """
        self.origin = origin
        self.target = target
        self.force = force

    def __add__(self, other):
        if isinstance(other, Vector2D):
            # Create new target X and Y
            X, Y = other.target.x - other.origin.x, other.target.y - other.origin.y
            # Create a new target Position2D
            target = Position2D(self.target.x + X, self.target.y + Y)
            # Return new Vector
            return Vector2D(self.origin, target, self.force + other.force)
        if isinstance(other, (int, float)): # Check if other is a integer or float
            # Return new Vector2D with added force
            return Vector2D(self.origin, self.target, self.force + other)
        return NotImplemented
    
    def pack(self) -> tuple[tuple[float, float], tuple[float, float], float]:
        return (self.origin.pack(), self.target.pack(), self.force)

class Line2D():
    def __init__(self, Point1: Position2D, Point2: Position2D, infinite: bool=False):
        """
        Create a line between two points
        Parameters:
        Point1 (Position2D): Point 1
        Point2 (Position2D): Point 2
        infinite (bool, optional): Should the line continue after the two points. Defaults to false
        """
        
        self.infinite = infinite
        if Point1.x == Point2.x and Point1.y == Point2.y and not infinite:
            raise e.InvalidCoordinatesError(f"Point {Point1.pack()} and Point {Point2.pack()} are on the same location.\n- Did you mean to use Position2D instead?")
        self.Point1, self.Point2 = (Point1, Point2) if Point1.x <= Point2.x else (Point2, Point1) # Point 1 forced to be the most left point

        self.vertical = None
        # Find the slope of the line
        if Point1.x == Point2.x:
            self.slope = 0
            if Point1.y != Point2.y:
                # Vertical line
                self.vertical = Point1.x
            self.bias = 0
        else:
            self.slope = (Point1.y - Point2.y) / (Point1.x - Point2.x)
            # Find the bias of the line
            self.bias = self.Point1.y - self.slope * Point1.x

        print(f"Slope: {self.slope} - Bias: {self.bias} ({Point1.pack()}, {Point2.pack()}) Vertical: {self.vertical}")

    def __truediv__(self, other):
        if not isinstance(other, Position2D):
            return NotImplemented
        # Check for crossing between Line and Dot
        doesLineAndDotCross = self.bias == other.y - self.slope * other.x
        if doesLineAndDotCross:
            crossX = (other.y - self.bias) / self.slope
            crossY = self.slope * crossX + self.bias # Fill into own line formula

            # If self is not infinite, make sure to check if the option is actually valid
            if (not self.infinite) and (not self.Point2.x >= crossX >= self.Point1.x):
                return None
            # Return new position with the CrossX and CrossY
            return Position2D(crossX, crossY)

    def pack(self) -> tuple[tuple[float, float], tuple[float, float]]:
        return (self.Point1.pack(), self.Point2.pack())

class Object2D():
    def __init__(self, root: Engine2D, Point1: Position2D, Point2: Position2D, mass: float=1):
        """
        Parameters:
        root (Engine2D): Root of this Object
        Point1 (Position2D): Corner one of the Object
        Point2 (Position2D): Corner opposite to Point1 of the Object
        mass (float, optional): Mass of the object. Defaults to 1
        """
        self.root = root
        root.addObject(self)

        # Check if points are valid
        pointsValid = any([ Coordinate1 == Coordinate2 for Coordinate1, Coordinate2 in zip(Point1.pack(), Point2.pack()) ])
        if pointsValid:
            # Points have equal X or Y coordinates
            raise e.InvalidCoordinatesError(f"Point {Point1.pack()} and Point {Point2.pack()} are not opposite corners")
        
        # # # # # # # # # # # # # # # # # # #
        #       CORNER RECONSTRUCTION       #
        # # # # # # # # # # # # # # # # # # #
        # Make sure Point1 is always at the bottom left and Point2 at the top right
        xCoordinates = (Point1.x, Point2.x)
        yCoordinates = (Point1.y, Point2.y)
        Point1.update(x = min(xCoordinates), y = min(yCoordinates))
        Point2.update(x = max(xCoordinates), y = max(yCoordinates))
        
        # Create all four corners
        # [bottomLeft, topLeft, topRight, bottomRight]
        self.corners = [Point1, Position2D(Point1.x, Point2.y), Point2, Position2D(Point2.x, Point1.y)]
        
    def __truediv__(self, other):
        if not isinstance(other, Object2D):
            return NotImplemented
        # Other is a Object2D --> Check for collision between each corner of self and the other Object
        # Create lines of the vertices of the other Object
        other_vertices = [ Line2D(corner, other.corners[i+1]) for i, corner in enumerate(other.corners) if not i > 2 ]
        other_vertices.append(Line2D(other.corners[0], other.corners[3])) # Final vertice
        print("Vertices:", ' '.join([ str(vertice.pack()) for vertice in other_vertices]))

class Engine2D():
    def __init__(self, Gravity: float=1):
        """
        Create a new Engine
        Parameters:
        Gravity (float, optional): Gravity multiplier. Defaults to 1
        """
        self.gravity = Gravity
        self.objects = []

    def addObject(self, Object: Object2D, Gravity: float=1):
        """
        Add a object to the Engine
        Parameters:
        Object (Object2D): Object to add to the Engine
        """
        #TODO: Add Collision checks to prevent the new Object from being added if it is
        #      in another object
        self.objects.append(Object)

    def renderTick(self):
        """
        Render a singular tick.
        - Applies gravity to all object
        - Detects collision
        """


if __name__ == "__main__":
    origin = Position2D(2, -2)
    target = Position2D(4, -6)
    line = Line2D(origin, target)
    print((line / Position2D(6, -8)))
    root = Engine2D()
    d = Vector2D(origin, target, 4)
    g = Vector2D(origin, target, 4)
    print(f"PACKED: {(d + g).pack()}")
    object = Object2D(root, target, origin)
    object2 = Object2D(root, target, origin)
    print(f"{object / object2}")