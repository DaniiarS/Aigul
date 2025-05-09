import helper

bus_stops = helper.read_bus_stops(helper.ROUTE)

# STEP 1: Enumerate addresses in the file
helper.enumerate_address(f"{helper.ROUTE}/addresses.csv", f"{helper.ROUTE}/enumerated_addresses.csv")
bus_stop_addresses = helper.read_csv(f"{helper.ROUTE}/enumerated_addresses.csv")

# STEP 2: Add indexes and address to the bus_stop objects
for bus_stop in bus_stops:
    for addr in bus_stop_addresses:
        if bus_stop.id == addr[1]:
            bus_stop.addr = addr[0]
            bus_stop.index = int(addr[-1])

# STEP 3: Sort bus_stops and indexes
size = len(bus_stops)
for i in range(size):
    for j in range(1,size):
        if bus_stops[j].index < bus_stops[j-1].index:
            bus_stops[j], bus_stops[j-1] = bus_stops[j-1], bus_stops[j]

# STEP 4: Write and save bus_stops
helper.write_csv(f"{helper.ROUTE}/bus_stops.csv", bus_stops)