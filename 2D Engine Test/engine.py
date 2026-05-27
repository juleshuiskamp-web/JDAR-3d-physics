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
    
    def normalize(self) -> Point:
        def n(coord): # Helper function to prevent writing this twice
            return 1 if coord > 0 else -1 if coord < 0 else 0
        return Point(n(self.x), n(self.y))
    
    def abs(self) -> Point:
        """Returns a new point with the absolute values of x and y"""
        return Point(abs(self.x), abs(self.y))

    def copy(self) -> Point:
        return Point(self.x, self.y)

class Object2D:
    id: int
    """Identifier set by engine2D.add"""

    mass: float
    """Mass of the object in kg"""
    middle: Point
    """middle point of this object (m for short)"""

    points: list[Point]
    """Format: bottom left, top right"""
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
        self.points = [Point(xmin, ymin), Point(xmax, ymax)]
        self.middle = Point((xmin + xmax) / 2, (ymin + ymax) / 2)
        self.range = Point((xmax - xmin) / 2, (ymax - ymin) / 2) # Avg range for collisions

        self.static = static
        self.velocity = Point(0, 0)
        self.acceleration = Point(0, 0)

    def collide(self, other: Object2D):
        """
        Returns
            does collide?, xoverlap, yoverlap
        """
        assert isinstance(other, Object2D)
        delta = (other.middle - self.middle).abs()
        overlap = (self.range + other.range) - delta
        
        if overlap.x <= 0 or overlap.y <= 0:
            return False, 0, 0

        if overlap.x > overlap.y:
            return True, 0, max(0, overlap.y)  * (-1 if self.middle.y < other.middle.y else 1)
        else:
            return True, max(0, overlap.x) * (-1 if self.middle.x < other.middle.x else 1), 0
    
    def move(self, x: float, y: float) -> None:
        for point in self.points:
            point.x += x
            point.y += y
        self.middle.x += x
        self.middle.y += y

    def damp(self, dampening: float, overlapx: float, overlapy: float) -> None:
        if overlapx != 0:
            self.velocity.x *= -dampening
        if overlapy != 0:
            self.velocity.y *= -dampening

class Engine:
    objects: set[Object2D]
    phys: float
    """Physics scaler. Used for making the simulation move objects faster"""

    def __init__(self, gravity_multiplier: float=9.81, dampening: float=0.8, physics_scaler: float=1, friction: float=0.999):
        """
        Create a new physics engine.

        Args:
            gravity_multiplier: Global gravity multiplier. Defaults to 9.81 (earth)
            dampening: Dampening applied on collision
            physics_scaler: Multiplier on physics forces
            friction: Multiplier for all forces (applied every tick). Number between 0 and 1. 1 is no friction and 0 is no movement
        """
        self.grav = gravity_multiplier
        self.dampening = dampening
        self.phys = physics_scaler
        self.friction = max(min(friction, 1), 0)

        self.objects = set()

    def add(self, *objects: Object2D):
        for object in objects:
            object.id = len(self.objects)
            self.objects.add(object)
        self.update()
    
    def update(self):
        self.combs = [ comb for comb in combinations(self.objects, 2) if not (comb[0].static and comb[1].static) ]

    def tick(self, dt: float=0.0166):
        if len(self.objects) == 0:
            return
        # Apply gravity, velocity and acceleration
        for object in self.objects:
            if object.static: continue
    
            deltaforce = Point(0, -self.grav * object.mass) # For now only gravitational force

            object.acceleration.x, object.acceleration.y = deltaforce.x / object.mass, deltaforce.y / object.mass

            # Apply friction
            object.velocity *= self.friction
            object.velocity.x += object.acceleration.x * dt * self.phys
            object.velocity.y += object.acceleration.y * dt * self.phys

            object.move(object.velocity.x * dt, object.velocity.y * dt)

        if len(self.objects) == 1:
            return
        
        # Simple bounce
        for object1, object2 in self.combs:
            collision, overlapx, overlapy = object1.collide(object2)
            if collision: 
                m1 = 1 if object2.static else 0.5
                m2 = 1 if object1.static else 0.5

                if (not object1.static) and (not object2.static):
                    v1, v2 = object1.velocity.copy(), object2.velocity.copy()
                    object1.velocity, object2.velocity = v2, v1
                else:
                    object1.damp(self.dampening, overlapx, overlapy)
                    object2.damp(self.dampening, overlapx, overlapy)

                if not object1.static:
                    object1.move(overlapx * m1, overlapy * m1)
                if not object2.static:
                    object2.move(-overlapx * m2, -overlapy * m2)