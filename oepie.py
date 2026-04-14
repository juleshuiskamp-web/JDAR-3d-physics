import math as m
while True:
    zoom = float(input("zoom"))
    screenWidth = int(input("screenwidth"))
    power = round(m.log((screenWidth*zoom),10))
    relScreenWidth = (screenWidth*zoom) /(10**power) 
    print(f"power{power},scientific{relScreenWidth}")
    print(f"screenwidth{screenWidth*zoom}")