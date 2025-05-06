import json
import csv

class BusStop:
    def __init__(self, id: str, point: str, name: str = None, addr: str = None):
        self.id = str(id)
        self.lat = self.get_coord(point)["lat"]
        self.lng = self.get_coord(point)["lon"]
        self.name = name
        self.addr = addr
    
    def get_coord(self, point: str):
        coordinates = ""
        flag = False
        for ch in point:
            if ch == "(":
                flag = True
                continue
            elif ch == ")":
                flag = False
                break
            
            if flag:
                coordinates += ch
            
        coord_split = coordinates.split()
        return {"lon": coord_split[0], "lat": coord_split[1]}
    
    def to_list(self):
        return [self.id, self.name, self.addr, self.lng, self.lat]
    
    def __repr__(self):
        return f"id: {self.id}, name: {self.name}, address: {self.addr} lat: {self.lat}, lng: {self.lng}"


def read_json(file_path:str):
    with open(file_path, "r") as rf:
        data = json.load(rf)
    
    return data

def read_csv(file_path: str):
    with open(file_path, "r") as rf:
        data = list(csv.reader(rf))
    
    return data



bus_stops = read_json("bus_stops_raw.json")
bus_stop_addresses = read_csv("mapping.csv")

bus_stop_objs = [BusStop(bus_stop["id"], bus_stop["geometry"], name = "7") for bus_stop in bus_stops]

for bus_stop in bus_stop_objs:
    for addr in bus_stop_addresses:
        if bus_stop.id == addr[-1]:
            bus_stop.addr = addr[0]
            # print(bus_stop.addr, addr[0])

for bus_stop in bus_stop_objs:
    print(bus_stop.to_list())

# with open("bus_stops.csv", "a") as wf:
#     writer = csv.writer(wf)
#     for bus_stop in bus_stop_objs:
#         writer.writerow(bus_stop.to_list())