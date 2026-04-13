import tkinter as tk,math as m,random as r,re

class mainWindow():
    def __init__(self,):
        self.zoom = 1
        self.center = [0,0]
        self.lastMousePos = [0,0]
        self.dragging = False
        self.window = tk.Tk()
        self.window.geometry(f"{self.window.winfo_screenwidth()}x{self.window.winfo_screenheight()}")
        self.window.title("2d physics")
        self.options = tk.Frame(self.window, height=int(self.window.winfo_screenheight()/8),bg="blue")
        self.options.pack(side="top", fill="x")
        self.canvas = tk.Canvas(self.window,bg="green",bd="0",highlightthickness=0)
        self.canvas.pack(side="left", fill="both",expand=True)
        self.toggleEditor = tk.Frame(self.window, width=0,bg="red")
        self.toggleEditor.pack_propagate(False)
        self.toggleEditor.pack(side="left",fill="y")
        self.button = []
        self.window.bind("<Motion>",self.draggin)
        self.window.bind("<ButtonPress-3>",self.rightClick)
        self.window.bind("<ButtonRelease-3>",self.rightRelease)
        self.window.bind("<MouseWheel>",self.zooming)

    def draw(self,):
        self.canvas.delete("all")
        step = 100 * self.zoom

        for i in range(10):
            for j in range(10):
                x = i * step - self.center[0]
                y = j * step - self.center[1]
                size = 5 * self.zoom
                self.canvas.create_oval(x-size, y-size, x+size, y+size, fill="white")

    def draggin(self,event):
        if not self.dragging:
            return
        dx = event.x - self.lastMousePos[0]
        dy = event.y - self.lastMousePos[1]
        self.center[0] -= dx * self.zoom
        self.center[1] -= dy * self.zoom
        self.lastMousePos = [event.x, event.y]
        self.draw()
    
    def rightClick(self,event):
        self.dragging = True
        self.lastMousePos = [event.x, event.y]
    
    def rightRelease(self,event):
        self.dragging = False
    
    def zooming(self,event):
        factor = 1.1 if event.delta > 0 else 0.9
        self.zoom *= factor
        self.draw()

    def elements(self):
        pass

    def window(self,):
        pass

    def start(self):
        self.window.mainloop()

    def buttons(self):
        self.button = [tk.Button(self.options, text="refresh points", command=self.edito, width=5) for i in range(8)]
        for i,button in enumerate(self.button):
            button.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            self.options.grid_columnconfigure(i, weight=1)

    def edito(self):
        if not self.toggleEditor.winfo_ismapped():
            self.toggleEditor.pack(side="right", fill="y")
            current = 0
            crop = False
        else: 
           current = self.toggleEditor.winfo_width()
           crop = current >= int(self.window.winfo_screenwidth() / 6)
        
        step = [0]
        stepsSize = max(1, self.window.winfo_screenwidth() // 360)
        maxWidhetSize = int(self.window.winfo_screenwidth() / 3)
        target = 0 if crop else maxWidhetSize
        total_steps = max(1, abs(target - current) // stepsSize)


        def expand():
            if step[0] < total_steps:
                step[0] += 1
                direction = -1 if crop else 1
                new_width = current + (step[0] * stepsSize * direction)
                new_width = max(0, min(maxWidhetSize, new_width))
                self.toggleEditor.config(width=new_width)
                self.window.after(8, expand)
            else:
                self.toggleEditor.config(width=target)
                if crop:
                    self.toggleEditor.pack_forget()

        expand()

if __name__ == "__main__":
    root = mainWindow()
    root.buttons()
    root.start()