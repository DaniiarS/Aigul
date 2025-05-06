import json
import csv
import folium

#====================================================================================
# DEFINITION: BusStop: cls, read_json(), read_csv, read_bus_stops_raw, write_json
#====================================================================================

class BusStop:
    def __init__(self, id: str, point: str, name: str = None, addr: str = None, index: int = 0):
        self.id = str(id)
        self.lat = self.get_coord(point)["lat"]
        self.lng = self.get_coord(point)["lon"]
        self.name = name
        self.addr = addr
        self.index = 0
    
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
        return [self.id, self.name, self.addr, self.lng, self.lat, self.index]
    
    def __repr__(self):
        return f"id: {self.id}, name: {self.name}, address: {self.addr} lat: {self.lat}, lng: {self.lng}, index: {self.index}"


def read_json(file_path:str):
    with open(file_path, "r") as rf:
        data = json.load(rf)
    
    return data

def read_csv(file_path: str):
    with open(file_path, "r") as rf:
        data = list(csv.reader(rf))
    
    return data

def read_bus_stops_raw(file_path: str):
    with open(file_path, "r") as rf:
        data = json.load(rf)
    
    result = data[0]["movements"][1]["alternatives"][0]["platforms"]
    return result

def write_json(file_path: str, obj: list):
    with open(file_path, "a") as wf:
        json.dump(obj, wf)

    return None

def write_csv(file_path:str, bus_stop_objs):
    with open(file_path, "a") as wf:
        writer = csv.writer(wf)
        for bus_stop in bus_stops:
            writer.writerow(bus_stop.to_list())

    return None
#==================================================================
# EXECUTION
#==================================================================


#=================
# Refine raw data
#=================
# bus_stops_raw = read_bus_stops_raw("8/response.json")
# write_json("8/bus_stops_raw.json", bus_stops_raw)



bus_stops_raw = read_json("7/bus_stops_raw.json")

#Create a list of BusStop objects
bus_stops = [BusStop(bus_stop["id"], bus_stop["geometry"], name="7", index=i) for i, bus_stop in enumerate(bus_stops_raw)]
bus_stop_addresses = read_csv("7/mapping.csv")

# Add adresses and indexes
for bus_stop in bus_stops:
    for addr in bus_stop_addresses:
        if bus_stop.id == addr[1]:
            bus_stop.addr = addr[0]
            bus_stop.index = int(addr[2])

# Sort bus_stops by indexes
size = len(bus_stops)
for i in range(size):
    for j in range(1,size):
        if bus_stops[j].index < bus_stops[j-1].index:
            bus_stops[j], bus_stops[j-1] = bus_stops[j-1], bus_stops[j]

# Write and Save bus_stops
write_csv("7/bus_stops.csv", bus_stops)




#================================
# Plot points on a map
#================================

# m = folium.Map(location=[42.8746, 74.5698], zoom_start=13)
# # Add markers
# for i, stop in enumerate(bus_stops):
#     folium.Marker(
#         [stop.lat, stop.lng],
#         popup=f"Bus Stop name: {stop.addr}, Bus Stop id: {stop.id}",
#         # tooltip="Click me"
#     ).add_to(m)

# # Save to HTML file
# m.save("bus_stops_map.html")
