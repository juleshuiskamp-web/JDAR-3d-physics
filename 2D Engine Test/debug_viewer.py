import engine
import pyglet

PFPS = 120 # Physics frames per second

class Viewer(pyglet.window.Window):
    def __init__(self):
        super().__init__()

        pyglet.clock.schedule_interval(self.engine_update, 1/PFPS)
        self.graph_mult = 5
        self.engine = engine.Engine(gravity_multiplier=5, physics_scaler=4)
        self.objects = [ engine.Object2D(engine.Point(10, 10), engine.Point(100, 30), static=True), engine.Object2D(engine.Point(10, 40), engine.Point(30, 60)), engine.Object2D(engine.Point(70, 40), engine.Point(90, 60)) ]
        self.objects[1].velocity = engine.Point(20, 30)
        self.engine.add(*self.objects)

        # Graphics
        self.batch = pyglet.graphics.Batch()
        self.shapes = [ pyglet.shapes.Rectangle(10, 10, 20, 20, batch=self.batch, color=(100, 0, 0)), pyglet.shapes.Rectangle(10, 40, 20, 20, batch=self.batch, color=(0, 100, 0)), pyglet.shapes.Rectangle(0, 0, 0, 0, batch=self.batch, color=(0, 0, 100)) ]

    def engine_update(self, dt):
        self.engine.tick(dt)

        for i, shape in enumerate(self.shapes):
            object = self.objects[i]
            cl, cr = object.points[0], object.points[1] # Corner left, corner right
            width, height = cr.x - cl.x, cr.y - cl.y
            shape.position = (cl * self.graph_mult).pack()
            shape.width, shape.height = width * self.graph_mult, height * self.graph_mult

    def on_draw(self):
        self.clear()
        self.batch.draw()

v = Viewer()
pyglet.app.run()