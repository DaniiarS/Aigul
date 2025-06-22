from app.db.database import SessionLocal
from app.db.models import BusStop, BusStopRoute, Route
from sqlalchemy.exc import SQLAlchemyError

from app.core.bus_stop import BusStopEntity
from app.core.point import Coord
from app.utils.eta import calc_distance

from tests.points_sum import ap_to_db


import json

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
        ROUTE_ID = db.query(Route).filter(Route.route_name==ROUTE).first().route_id
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

        with open("geojson_generated-7-bus_stops.geojson", "w") as wf:
            json.dump(geo_json, wf, indent=2)
    except Exception as e:
        print(f"{e}")

def filter_assistant_points(file_path: str, SEGMENT_ID: str, index: int = 0) -> list[dict]:
    result = []
    with open(file_path, "r") as rf:
        geo_json: dict = json.load(rf)
        objects: list[dict] = geo_json["features"]

        index = index
        for obj in objects:
            if obj["geometry"]["type"] == "Point" and (obj["properties"].get("marker-size") == None):
                obj["properties"]["assistant-point"] = True
                obj["properties"]["index"] = index
                obj["properties"]["segment_id"] = SEGMENT_ID
                index += 1
                result.append(obj)
    return result

def filter_line_strings(file_path: str, index: int = 0) -> list[dict]:
    result = []

    with open(file_path, "r") as rf:
        geo_json: dict = json.load(rf)
        objects: list[dict] = geo_json["features"]

        index = index
        for obj in objects:
            if obj["geometry"]["type"] ==  "LineString":
                lat1 = obj["geometry"]["coordinates"][0][1]
                lon1 = obj["geometry"]["coordinates"][0][0]

                lat2 = obj["geometry"]["coordinates"][1][1]
                lon2 = obj["geometry"]["coordinates"][1][0]

                line_string = {
                    "index": index,
                    "length": calc_distance(Coord(lat=lat1, lon=lon1), Coord(lat=lat2, lon=lon2))
                }
                result.append(line_string)
                index += 1
    return result

def set_l_sum(assistant_points: list[dict], filtered_line_strings: list[dict], l_sum: float = 0) -> list[dict]:
    l_sum = l_sum
    
    for point in assistant_points:
        for ls in filtered_line_strings:
            if point["properties"]["index"] == ls["index"]:
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
# SEGMENT_ID = 38
# assistant_points = filter_assistant_points(f"app/data/points/7/assistant_points/assistant-points-raw-7-{SEGMENT_ID}.geojson", SEGMENT_ID)
# # printl(assistant_points)

# filtered_line_strings = filter_line_strings(f"app/data/points/7/assistant_points/assistant-points-raw-7-{SEGMENT_ID}.geojson")
# # printl(filtered_line_strings)

# result = set_l_sum(assistant_points, filtered_line_strings)
# # printl(result)

# ap_to_db(result)
