import folium
import json
import csv
from objects import BusStop

def sort(data: list) -> list:
    size = len(data)

    for i in range(size):
        for j in range(1,size):
            if int(data[j][-1]) < int(data[j -1][-1]):
                data[j], data[j-1] = data[j-1], data[j]
    
    return data

# Example list of bus stops with unknown names
with open("route_7_bus_stops.json", "r") as rf:
    bus_stops_data = json.load(rf)

with open("bus_7_names.csv", "r") as rf:
    data = list(csv.reader(rf))
    with open("write_bus_stop_route.csv", "w") as wf:
        writer = csv.writer(wf)

        for i, row in enumerate(data):
            writer.writerow([row[-1], 1, i])
    bus_stop_names = sort(data)


# print(bus_stop_names)

bus_stops = []
for i, bus_stop in enumerate(bus_stops_data):
    bus_stops.append(BusStop(bus_stop["id"], bus_stop["geometry"], bus_stop_names[i][0]))


# print(bus_stops) 
# print(len(bus_stops))
# print(len(bus_stop_names))

# for bus_stop in bus_stops:
#     print(bus_stop)


# bus = BusStop(bus_stops[0]["geometry"], bus_stops[0]["id"])
# bus_stops = [
#     {"lat": 42.8746, "lon": 74.5698},  # Bishkek center
#     {"lat": 42.8700, "lon": 74.5900},
# ]
# unknown_bus_stops = []

# Create a map centered around Bishkek
m = folium.Map(location=[42.8746, 74.5698], zoom_start=13)



# Add markers
for i, stop in enumerate(bus_stops):
    folium.Marker(
        [stop.lat, stop.lon],
        popup=f"Bus Stop name: {stop.name}, Bus Stop id: {stop.id}",
        # tooltip="Click me"
    ).add_to(m)

# Save to HTML file
m.save("bus_stops_map.html")
