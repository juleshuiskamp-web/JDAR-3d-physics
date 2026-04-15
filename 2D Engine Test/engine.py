from __future__ import annotations # Makes circular references possible
import engineErrors as e
import math

EPSILON = 10 ** -9 # Small number used for collision checks etc

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

    def distance(self, point: Position2D) -> float:
        d = math.sqrt((point.x - self.x)**2 + (point.y - self.y)**2)
        return d

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

class Vector2D():
    def __init__(self, origin: Position2D, target: Position2D, force: float):
        """
        Parameters:
        origin (Position2D): Origin of the force
        target (Position2D): Target of the force
        force (float): Force from the Origin to the Target
        """
        self.origin = origin
        self.force = force
        target -= origin # Change target so it is in perspective to the origin
        
        # Calculate lenght and normalize so 1 == 1N
        lenght = math.sqrt(target.x ** 2 + target.y ** 2)
        target /= lenght
        target *= force

        target += origin
        self.target = target

    def __add__(self, other):
        if isinstance(other, Vector2D):
            if not self.origin.pack() == other.origin.pack():
                raise e.InvalidOriginsError(f"Origins {self.origin} and {other.origin} are different")
            target = self.target - self.origin # normalize targets so it is in perspective to the origin
            other.target -= self.origin
            target += other.target
            origin = self.origin
            force = self.force + other.force
            del self # Clean up
            return Vector2D(origin, target, force)
        if isinstance(other, (int, float)): # Check if other is a integer or float
            origin = self.origin
            force = self.force + other
            # Calculate new target
            target = self.target - self.origin
            target /= self.force
            target *= force
            del self # Clean up
            return Vector2D(origin, target, force)
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
        infinite (bool, optional): Should the line after the two points. Defaults to false
        """
        
        self.infinite = infinite
        if Point1.pack() == Point2.pack() and not infinite:
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
    
    def distance(self, point: Position2D):
        if self.vertical: # Vertical line: distance is x difference
            return abs(self.vertical - point.x)
        elif self.slope == 0: # Horizontal line: distance is y difference
            return abs(self.bias - point.y)
        
        # Find perpendicular line
        pSlope = -1 / self.slope
        pBias = point.y - pSlope * point.x

        # Solve intersection between lines
        # pSlope*x + pBias = self.slope*x + self.bias
        crossX = (pBias - self.bias) / (self.slope - pSlope)

        if not self.infinite: # Line is segment
            if not self.Point1.x >= crossX >= self.Point2.x:
                # Shortest distance is either endpoint
                distance = min(point.distance(self.Point1), point.distance(self.Point2))
                return distance
        crossY = self.slope * crossX + self.bias
        intersection = Position2D(crossX, crossY)
        return intersection.distance(point)

    def __truediv__(self, other):
        if not isinstance(other, Position2D):
            return NotImplemented
        crossPoint = False # Defaults to no cross point

        # Specifics: vertical and horizontal line:
        if not self.vertical is None:
            if other.x == self.vertical:
                crossPoint = Position2D(other.x, other.y)
            else:
                return False
        if self.slope == 0: 
            if other.y == self.bias: # Horizontal line + line goes over point
                crossPoint = Position2D(other.x, other.y)
            else:
                return False
        # Check for crossing between Line and Dot
        doesLineAndDotCross = self.bias == other.y - self.slope * other.x
        if doesLineAndDotCross:
            crossPoint = Position2D(other.x, other.y)
        selfYs = (min(self.Point1.y, self.Point2.y), max(self.Point1.y, self.Point2.y))
        # Check if point is possible on the line

        invalidX = not self.Point2.x >= other.x >= self.Point1.x
        invalidY = False if not self.vertical is None else not selfYs[0] >= other.y >= selfYs[1] 

        if (not self.infinite) and (invalidX or invalidY):
            # X is invalid or Y is invalid
            return False
        
        # Returns default (False) if no crossPoint is found
        return crossPoint
    
    def __str__(self):
        return str(self.pack())

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
        self.forces = set()

        # Check if points are valid
        pointsInvalid = any([ Coordinate1 == Coordinate2 for Coordinate1, Coordinate2 in zip(Point1.pack(), Point2.pack()) ])
        if pointsInvalid:
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
        self.Middle = Position2D(sum(xCoordinates)/2, sum(yCoordinates)/2) # Average of X and Y: middle of the object
        
        # Create all four corners
        # [bottomLeft, topLeft, topRight, bottomRight]
        self.corners = [Point1, Position2D(Point1.x, Point2.y), Point2, Position2D(Point2.x, Point1.y)]
        
        # Add to root after creating corners so collisionchecks can actually happen
        root.addObject(self)

    def __truediv__(self, other):
        if not isinstance(other, Object2D):
            return NotImplemented

        # Other is a Object2D --> Check for collision between each corner of self and the other Object
        # Create lines of the vertices of the other Object
        # [ bottom, left, top, right ] collisions between other corners
        other_vertices = [ Line2D(corner, other.corners[i-1]) for i, corner in enumerate(other.corners) ]

        collisions = [ vertice / point for vertice in other_vertices for point in self.corners ]
        return collisions

    def __str__(self):
        return str(self.pack())
    
    def move(self, x: float=0, y: float=0, checkCollisions: bool=False):
        """
        Move the targetted object by x and y.
        Parameters:
        x (float, optional): X movement
        y (float, optional): Y movement
        checkCollisions (bool, optional): Check for collisions during movement? Defaults to False. NOT IMPLEMENTED YET
        """
        for corner in self.corners:
            corner.x += x
            corner.y += y

    def pack(self):
        return tuple([ corner.pack() for corner in self.corners ])

class Engine2D():
    def __init__(self, Gravity: float=1):
        """
        Create a new Engine to place objects in
        Parameters:
        Gravity (float, optional): Gravity multiplier. Defaults to 1
        """
        self.gravity = Gravity
        self.objects = []

    def addObject(self, Object: Object2D, ignorecollisions: bool=False):
        """
        Add a object to the Engine and check if it doesnt interfere with other Objects
        Parameters:
        Object (Object2D): Object to add to the Engine
        ignorecollisions (bool, optional): Should the Engine ignore collisions when spawning the Object? Defaults to False
        """

        if not ignorecollisions:
            for collisionObject in self.objects:
                # Find direction from new Object to other Object and normalize it
                direction = (collisionObject.Middle - Object.Middle).normalize()
                # Multiply direction by EPSILION to get a extremly small direction number
                direction *= EPSILON
                # Move the other object so it wont collide
                collisionObject.move(direction.x, direction.y)

                if any(Object / collisionObject): # New object collides with the collisionObject
                    raise e.EngineNewObjectCollisionError(f"This object collides with another object!")
                # Move other object back (obviously)
                collisionObject.move(-direction.x, -direction.y)

        self.objects.append(Object)

    def renderTick(self) -> None:
        """
        Render a singular tick.
        - Applies gravity to all object
        - Detects collision
        """
        # Apply gravity
        for object in self.objects:
            # Calculate gravity vector
            target = object.Middle + Position2D(0, -1)
            gravity = Vector2D(object.Middle, target, 9.81 * self.gravity)
            object.forces.add(gravity)

        objectCombinations = [ (object1, object2) for object1 in self.objects for object2 in self.objects ]
        collisions = []
        
        for object1, object2 in objectCombinations:
            collisions.append(object1 / object2)

if __name__ == "__main__":
    p = Position2D(2, -2)
    p2 = Position2D(5, 0)
    p3 = Position2D(4, 10)
    l = Line2D(p, p2)
    print(l.distance(p3))

    # origin = Position2D(2, -2)
    # target = Position2D(4, -6)
    # origin2 = Position2D(2, -2)
    # target2 = Position2D(4, 4)
    # root = Engine2D()
    # object1 = Object2D(root, target, origin)
    # object2 = Object2D(root, target2, origin2)
    # print(object1 / object2)
    # root.renderTick()