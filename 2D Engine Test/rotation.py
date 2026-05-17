from __future__ import annotations
import pyglet
from pyglet.window import mouse
from math import sqrt, pow, cos, sin, radians

def clamp(value: int | float, minimum: int | float, maximum: int | float) -> int | float:
    return min(max(value, minimum), maximum)

def distance(p1: Point, p2: Point):
    return sqrt(pow(p1.x - p2.x, 2) + pow(p1.y - p2.y, 2))

def percent(value: int | float, minimum: int | float, maximum: int | float) -> int | float:
    x = maximum - minimum
    y = value - minimum
    return y / x

class Slider:
    def __init__(self, x: int, y: int, width: int, height: int, on_update, batch: pyglet.graphics.Batch, window: pyglet.window.BaseWindow):
        assert callable(on_update), "on_update must be a callable function"
        self.x, self.y, self.width, self.height, self.on_update = x, y, width, height, on_update

        window.push_handlers(self)
        self.slidebg = pyglet.shapes.Rectangle(x, y, width, height, color=(10, 10, 10), batch=batch)

        self.radius = height / 2
        self.M = Point(x, y + self.radius)
        self.slidebg1 = pyglet.shapes.Circle(x, y+self.radius, self.radius, color=(10, 10, 10), batch=batch)
        self.sidebg2 = pyglet.shapes.Circle(x+width, y+self.radius, self.radius, color=(10, 10, 10), batch=batch)
        self.slider = pyglet.shapes.Circle(x, y+self.radius, self.radius, color=(0, 100, 100), batch=batch)

        self.limits = (x, x+width)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not buttons & mouse.LEFT:
            return 
        if distance(Point(x, y), self.M) > self.radius + 2:
            return
        x = clamp(x, *self.limits)
        self.M.x = x
        self.slider.x = x
        self.on_update(percent(x, *self.limits))

class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def rotated(self, other: Point, angle: int) -> Point:
        angle = radians(angle)
        dx, dy = (self.x - other.x), (self.y - other.y)
        x = other.x + cos(angle) * dx - sin(angle) * dy
        y = other.y + sin(angle) * dx + cos(angle) * dy
        return Point(x, y)
    
    def pack(self):
        return self.x, self.y

class Rectangle:
    def __init__(self, p1: Point, p2: Point, batch: pyglet.graphics.Batch):
        self.p1 = Point(min(p1.x, p2.x), min(p1.y, p2.y))
        self.p2 = Point(max(p1.x, p2.x), max(p1.y, p2.y))
        
        width = self.p2.x - self.p1.x
        height = self.p2.y - self.p1.y
        self.shape = pyglet.shapes.Rectangle(p1.x, p1.y, width, height, batch=batch)
        self.shape.anchor_position = width // 2, height // 2
        
    def rotate(self, new_rotation: int):
        self.shape.rotation = new_rotation

class p:
    def __init__(self, x, y, batch: pyglet.graphics.Batch):
        self.position = Point(x, y)

        self.shape = pyglet.shapes.Circle(x, y, 5, batch=batch)
    
    def rotate(self, point: Point, rotation: int):
        new = self.position.rotated(point, rotation)
        self.shape.position = new.pack()


class Window(pyglet.window.Window):
    def __init__(self):
        super().__init__()
        self.set_caption("Point rotater")
        self.batch = pyglet.graphics.Batch()

        self.bg = pyglet.shapes.Rectangle(0, 0, self.width, self.height, color=(0, 60, 80), batch=self.batch)
        self.rect = Rectangle(Point(600, 400), Point(800, 600), self.batch)

        self.point = p(500, 420, self.batch)
        self.slide = Slider(100, self.height-100, 200, 40, self.on_update, self.batch, self)
        self.M = Point(700, 500)

    def on_draw(self):
        self.clear()

        self.batch.draw()

    def on_update(self, percent: float):
        rotation = round(percent * 360)
        # self.rect.rotate(rotation)
        M = Point(self.rect.shape.x, self.rect.shape.y)
        self.point.rotate(M, -rotation)


window = Window()
pyglet.app.run()