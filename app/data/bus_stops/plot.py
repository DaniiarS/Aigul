import app.core.bus_stop as bus_stop

bus_stops = bus_stop.read_bus_stops(bus_stop.ROUTE)
bus_stop.plot_bus_stops(bus_stops,bus_stop.ROUTE)