import helper

# Extracts coordintaes of bus_stops into dict
parsed_response = helper.parse_response(f"{helper.ROUTE}/response.json") 

# # Saves extracted coordinates into json file
helper.write_json(f"{helper.ROUTE}/bus_stops_raw.json", parsed_response) 