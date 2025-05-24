import app.core.bus_stop as bus_stop

# Extracts coordintaes of bus_stops into dict
parsed_response = bus_stop.parse_response(f"{bus_stop.ROUTE}/response.json") 

# # Saves extracted coordinates into json file
bus_stop.write_json(f"{bus_stop.ROUTE}/bus_stops_raw.json", parsed_response) 