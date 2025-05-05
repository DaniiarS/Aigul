import overpy
import folium

api = overpy.Overpass()

# Bounding box around Bishkek (South, West, North, East)
query = """
node["highway"="bus_stop"](42.790,74.460,42.950,74.710);
out body;
"""

result = api.query(query)

print(f"Found {len(result.nodes)} bus stops.\n")
# with open("bus_stops.txt", "w") as file:
#     for node in result.nodes:
#         data = f''' Name: {node.tags.get('name', 'Unknown')}\n
#                     Lat: {node.lat}, Lon: {node.lon}\n
#                     -----------------------------------
#                 '''
#             Bishkek city ID 2GIS:       15763221466054725

# {"meta":{"api_version":"3.0.18799","code":200,"issue_date":"20250425"},
#  "result":{"items":[{"full_name":"Бишкек, Кыргызская национальная филармония им. Токтогула Сатылганова",
#                      "id":"15763384674812303","name":"Кыргызская национальная филармония им. Токтогула Сатылганова",
#                      "route_type":"bus","subtype":"stop","type":"station"}],
#            "total":1
#           }
# }
#         file.write(data)

m = folium.Map(location=[42.8746, 74.5698], zoom_start=13)

for node in result.nodes:
    name = node.tags.get("name", "Unknown")
    if name == "Unknown":
            folium.Marker(
                                [node.lat, node.lon],
                                popup=f"Bus Stop  - {name}<br>Click to rename",
                                tooltip="Click me"
                            ).add_to(m)

m.save("bus_stops_map.html")
