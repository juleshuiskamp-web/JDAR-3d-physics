import math as m,tkinter as tk,random as r,re 
totPoints = 4
points = []
distances = []
pointsMatrix = []
class position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# def refreshPoints(event):
#     global points, distances, pointsMatrix, totPoints
#     print("refreshing points")
#     points.clear()
#     canvas.delete("all")
#     pointsMatrix.clear()
#     distances.clear()
#     for i in range(totPoints):
#         x = r.randint(0, 900)
#         y = r.randint(0, 900)
#         pos = position(x, y)
#         points.append(pos)
#         print(pos.x, pos.y)
#     # a = sorted(distances)[0]
#     # b = sorted(distances)[1]
#     # grootste = sorted(distances)[2]
#     # grootste = distances.index(grootste)
#     # grootste = points[grootste]
#     # c = distances.index(a)
#     # d = distances.index(b)
#     # e = points[c]
#     # f = points[d]
#     # pointMatrix = [point.x,point.y,e.x,e.y,grootste.x,grootste.y,f.x,f.y]
#     # print(pointMatrix)
#     # line = f"{pointMatrix[1]-((pointMatrix[0]-pointMatrix[4])/(pointMatrix[1]-pointMatrix[5])*pointMatrix[0])}+{((pointMatrix[0]-pointMatrix[4])/(pointMatrix[1]-pointMatrix[5])*pointMatrix[1])}*X"
#     # lineB = f"{pointMatrix[3]-((pointMatrix[2]-pointMatrix[6])/(pointMatrix[3]-pointMatrix[7])*pointMatrix[2])}+{((pointMatrix[2]-pointMatrix[6])/(pointMatrix[3]-pointMatrix[7])*pointMatrix[3])}*X"
#     pointMatrix = [[point.x,point.y] for point in points]
#     print(pointMatrix,"pointMatrix")
#     pointMatrix = [value for point in pointMatrix for value in point]
#     print(pointMatrix,"pointMatrix")
#     canvas.create_polygon(pointMatrix, fill="blue")

def readEntry(event):
    global totPoints
    print("reading entry")
    totPoints = invoerVeld.get()
    if totPoints.isdigit():
        totPoints = int(totPoints)
        if totPoints < 3 and totPoints > 1000:
            print("invalid input, using default value of 4")
            totPoints = 4
    else:
        print("invalid input, using default value of 4")
        totPoints = 4

def sort_points(points):
    # Bereken middelpunt
    cx = sum(p.x for p in points) / len(points)
    cy = sum(p.y for p in points) / len(points)

    # Sorteer op hoek rond middelpunt
    return sorted(points, key=lambda p: m.atan2(p.y - cy, p.x - cx))

def draw_polygon():
    canvas.delete("all")

    # Genereer random punten
    points = [position(r.randint(100, 1000000), r.randint(100, 1000000)) for _ in range(totPoints)]

    # Sorteer punten zodat geen kruisingen ontstaan
    sorted_points = sort_points(points)

    # Maak lijst voor tkinter
    pointMatrix = [coord for p in sorted_points for coord in (p.x, p.y)]

    # Teken polygon
    canvas.create_polygon(pointMatrix, fill="blue", outline="black")

    # Teken punten (optioneel)
    for p in sorted_points:
        canvas.create_oval(p.x-3, p.y-3, p.x+3, p.y+3, fill="red")

widow = tk.Tk()
canvas = tk.Canvas(widow, width=1000, height=1000)
canvas.pack()
topwin = tk.Toplevel(widow)
invoerVeld = tk.Entry(topwin)
invoerVeld.pack()
topwin.bind("<Return>", readEntry)
widow.bind("<Key-q>", lambda e: draw_polygon())
invoerVeld.focus()
widow.mainloop()