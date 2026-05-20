import math as m
import tkinter as tk
from Position2D import Position2D


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
        Returns (Position2D, zDist) or None if behind camera.
        """
        fHoek = m.radians(fov / 2)
        focal_len = screen_w / 2 / m.tan(fHoek)
        zDist = self.z - camera.z
        if zDist <= 0:
            return None
        x = (self.x - camera.x) * focal_len / zDist + screen_w / 2
        y = (self.y - camera.y) * focal_len / zDist + screen_h / 2
        return Position2D(x, y), zDist

class Line3D:
    """this is a class to effieciently link to 3d point and use them as such"""
    def __init__(self, A: Position3D, B: Position3D, color=(255, 255, 255)):
        self.point_A = A
        self.point_B = B
        self.color   = color
        self.vector  = B - A
        self.x = [A.x, self.vector.x]
        self.y = [A.y, self.vector.y]
        self.z = [A.z, self.vector.z]

    def project_to_buffer(self, z_buffer, color_buffer,camera: Position3D, fov: float,screen_w: int, screen_h: int):
        fHoek = m.radians(fov / 2)
        focal_len = screen_w / 2 / m.tan(fHoek)

        result_A = self.point_A.projector(fov, camera, screen_w, screen_h)
        result_B = self.point_B.projector(fov, camera, screen_w, screen_h)
        if result_A is None or result_B is None:
            return

        pA, zA = result_A   # zA = actual z-distance of point A from camera
        pB, zB = result_B   # zB = actual z-distance of point B from camera

        dx = pB.x - pA.x
        dy = pB.y - pA.y
        steps = max(int(abs(dx)), int(abs(dy)), 1) + 1

        for i in range(steps):
            t  = i / steps
            sx = pA.x + t * dx
            sy = pA.y + t * dy
            px = int(sx)
            py = int(sy)

            if not (0 <= px < screen_w and 0 <= py < screen_h):
                continue

            z = zA + t * (zB - zA)
            buffer_index = py * screen_w + px
            if z < z_buffer[buffer_index]:
                z_buffer[buffer_index] = z
                color_buffer[buffer_index] = self.color

    def _compare(self, B: 'Line3D'):
        """Closest-approach intersection of two infinite 3D lines."""
        if not isinstance(B, Line3D):
            return "not Line3D"
        try:
            xS = equalize(B=self.x, A=B.x)
            yT = equalize(A=self.y, B=B.y)
            zS = equalize(B=self.z, A=B.z)

            denom = 1 - yT[1] * zS[1]
            if abs(denom) < 1e-10:
                return "parallel"

            T = (yT[0] + yT[1] * zS[0]) / denom
            S = zS[0] + T * zS[1]

            ix = self.x[0] + self.x[1] * T
            iy = self.y[0] + self.y[1] * T
            iz = self.z[0] + self.z[1] * T

            expected_x = xS[0] + T * xS[1]
            if abs(S - expected_x) < 1e-4:
                return [T, S, [ix, iy, iz]]
            return "skew"
        except ZeroDivisionError:
            return "div0"

def equalize(A, B):
    if A[1] == 0:
        raise ZeroDivisionError
    return [(B[0] - A[0]) / A[1], B[1] / A[1]]

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

        self.camera = Position3D(x=0, y=0, z=0)

        self.lines: list[Line3D] = []

        self.z_buf = [m.inf] * (width * height)
        self.c_buf = [(0, 0, 0)] * (width * height)

        self.img = tk.PhotoImage(width=width, height=height)
        self.create_image(0, 0, anchor=tk.NW, image=self.img)

        self.dragging    = False
        self.last_mouse  = (0, 0)

        self.bind("<ButtonPress-3>", self.on_click)
        self.bind("<ButtonRelease-3>", self.on_release)
        self.bind("<Motion>", self.on_drag)
        self.bind("<MouseWheel>", self.on_scroll)

    def add_line(self, line: Line3D):
        self.lines.append(line)

    def draw(self):
        """Clears the buffer and draws all objects"""
        buffer_size = self.screen_w * self.screen_h
        self.z_buf = [m.inf] * buffer_size
        self.c_buf = [(255, 255, 255)] * buffer_size

        for line in self.lines:
            line.project_to_buffer(self.z_buf, self.c_buf,self.camera, self.fov,self.screen_w, self.screen_h,)
        self.render()

    def render(self):
        """Write color_buffer to the PhotoImage row by row."""
        for y in range(self.screen_h):
            row = self.c_buf[y * self.screen_w: (y + 1) * self.screen_w]
            row_str = " ".join(f"#{r:02x}{g:02x}{b:02x}" for r, g, b in row)
            self.img.put("{" + row_str + "}", (0, y))

    def on_click(self, event):
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

def make_box(center,
             color_front=(255,  80,  80),   # red
             color_back =( 80, 150, 255),   # blue
             color_sides=(255, 220,  50)):  # yellow
    """
    Returns 12 Line3D edges of an axis-aligned box centred at (center, center, center).
    w = width (x),  h = height (y),  d = depth (z)
 
    Front face = nearer to camera (smaller z)
    Back  face = farther from camera (larger z)
 
         ftl ------- ftr        btl ------- btr
          |           |          |           |
          |  (front)  |          |  (back)   |
          |           |          |           |
         fbl ------- fbr        bbl ------- bbr
    """
    hw, hh, hd = 100,100,100
 
    # 8 corners
    ftl = Position3D(x=center[0]-hw, y=center[1]-hh, z=center[2]-hd)  # front top    left
    ftr = Position3D(x=center[0]+hw, y=center[1]-hh, z=center[2]-hd)  # front top    right
    fbl = Position3D(x=center[0]-hw, y=center[1]+hh, z=center[2]-hd)  # front bottom left
    fbr = Position3D(x=center[0]+hw, y=center[1]+hh, z=center[2]-hd)  # front bottom right
    btl = Position3D(x=center[0]-hw, y=center[1]-hh, z=center[2]+hd)  # back  top    left
    btr = Position3D(x=center[0]+hw, y=center[1]-hh, z=center[2]+hd)  # back  top    right
    bbl = Position3D(x=center[0]-hw, y=center[1]+hh, z=center[2]+hd)  # back  bottom left
    bbr = Position3D(x=center[0]+hw, y=center[1]+hh, z=center[2]+hd)  # back  bottom right
 
    return [
        Line3D(ftl, ftr, color_front),
        Line3D(fbl, fbr, color_front),
        Line3D(ftl, fbl, color_front),
        Line3D(ftr, fbr, color_front),
        Line3D(btl, btr, color_back),
        Line3D(bbl, bbr, color_back),
        Line3D(btl, bbl, color_back),
        Line3D(btr, bbr, color_back),
        Line3D(ftl, btl, color_sides),
        Line3D(ftr, btr, color_sides),
        Line3D(fbl, bbl, color_sides),
        Line3D(fbr, bbr, color_sides),
    ]

if __name__ == "__main__":

    root = tk.Tk()
    root.title("3D cancas")

    canvas = Canvas3D(width=1920, height=1080, fov=90.0, master=root)
    canvas.pack()
    """
    A(-150,-100, 400) ─── B( 150,-100, 400)   red    top edge    (z=400)
    B( 150,-100, 400) ─── C( 150, 100, 600)   green  right edge  (depth change)
    C( 150, 100, 600) ─── D(-150, 100, 600)   blue   bottom edge (z=600)
    D(-150, 100, 600) ─── A(-150,-100, 400)   yellow left edge   (depth change)
    """
    canvas.add_line(Line3D(Position3D(x=-100, y=-100, z=400), Position3D(x= 100, y=-100, z=400), color=(255,  80,  80)))
    canvas.add_line(Line3D(Position3D(x= 100, y=-100, z=400), Position3D(x= 100, y= 100, z=400), color=(255,  80,  80)))
    canvas.add_line(Line3D(Position3D(x= 100, y= 100, z=400), Position3D(x=-100, y= 100, z=400), color=(255,  80,  80)))
    canvas.add_line(Line3D(Position3D(x=-100, y= 100, z=400), Position3D(x=-100, y=-100, z=400), color=(255,  80,  80)))

    canvas.add_line(Line3D(Position3D(x=-100, y=-100, z=600), Position3D(x= 100, y=-100, z=600), color=( 80, 150, 255)))
    canvas.add_line(Line3D(Position3D(x= 100, y=-100, z=600), Position3D(x= 100, y= 100, z=600), color=( 80, 150, 255)))
    canvas.add_line(Line3D(Position3D(x= 100, y= 100, z=600), Position3D(x=-100, y= 100, z=600), color=( 80, 150, 255)))
    canvas.add_line(Line3D(Position3D(x=-100, y= 100, z=600), Position3D(x=-100, y=-100, z=600), color=( 80, 150, 255)))

    canvas.add_line(Line3D(Position3D(x=-100, y=-100, z=400), Position3D(x=-100, y=-100, z=600), color=(255, 220,  50)))
    canvas.add_line(Line3D(Position3D(x= 100, y=-100, z=400), Position3D(x= 100, y=-100, z=600), color=(255, 220,  50)))
    canvas.add_line(Line3D(Position3D(x= 100, y= 100, z=400), Position3D(x= 100, y= 100, z=600), color=(255, 220,  50)))
    canvas.add_line(Line3D(Position3D(x=-100, y= 100, z=400), Position3D(x=-100, y= 100, z=600), color=(255, 220,  50)))
    """
    for edge in make_box(center=[500,200,300]):
        canvas.add_line(edge)
    """
    canvas.draw()
    root.mainloop()
