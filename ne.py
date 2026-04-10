import tkinter as tk,math as m,random as r,re

class mainWindow():
    def __init__(self,size,):
        self.window = tk.Tk()
        self.window.geometry("400x400")
        self.window.title("2d physics")
        self.canvas = tk.Canvas(self.window, width=400, height=400)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", refreshPoints)

    def elements(self):
        pass

    def window

    def start(self):
        self.window.mainloop()

class frame():
    def __init__(self,position,root,size):
        self.frame = tk.Frame(root, width=size[0], height=size[1])