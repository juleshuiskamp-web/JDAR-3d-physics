import tkinter as tk
import random

root = tk.Tk()
root.title("Random Polygon")

canvas = tk.Canvas(root, width=500, height=400, bg="white")
canvas.pack()

def random_polygon():
    canvas.delete("all")

    num_points = random.randint(3, 6)  # number of corners
    points = []

    for _ in range(num_points):
        x = random.randint(50, 450)
        y = random.randint(50, 350)
        points.extend([x, y])

    canvas.create_polygon(
        points,
        fill=random.choice(["red", "green", "blue", "yellow", "purple"]),
        outline="black"
    )

for point in points:
    points.remove(point)
    for sPoint in points:
        lenght = sqrt((point[0]-sPoint[0])**2 + (point[1]-sPoint[1])**2)
        listX.append((length, point))
        listX = sorted(listX, key=lambda i: i[0])[:2]

# Button to generate new polygon
btn = tk.Button(root, text="Generate Polygon", command=random_polygon)
btn.pack()

# Generate one at start
random_polygon()

root.mainloop()