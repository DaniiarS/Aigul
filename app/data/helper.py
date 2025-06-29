from app.db.database import SessionLocal
from app.db.models import BusStop, BusStopRoute, Route
from sqlalchemy.exc import SQLAlchemyError

from app.core.bus_stop import BusStopEntity
from app.core.point import Coord
from app.utils.eta import calc_distance

from tests.points_sum import ap_to_db


import json
import csv

def get_bus_stops_db(ROUTE: str) -> list[BusStopEntity]:
    db = SessionLocal()
    result = []
    
    try:
        route_id: int = db.query(Route).filter(Route.route_name==ROUTE).first().route_id
        bus_stops = db.query(BusStop).filter(BusStop.bus_stop_name==ROUTE).all()
        for bus_stop in bus_stops:
            bus_stop_id: int = bus_stop.bus_stop_id
            bus_stop_index = db.query(BusStopRoute).filter((BusStopRoute.route_id==route_id) & (BusStopRoute.bus_stop_id==bus_stop_id)).first().bus_stop_index

            result.append(BusStopEntity.model_to_obj(bus_stop,bus_stop_index))
    except SQLAlchemyError as e:
        print(f"{e}")
    finally:
        db.close()
    
    return result

def generate_bus_stops_geojson(ROUTE: str):
    db = SessionLocal()
    try:
        ROUTE_ID = db.query(Route).filter(Route.name==ROUTE).first().id 
        bus_stop_route = db.query(BusStopRoute).filter(BusStopRoute.route_id==ROUTE_ID).all()
        bus_stop_route.sort(key=lambda item: item.bus_stop_index)

        res = [db.query(BusStop).filter(BusStop.id==bsr.bus_stop_id).first() for bsr in bus_stop_route]

        geo_json = {
            "type": "FeatureCollection",
            "features": []
        }

        for id, bus_stop in enumerate(res):
            feature = {
                    "type": "Feature",
            "properties": {
                "marker-color": "#0433ff",
                "marker-size": "medium",
                "marker-symbol": "circle-stroked"
            },
            "geometry": {
                "coordinates": [
                bus_stop.lon,
                bus_stop.lat
                ],
                "type": "Point"
            },
            "id": id
            }
            geo_json["features"].append(feature)

        with open(f"app/data/bus_stops/{ROUTE}/bus_stops-{ROUTE}.geojson", "w") as wf:
            json.dump(geo_json, wf, indent=2)
    except Exception as e:
        print(f"{e}")


""" To obtain assistant-points for the given route we use geojson.io.
    First, BusStop markers are added to the map with blue color.
    Second, using those BusStop markers to follow the route, assistant-points are added between two BusStop markers.
    Finally, the goal is to extract the assistant-points leaving BusStop points. The following code implements this functionality.
"""
def filter_assistant_points(file_path: str, SEGMENT_ID: str, index: int = 0) -> list[dict]:
    result = []
    with open(file_path, "r") as rf:
        geo_json: dict = json.load(rf)
        objects: list[dict] = geo_json["features"]

        index = index
        for obj in objects:
            if obj["geometry"]["type"] == "Point" and (obj["properties"].get("marker-size") == None):
                obj["properties"]["assistant-point"] = True
                obj["properties"]["point_index"] = index
                obj["properties"]["segment_id"] = SEGMENT_ID
                index += 1
                result.append(obj)
    return result

""" We need information about assistant-points and about the segment in which assistant-points are located.
    We have to know the following information: segment's length, assistant-points distance on the route starting from the BusStop, and distance between two assistant points(current, and point on the left).
    The following code calculates the required distances and sets indexes to the assistant points within a segment.
"""
def filter_line_strings(file_path: str, index: int = 0) -> list[dict]:
    result = dict()
    result["line_strings"] = []

    with open(file_path, "r") as rf:
        geo_json: dict = json.load(rf)
        objects: list[dict] = geo_json["features"]

        index = index
        pref_length = 0
        for obj in objects:
            if obj["geometry"]["type"] ==  "LineString":
                lat1 = obj["geometry"]["coordinates"][0][1]
                lon1 = obj["geometry"]["coordinates"][0][0]

                lat2 = obj["geometry"]["coordinates"][1][1]
                lon2 = obj["geometry"]["coordinates"][1][0]
                
                length = calc_distance(Coord(lat=lat1, lon=lon1), Coord(lat=lat2, lon=lon2))
                pref_length += length

                line_string = {
                    "index": index,
                    "length": length,
                    "pref_length": round(pref_length, 2)
                }
                result["line_strings"].append(line_string)
                index += 1
        result["pref_length"] = pref_length
    return result

def set_l_sum(assistant_points: list[dict], filtered_line_strings: list[dict], l_sum: float = 0) -> list[dict]:
    l_sum = l_sum
    
    for point in assistant_points:
        for ls in filtered_line_strings["line_strings"]:
            if point["properties"]["point_index"] == ls["index"]:
                l_sum += ls["length"]
                
                point["properties"]["l"] = ls["length"]
                point["properties"]["l_sum"] = round(l_sum,2)
    
    return assistant_points

def set_index_assist_points(geojson_objects: list) -> list:
    index = 0
    for point in geojson_objects:
        if point["properties"].get("flag") != None:
            index = 0
        point["properties"]["index"] = index
        index += 1
    
    return geojson_objects

def printl(array: list) -> None:
    for item in array:
        print(item)

# # the last long segment is left -> segment id is 38
ROUTE = "14T"
# SEGMENT_INDEX = 0

# bus_stops = []
# with open(f"app/data/bus_stops/{ROUTE}/bus_stops.csv", "r") as rf:
#     reader = list(csv.reader(rf))
#     bus_stops = reader
# print(bus_stops)


# Calculate pref sum for each of the Segments, identify ids of the edge buses(a and b) and create a list with Segment data to insert to db.
# result = []
# db = SessionLocal()
# for SEGMENT_INDEX in range(27):
#     try:
#         if SEGMENT_INDEX == 15 or SEGMENT_INDEX == 16:
#             continue
#         bus_stop_a: BusStop = db.query(BusStop).filter((BusStop.lon==bus_stops[SEGMENT_INDEX][-3]) & (BusStop.lat==bus_stops[SEGMENT_INDEX][-2])).first()
#         bus_stop_b: BusStop = db.query(BusStop).filter((BusStop.lon==bus_stops[SEGMENT_INDEX+1][-3]) & (BusStop.lat==bus_stops[SEGMENT_INDEX+1][-2])).first()
#         # assistant_points = filter_assistant_points(f"app/data/points/{ROUTE}/assistant_points/assistant-points-raw-{ROUTE}-{SEGMENT_INDEX}.geojson", SEGMENT_INDEX)
#         # printl(assistant_points)

#         filtered_line_strings = filter_line_strings(f"app/data/points/{ROUTE}/assistant_points/assistant-points-raw-{ROUTE}-{SEGMENT_INDEX}.geojson")
#         # print(filtered_line_strings["pref_length"])

#         result.append([round(filtered_line_strings["pref_length"],2), f"{bus_stop_a.name} - {bus_stop_b.name}", bus_stop_a.id, bus_stop_b.id])
#     except Exception as e:
#         print(f"Unexpected errpr: {e}")

count = 0
for i in range(27):
    if i == 15 or i == 16:
        continue
    fl = filter_line_strings(f"app/data/points/{ROUTE}/assistant_points/assistant-points-raw-{ROUTE}-{i}.geojson")
    ap = filter_assistant_points(f"app/data/points/{ROUTE}/assistant_points/assistant-points-raw-{ROUTE}-{i}.geojson", 42 + count)
    res = set_l_sum(ap, fl)
    count += 1
    ap_to_db(res)

# Create csv file with Segment data for ROUTE's route
# with open(f"app/data/segments/{ROUTE}/segments.csv", "w") as wf:
#     writer = csv.writer(wf)x
#     writer.writerows(result)

# result = set_l_sum(assistant_points, filtered_line_strings)
# # printl(result)

# ap_to_db(result)

# ROUTE = "14T"
# generate_bus_stops_geojson(ROUTE)