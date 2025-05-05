import json

with open("Route-7.json", "r") as jf:
    obj = json.load(jf)

route_7 = obj[0]

# print(route_7["movements"][1]["alternatives"][0]["platforms"])

bus_stops = route_7["movements"][1]["alternatives"][0]["platforms"]

with open("route_7_bus_stops.json", "w") as jfw:
    json.dump(bus_stops, jfw)

for bus_stop in bus_stops:
    print(bus_stop)