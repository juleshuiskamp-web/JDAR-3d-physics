import tkinter as tk, math
window = tk.Tk()
canvas = tk.Canvas(master=window,bg='lightblue')
canvas.pack(expand=True,fill='both')
width= window.winfo_screenwidth() 
height= window.winfo_screenheight()
window.geometry("%dx%d" % (width, height))
# zoom = [1]
# center = [0,0]
# adaptation =width * sqrt(zoom)
# x = center.x + delta(x)/sqrt(zoom)
# y = center.y + delta(y)/sqrt(zoom)


dragging = [False]
mousePosition = [[0,0],[0,0]]

def scrolling(event):
    # if event.delta > 0:
    #     # window.zoom = window.zoom / (1 + event.delta/10)
    # elif event.delta < 0: pass# window.zoom = window.zoom / (1 - event.delta/10)
    print(event.delta)

def rightPress(event):
    dragging[0] = True

def rightRelease(event):
    dragging[0] = False

def draggin(event):
    if dragging[0]:
        print(event.x,event.y)
        mousePosition[0][0] = mousePosition[0][1]
        mousePosition[0][1] = mousePosition[1][1]
        mousePosition[1][0] = event.x
        mousePosition[1][1] = event.y
        delta =[mousePosition[0]-mousePosition[1]]
        print(f'delta is {delta}')
        print(f"{mousePosition[1],mousePosition[1]}")
window.bind("<MouseWheel>", scrolling)
window.bind("<Motion>", draggin)
window.bind("<ButtonPress-3>", rightPress)
window.bind("<ButtonRelease-3>", rightRelease)
window.mainloop()