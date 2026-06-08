from __future__ import annotations
import math as m
import tkinter as tk
import time as t
from PIL import Image, ImageTk
import numpy as np
import engine

SCALE = 10
OFFSET = (100, 100)
TARGET_FPS = 20
FRAME_MS = 1000 // TARGET_FPS
CAM_ROT_SPEED = 0.05

class Position3D:
    """this is the class for making a 3d vector/point"""
    def __init__(self, Root=None, **kwargs):
        if all(k in kwargs for k in ("x", "y", "z")):
            self.x = float(kwargs["x"])
            self.y = float(kwargs["y"])
            self.z = float(kwargs["z"])
        else:
            self.x, self.y, self.z = (float(v) for v in next(
                kwargs[k] for k in kwargs if isinstance(kwargs[k], list)
            ))
        self.root = Root

    def __sub__(self, other):
        if not isinstance(other, Position3D): return NotImplemented
        return Position3D(x=self.x-other.x, y=self.y-other.y, z=self.z-other.z)

    def __add__(self, other):
        if not isinstance(other, Position3D): return NotImplemented
        return Position3D(x=self.x+other.x, y=self.y+other.y, z=self.z+other.z)

    def __mul__(self, other):
        if not isinstance(other, (float, int)): return NotImplemented
        return Position3D(x=self.x*other, y=self.y*other, z=self.z*other)

    def __truediv__(self, other):
        if not isinstance(other, (float, int)): return NotImplemented
        return Position3D(x=self.x/other, y=self.y/other, z=self.z/other)

    def __str__(self):
        return f"({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"

    def copy(self):
        return Position3D(x=self.x, y=self.y, z=self.z)

    def projector(self, fov: float, camera: 'Position3D', screen_w: int, screen_h: int):
        """
        Projects this point onto the screen.
        Returns (engine.Point, zDist) or None if behind camera.
        """
        fHoek = m.radians(fov / 2)
        focal_len = screen_w / 2 / m.tan(fHoek)
        zDist = self.z - camera.z
        if zDist <= 0:
            return None
        x = (self.x - camera.x) * focal_len / zDist + screen_w / 2
        y = (self.y - camera.y) * focal_len / zDist + screen_h / 2
        return engine.Point(x, y), zDist
    
    def rotate_point(self,camera,yaw,pitch,roll) -> Position3D:
        """translate a point relative to a turnning point(bijv. camera) deze functie is gebaseerd om een ratatie matrix """
        x = self.x - camera.x
        y = self.y - camera.y
        z = self.z - camera.z

        cos_y = m.cos(yaw)
        sin_y = m.sin(yaw)

        xz_x = x * cos_y - z * sin_y
        xz_z = x * sin_y + z * cos_y

        x, z = xz_x, xz_z

        cos_x = m.cos(pitch)
        sin_x = m.sin(pitch)

        yz_y = y * cos_x - z * sin_x
        yz_z = y * sin_x + z * cos_x

        y, final_z = yz_y, yz_z

        cos_z = m.cos(roll)
        sin_z = m.sin(roll)

        final_x = x * cos_z - y * sin_z
        final_y = x * sin_z + y * cos_z

        return Position3D(
            x=final_x+camera.x,
            y=final_y+camera.y,
            z=final_z+camera.z
        )

class Line3D:
    """this is a class to effieciently link to 3d point and use them as such"""
    def __init__(self, A: Position3D, B: Position3D, color=(255, 255, 255)):
        self.point_A = A
        self.point_B = B
        self.color = color
        self.vector = B - A
        self.x = [A.x, self.vector.x]
        self.y = [A.y, self.vector.y]
        self.z = [A.z, self.vector.z]
        self.cache = [self.point_A,self.point_B]

    def project_to_buffer(self, z_buffer, color_buffer, camera, fov, canvas):
        rotated_point_A = self.point_A.rotate_point(camera = camera,pitch = canvas.pitch,roll = canvas.roll,yaw = canvas.yaw)
        rotated_point_B = self.point_B.rotate_point(camera = camera,pitch = canvas.pitch,roll = canvas.roll,yaw = canvas.yaw)
        result_A = rotated_point_A.projector(fov, camera, canvas.screen_w, canvas.screen_h)
        result_B = rotated_point_B.projector(fov, camera, canvas.screen_w, canvas.screen_h)
        if result_A is None or result_B is None:
            return

        pA, zA = result_A
        pB, zB = result_B
        dx = pB.x - pA.x
        dy = pB.y - pA.y

        steps = max(int(abs(dx)), int(abs(dy)), 1) + 1
        t  = np.linspace(0, 1, steps, endpoint=False)
        sx = (pA.x + t * dx).astype(int)
        sy = (pA.y + t * dy).astype(int)
        sz = zA + t * (zB - zA)
 
        mask = (sx >= 0) & (sx < canvas.screen_w) & (sy >= 0) & (sy < canvas.screen_h)
        sx, sy, sz = sx[mask], sy[mask], sz[mask]

        idx = sy * canvas.screen_w + sx
        z_mask = sz < z_buffer[idx]
        idx, sz = idx[z_mask], sz[z_mask]

        z_buffer[idx] = sz
        color_buffer[idx] = self.color

class Canvas3D(tk.Canvas):
    """
    a canvas method partially build on the canvas2d methods to move the camera to display 3d objects
    """

    FOV_MIN  = 10.0
    FOV_MAX  = 160.0

    def __init__(self, width=800, height=600, fov=90.0, **kwargs):
        super().__init__(width=width, height=height, bg="black", **kwargs)

        self.screen_w = width
        self.screen_h = height
        self.fov = fov
        buffer_size = self.screen_w * self.screen_h
        self.z_buf = np.full(buffer_size, np.inf)
        self.c_buf = np.full((buffer_size, 3), 255, dtype=np.uint8)

        self.img = Image.frombuffer("RGB", (self.screen_w, self.screen_h), self.c_buf, "raw", "RGB", 0, 1)
        self.photo = ImageTk.PhotoImage(self.img)
        self.canvas_img = self.create_image(0, 0, anchor="nw", image=self.photo)

        self.frame_times = []
        self.fps_label = tk.Label(root, text="FPS: --", bg="black", fg="lime",font=("Courier", 10))
        self.fps_label.place(x=10, y=10)

        self.camera = Position3D(x=0, y=0, z=-150)
        
        self.roll,self.pitch,self.yaw = 0.0,0.0,0.0
        self.lines: list[Line3D] = []
        self.last_tick = t.perf_counter()

        self.eventlist = {}
        self.dragging    = False
        self.last_mouse  = (0, 0)

        self.bind("<ButtonPress-3>", self.on_click)
        self.bind("<ButtonRelease-3>", self.on_release)
        self.bind("<Motion>", self.on_drag)
        # self.bind("<MouseWheel>", self.on_scroll)
        self.bind("<KeyPress-a>", self.key_left)
        self.bind("<KeyPress-d>", self.key_right)
        self.bind("<KeyPress-w>", self.key_up)
        self.bind("<KeyPress-s>", self.key_down)
        self.bind("<KeyPress-q>", self.roll_left)
        self.bind("<KeyPress-e>", self.roll_right)
        self.bind("<Up>", self.move_z_positive)
        self.bind("<Down>", self.move_z_negative)

        self.engine = engine.Engine(physics_scaler=4, friction=0.999)
        self.objects = [ 
            GUI_Object(engine.Point(10, 10), engine.Point(100, 30), static=True, offset=OFFSET, scale=SCALE,root=self,color=(255,100,133)), 
            GUI_Object(engine.Point(10, 40), engine.Point(30, 60), offset=OFFSET, scale=SCALE,root=self,z1=305,z2=325,color=(200,0,255)), 
            GUI_Object(engine.Point(70, 40), engine.Point(90, 60), offset=OFFSET, scale=SCALE,root=self,z1=305,z2=325,color=(150,200,255)), 
            GUI_Object(engine.Point(110, 20), engine.Point(130, 80), static=True, offset=OFFSET, scale=SCALE,root=self,color=(0,255,0)),
            GUI_Object(engine.Point(0, 20), engine.Point(5, 100), static=True, offset=OFFSET, scale=SCALE,root=self,color=(0,0,255))
            ]
        
        self.objects[2].object.velocity = engine.Point(-40, 30)
        self.objects[1].object.velocity = engine.Point(60, 30)

        self.focus_set()

    def engine_update(self):
        now = t.perf_counter()
        dt = now - self.last_tick
        self.last_tick = now
        self.engine.tick(dt)

        for obj in self.objects:
            obj.update()
        self.after(12, self.engine_update)

    def add_line(self, line: Line3D):
        self.lines.append(line)

    def draw(self):
        """Clears the buffer and draws all objects"""
        self.z_buf.fill(np.inf) 
        self.c_buf.fill(255)
        
        for line in self.lines:
            line.project_to_buffer(self.z_buf, self.c_buf,self.camera, self.fov,canvas=self)
        self.recompute_coods = False

    def update_frame(self):
        start = t.perf_counter()

        self.draw()
        self.img = Image.frombuffer("RGB", (self.screen_w, self.screen_h), self.c_buf, "raw", "RGB", 0, 1)
        self.photo.paste(self.img)

        elapsed_time = (t.perf_counter() - start) * 1000

        self.frame_times.append(elapsed_time)
        if len(self.frame_times) > 30:
            self.frame_times.pop(0)
        avg = sum(self.frame_times) / len(self.frame_times)
        actual_fps = 1000 / avg if avg > 0 else 0
        #recommended = int(1000 / avg) if avg > 0 else TARGET_FPS
        self.fps_label.config(text=f"FPS: {actual_fps:.1f} / {TARGET_FPS} ")

        self.after(max(1, int(FRAME_MS - elapsed_time)), self.update_frame)
    
    def roll_left(self, event):
        """key:q"""
        self.roll -= CAM_ROT_SPEED

    def roll_right(self, event):
        """key:e"""
        self.roll += CAM_ROT_SPEED

    def key_left(self, event):
        """key:a"""
        self.yaw -= CAM_ROT_SPEED

    def key_right(self, event):
        """key:d"""
        self.yaw += CAM_ROT_SPEED

    def key_up(self, event):
        """key:w"""
        self.pitch += CAM_ROT_SPEED

    def key_down(self, event):
        """key:s"""
        self.pitch -= CAM_ROT_SPEED
    
    def move_z_positive(self, event):
        self.camera.z += 10

    def move_z_negative(self,event):
        self.camera.z -= 10

    def on_click(self, event):
        """"""
        self.dragging   = True
        self.last_mouse = (event.x, event.y)

    def on_release(self, event):
        self.dragging = False

    def on_drag(self, event):
        if not self.dragging:
            self.last_mouse = (event.x, event.y)
            return
        dx = event.x - self.last_mouse[0]
        dy = event.y - self.last_mouse[1]
        self.last_mouse = (event.x, event.y)

        # how many world units does one pixel correspond to at current fov?
        fHoek = m.radians(self.fov / 2)
        focal_len = self.screen_w / 2 / m.tan(fHoek)
        # use a representative depth for drag sensitivity
        ref_depth = 500.0
        scale = ref_depth / focal_len

        self.camera.x -= dx * scale
        self.camera.y -= dy * scale
        self.draw()

    def on_scroll(self, event):
        factor = 0.9 if event.delta > 0 else 1.1   # scroll up = zoom in = smaller fov
        self.fov = max(self.FOV_MIN, min(self.FOV_MAX, self.fov * factor))
        self.draw()

    def dual_point_to_3d_object(self, point1: Position3D, point2: Position3D, color:set):
        """this is a helper function to make a line3d from two points"""
        x1, y1, z1 = point1.x,point1.y,point1.z
        x2, y2, z2 = point2.x,point2.y,point2.z

        corners = [
            Position3D(x=x1, y=y1, z=z1),
            Position3D(x=x2, y=y1, z=z1),
            Position3D(x=x2, y=y2, z=z1),
            Position3D(x=x1, y=y2, z=z1),
            Position3D(x=x1, y=y1, z=z2),
            Position3D(x=x2, y=y1, z=z2),
            Position3D(x=x2, y=y2, z=z2),
            Position3D(x=x1, y=y2, z=z2),
        ]

        edge_indices = [
            (0, 1), (3, 2), (4, 5), (7, 6),  # along X
            (0, 3), (1, 2), (4, 7), (5, 6),  # along Y
            (0, 4), (1, 5), (2, 6), (3, 7),  # along Z
        ]
        for a, b in edge_indices:
            self.add_line(Line3D(corners[a], corners[b], color))
        return corners
        

class GUI_Object:
    def __init__(self, point1: engine.Point, point2: engine.Point, static: bool=False, offset: tuple[int, int]=(0, 0), scale: int=1,root=None,z1 = 200 , z2 = 400,color = (200,100,0) ):
        self.root = root
        self.object = engine.Object2D(point1, point2, static=static)
        self.root.engine.add(self.object)
        """self.points is a list where the first point is xmin,ymin and the second point isxmax,ymax"""
        self.points = self.object.points
        self.point1_z = z1
        self.point2_z = z2
        self.offset = offset
        self.scale = scale
        self.color = color
        self.position = offset
        self.corners = []
        self.initiate()
    
    def initiate(self):
        self.corners = self.root.dual_point_to_3d_object(
            Position3D(x=self.object.points[0].x * self.scale + self.offset[0],y=self.object.points[0].y * self.scale + self.offset[1],z=self.point1_z),
            Position3D(x=self.object.points[1].x * self.scale + self.offset[0],y=self.object.points[1].y * self.scale + self.offset[1],z=self.point2_z),
            color=self.color)
    
    def update(self):
        x = [self.points[0].x*-1,self.points[1].x*-1]
        y = [self.points[0].y*-1,self.points[1].y*-1]

        self.corners[0].y,self.corners[0].x = y[0],x[0]
        self.corners[1].y,self.corners[1].x = y[0],x[1]
        self.corners[2].y,self.corners[2].x = y[1],x[1]
        self.corners[3].y,self.corners[3].x = y[1],x[0]

        self.corners[4].y,self.corners[4].x = y[0], x[0]
        self.corners[5].y,self.corners[5].x = y[0],x[1]
        self.corners[6].y, self.corners[6].x = y[1],x[1]
        self.corners[7].y,self.corners[7].x = y[1],x[0]
    
def initiate_3d_canvas(fov=90,master="root",**kwargs):
    canvas = Canvas3D(fov=fov, master=master,**kwargs)
    canvas.pack()
    canvas.update_frame()
    canvas.engine_update()
    return canvas

if __name__ == "__main__":

    root = tk.Tk()
    root.title("3D cancas")

    canvas = Canvas3D(width=1920, height=1080, fov=90.0, master=root)
    canvas.pack()

    canvas.update_frame()
    canvas.engine_update()
    root.mainloop()
