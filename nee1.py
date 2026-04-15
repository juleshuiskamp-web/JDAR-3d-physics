def cross(o, a, b):
    return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)

def convex_hull(points):
    points = sorted(points, key=lambda p: (p.x, p.y))
    
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]

    sorted_points = convex_hull(points)

pointMatrix = [coord for p in sorted_points for coord in (p.x, p.y)]

canvas.create_polygon(pointMatrix, fill="blue", outline="black")

def polygonize(points):
    points = points[:]
    
    # start met eerste 3 punten
    polygon = points[:3]
    remaining = points[3:]

    while remaining:
        p = remaining.pop(0)

        best_index = 0
        best_increase = float("inf")

        for i in range(len(polygon)):
            a = polygon[i]
            b = polygon[(i + 1) % len(polygon)]

            increase = distance(a, p) + distance(p, b) - distance(a, b)

            if increase < best_increase:
                best_increase = increase
                best_index = i + 1

        polygon.insert(best_index, p)

    return polygon

def sort_points(points):
    # Bereken middelpunt
    cx = sum(p.x for p in points) / len(points)
    cy = sum(p.y for p in points) / len(points)

    # Sorteer op hoek rond middelpunt
    return sorted(points, key=lambda p: m.atan2(p.y - cy, p.x - cx))