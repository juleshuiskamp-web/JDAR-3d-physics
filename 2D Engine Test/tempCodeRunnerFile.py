from __future__ import annotations
import engine
import pyglet

PFPS = 120 # Physics frames per second
OFFSET = (100, 100)
SCALE = 10

class GUI_Object:
    def __init__(self, viewer: Viewer, point1: engine.Point, point2: engine.Point, static: bool=False, offset: tuple[int, int]=(0, 0), scale: int=1):
        viewer.push_handlers(self)

        self.object = engine.Object2D(point1, point2, static=static)
        viewer.engine.add(self.object)
        
        dx = abs(point2.x - point1.x) * scale # Width
        dy = abs(point2.y - point1.y) * scale # Height
        self.shape = pyglet.shapes.Rectangle(-dx, -dy, dx, dy, batch=viewer.batch, color=(200, 100, 0))
        self.offset = offset
        self.scale = scale

    def on_mouse_press(self, x, y, button, modifiers):
        return super().on_mouse_press(x, y, button, modifiers)
    
    def update(self):
        pos = [ coord * self.scale for coord in self.object.points[0].pack() ]
        pos[0] += self.offset[0]
        pos[1] += self.offset[1]
        self.shape.position = pos

class Viewer(pyglet.window.Window):
    def __init__(self):
        super().__init__(fullscreen=True)

        # Graphics
        self.batch = pyglet.graphics.Batch()
        pyglet.clock.schedule_interval(self.engine_update, 1/PFPS)
        self.graph_mult = 5
        self.engine = engine.Engine(gravity_multiplier=5, physics_scaler=4)
        self.objects = [ 
            GUI_Object(self, engine.Point(10, 10), engine.Point(100, 30), static=True, offset=OFFSET, scale=SCALE), 
            GUI_Object(self, engine.Point(10, 40), engine.Point(30, 60), offset=OFFSET, scale=SCALE), 
            GUI_Object(self, engine.Point(110, 20), engine.Point(130, 80), static=True, offset=OFFSET, scale=SCALE),
            GUI_Object(self, engine.Point(0, 20), engine.Point(5, 100), static=True, offset=OFFSET, scale=SCALE)
            ]
        
        self.objects[1].object.velocity = engine.Point(40, 30)

    def engine_update(self, dt):
        self.engine.tick(dt)

        for object in self.objects:
            object.update()

    def on_draw(self):
        self.clear()
        self.batch.draw()

v = Viewer()
pyglet.app.run()