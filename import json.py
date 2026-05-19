import json
#Import de Json bestand 
with open("object_data.json", "r") as file:
    data = json.load(file)


obj = data["object"]

name = obj["naam"]
x = obj["position"]["x"]
y = obj["position"]["y"]
z = obj["position"]["z"]
#Checkt of de coordinaten een int of float zijn, als dat zo is print het de packet, anders geeft het een error
if (
    isinstance(x,(int,float)) and
    isinstance(y,(int,float)) and
    isinstance(z,(int,float))
):
    print ("Coordianten zijn goed")
    packet = {
    "naam": obj["naam"],
    "x": x,
    "y": y,
    "z": z
    }
    print(packet)

else: print ("Error coordianten zijn niet goed")
