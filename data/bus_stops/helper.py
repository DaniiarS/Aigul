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

def parse_response(file_path: str) -> dict:
    with open(file_path, "r") as rf:
        data = json.load(rf)
    
    result = data[0]["movements"][1]["alternatives"][0]["platforms"]
    return result

def write_json(file_path: str, obj: list):
    with open(file_path, "w") as wf:
        json.dump(obj, wf)

    return None

def write_csv(file_path:str, bus_stop_objs):
    with open(file_path, "w") as wf:
        writer = csv.writer(wf)
        for bus_stop in bus_stop_objs:
            writer.writerow(bus_stop.to_list())

    return None

def enumerate_address(addresses_file: str, enumerated_file: str):
    with open(addresses_file, "r") as rf:
        reader = csv.reader(rf)
        with open(enumerated_file, "w") as wf:
            writer = csv.writer(wf)
            for i, line in enumerate(reader):
                line.append(i)
                writer.writerow(line)
    
    return None

def plot_bus_stops(bus_stops: BusStop, ROUTE: str):
    BISHKEK_COORDS = [42.8746, 74.5698]
    m = folium.Map(location=BISHKEK_COORDS, zoom_start=13)
    
    # Add markers
    for bus_stop in bus_stops:
        folium.Marker(
            [bus_stop.lat, bus_stop.lng],
            popup=f"Bus Stop addr: {bus_stop.addr}, Bus Stop id: {bus_stop.id}",
            # tooltip="Click me"
        ).add_to(m)

    # Save to HTML file
    m.save(f"{ROUTE}/bus_stops_map_{ROUTE}.html")

    return None

def read_bus_stops(ROUTE: str) -> list[BusStop]:
    bus_stops_raw = read_json(f"{ROUTE}/bus_stops_raw.json")
    bus_stops = [BusStop(bus_stop["id"], bus_stop["geometry"], name=f"{ROUTE}", index=0) for bus_stop in bus_stops_raw]

    return bus_stops

#==================================================================
# EXECUTION: Refine, Save local, Plot, Process and Save
#==================================================================

ROUTE = "254"










#==================================================================
# Refine raw data
#==================================================================

# Extracts coordintaes of bus_stops into dict
# parsed_response = parse_response(f"{ROUTE}/response.json") 

# # Saves extracted coordinates into json file
# write_json(f"{ROUTE}/bus_stops_raw.json", parsed_response) 

# #==================================================================
# # Local Scope: Upload the data from files to variables
# #==================================================================

# # Reads parsed json coordinates into a dict object

# # #Creates a list of BusStop objects

# #==================================================================
# # Plot points on a map
# #==================================================================
# # Each marker displays: address and id(according to the Response)
# plot_bus_stops(bus_stops, ROUTE)

# Enumerates bus stops by writing indexes
# In the addresses.csv bus-stops are sorted in the order the buses visit them in the route
# So it is enough to give them indexes from 0 to n

# enumerate_address(f"{ROUTE}/addresses.csv", f"{ROUTE}/enumerated_addresses.csv")
# bus_stop_addresses = read_csv(f"{ROUTE}/enumerated_addresses.csv")

# # #=====================================================================================
# # # NOTE: Response from the External API returns the following 
# # # bus-stop data-object: (id, lat, lng)
# # # On the other hand, we also receive sorted Addresses of the bus_stops
# # # But we need (address, lat, lng), and to do that we have to do mapping id -> addr
# # # For now the only way to achieve it is to plot bus-stops on the map with
# # # their id-s and to mannualy assign id-s for each of the Address we obtained.
# # #=====================================================================================

# Adds adresses and indexes
# for bus_stop in bus_stops:
#     for addr in bus_stop_addresses:
#         if bus_stop.id == addr[1]:
#             bus_stop.addr = addr[0]
#             bus_stop.index = int(addr[-1])

# Sort bus_stops by indexes
# size = len(bus_stops)
# for i in range(size):
#     for j in range(1,size):
#         if bus_stops[j].index < bus_stops[j-1].index:
#             bus_stops[j], bus_stops[j-1] = bus_stops[j-1], bus_stops[j]

# Write and Save bus_stops
# write_csv(f"{ROUTE}/bus_stops.csv", bus_stops)