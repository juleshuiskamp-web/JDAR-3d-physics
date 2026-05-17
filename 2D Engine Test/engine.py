from __future__ import annotations
import math
from itertools import combinations  

class Point:
    def __init__(self, x: int | float, y: int | float):
        self.x, self.y = x, y

    def __sub__(self, other):
        assert isinstance(other, Point)
        return Point(self.x - other.x, self.y - other.y)
    
    def __truediv__(self, other):
        return Point(self.x / other, self.y / other)
    
    def __mul__(self, other):
        return Point(self.x * other, self.y * other)
    
    def __add__(self, other):
        assert isinstance(other, Point)
        return Point(self.x + other.x, self.y + other.y)

    def pack(self) -> tuple[int | float, int | float]:
        return self.x, self.y
    
    def rotated(self, pivot: Point, angle: int) -> Point:
        """
        Rotate self around the pivot. Returns a new point.
        
        Args:
            pivot: Point to rotate self around
            angle: Angle (in degrees)
        """
        angle = math.radians(angle)
        dx, dy = (self.x - pivot.x), (self.y - pivot.y) # Transform to local space
        x = pivot.x + math.cos(angle) * dx - math.sin(angle) * dy
        y = pivot.y + math.sin(angle) * dx + math.cos(angle) * dy
        return Point(x, y)
    
class Vector2D():
    def __init__(self, origin: Point, target: Point, force: float):
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
            assert self.origin.pack() == other.origin.pack(), f"Origins {self.origin.pack()} and {other.origin.pack()} are different"
            target = self.target - self.origin # normalize targets so it is in perspective to the origin
            other.target -= self.origin
            target += other.target
            origin = self.origin
            force = self.force + other.force
            return Vector2D(origin, target, force)
        if isinstance(other, (int, float)): # Check if other is a integer or float
            origin = self.origin
            force = self.force + other
            # Calculate new target
            target = self.target - self.origin
            target /= self.force
            target *= force
            return Vector2D(origin, target, force)
        return NotImplemented

    def pack(self) -> tuple[tuple[float, float], tuple[float, float], float]:
        return (self.origin.pack(), self.target.pack(), self.force)

class Object2D:
    angle: int
    """Rotation in degrees"""
    mass: float
    """Mass of the object in kg"""

    force: Vector2D
    points: list[Point]
    def __init__(self, point1: Point, point2: Point, static: bool=False, mass: float=1):
        """
        Args:
            point1: One corner of the object
            point2: Other corner of the object, opposite to point1
            static: Should forces be applied to the object
            mass: Mass of the object
        """
        self.mass = mass
        xmin, xmax = min(point1.x, point2.x), max(point1.x, point2.x)
        ymin, ymax = min(point1.y, point2.y), max(point1.y, point2.y)
        self.points = [Point(xmin, ymin), Point(xmax, ymax), Point(xmin, ymax), Point(xmax, ymin)]
        self.m = Point((xmin + xmax) / 2, (ymin + ymax) / 2)

        self.angle = 0
        self.force = None
        self.static = static
        self.velocity = Point(0, 0)
        self.acceleration = Point(0, 0)

    def check_collision(self, object: Object2D, point: Point) -> bool:
        # Transform into local space of object and rotate the point
        rotated = point.rotated(object.m, -object.angle)
        # Check for collision
        if (object.points[0].x <= rotated.x <= object.points[1].x and object.points[0].y <= rotated.y <= object.points[1].y):
            return True
        return False

    def collide(self, other: Object2D) -> bool:
        for point in self.points:
            if self.check_collision(other, point):
                return True
        return False
    
    def move(self, x: float, y: float) -> None:
        for point in self.points:
            point.x += x
            point.y += y
        self.m.x += x
        self.m.y += y

    def reverse(self, dampening: float) -> None:
        """Reverses both velocitys from self. Only if not static"""
        if self.static:
            return
        
        self.velocity *= -dampening

class Engine:
    objects: set[Object2D]
    def __init__(self, gravity_multiplier: float=9.81, dampening: float=0.8, physics_scaler: float=1):
        """
        Create a new physics engine.

        Args:
            gravity_multiplier: Global gravity multiplier. Defaults to 9.81 (earth)
            dampening: Dampening applied on collision
            physics_scaler: Multiplier on physics forces
        """
        self.grav = gravity_multiplier
        self.dampening = dampening
        self.phys = physics_scaler

        self.objects = set()

    def add(self, *objects: Object2D):
        for object in objects:
            self.objects.add(object)
        self.update()
    
    def update(self):
        self.combs = list(combinations(self.objects, 2))

    def doubleCheck(self, object1: Object2D, object2: Object2D):
        if object1.collide(object2):
            return True
        if object2.collide(object1):
            return True
        return False

    def tick(self, dt: float=0.0166):
        if len(self.objects) == 0:
            return
        # Apply gravity, velocity and acceleration
        for i, object in enumerate(self.objects):
            if object.static: continue
            
            collides = False, None
            for ic, cobject in enumerate(self.objects):
                if ic == i: continue
                if self.doubleCheck(cobject, object):
                    collides = True, cobject
                    break
            df = Point(0, -self.grav * object.mass) # For now only gravitational force

            object.acceleration.x, object.acceleration.y = df.x / object.mass, df.y / object.mass
            object.velocity.x += object.acceleration.x * dt * self.phys
            object.velocity.y += object.acceleration.y * dt * self.phys

            object.move(object.velocity.x * dt, object.velocity.y * dt)

            if collides[0] and cobject.static:
                # Object collides with is cobject
                if self.doubleCheck(cobject, object): # Still collides, so move object back to prevent falling trough. Not sure if this breaks something, nor do i want to find out
                    object.move(-object.velocity.x * dt, -object.velocity.y * dt)

        if len(self.objects) == 1:
            return
        
        # Simple bounce
        for object1, object2 in self.combs:
            if self.doubleCheck(object1, object2):
                print("COLLISION")
                object1.reverse(self.dampening)
                object2.reverse(self.dampening)
            
o1 = Object2D(Point(10, 10), Point(20, 20))
o2 = Object2D(Point(10, 30), Point(20, 20))
o2.angle = 90

print(o1.collide(o2))