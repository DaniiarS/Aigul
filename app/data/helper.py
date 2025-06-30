from app.db.database import SessionLocal
from app.db.models import BusStop, BusStopRoute, Route, Point, Segment
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import exists

from app.core.bus_stop import BusStopEntity
from app.core.point import Coord
from app.utils.eta import calc_distance
import sys

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
    Example geo_json:
         "features": [
        {
            "type": "Feature",
            "properties": {
                "marker-color": "#0433ff",
                "marker-size": "medium",
                "marker-symbol": "circle-stroked"
            },
            "geometry": {
                "coordinates": [
                    "74.762537",
                    "42.881171"
                ],
                "type": "Point"
            },
            "id": 0
        }
                    ]
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


def ap_to_db(filtered_points: list[dict]):
    db = SessionLocal()

    try:
        for point in filtered_points:
            point_db = Point(lat=point["geometry"]["coordinates"][-1], lon=point["geometry"]["coordinates"][0], l_delta=point["properties"]["l"], l_sum=point["properties"]["l_sum"], index=point["properties"]["point_index"], segment_id=point["properties"]["segment_id"])
            db.add(point_db)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
    finally:
        db.close()


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
                # Read lat and lon of LineString's edges
                lat1 = obj["geometry"]["coordinates"][0][1]
                lon1 = obj["geometry"]["coordinates"][0][0]

                lat2 = obj["geometry"]["coordinates"][1][1]
                lon2 = obj["geometry"]["coordinates"][1][0]
                
                # Calculate the length of the LineString
                length = calc_distance(Coord(lat=lat1, lon=lon1), Coord(lat=lat2, lon=lon2))
                pref_length += length
                
                # Create a dict wiht LineStrings data
                line_string = {
                    "index": index,
                    "length": length,
                    "pref_length": round(pref_length, 2)
                }

                # Append it to the list where the all LineStrings are stored
                result["line_strings"].append(line_string)
                index += 1
        
        # Store separately the length of the whole Segment(which is the sum of LineStrings lengths)
        result["pref_length"] = pref_length
    return result

def set_l_sum(assistant_points: list[dict], filtered_line_strings: list[dict], l_sum: float = 0) -> list[dict]:
    l_sum = l_sum
    
    for point in assistant_points:
        for ls in filtered_line_strings["line_strings"]:
            if point["properties"]["point_index"] == ls["index"]:
                l_sum += ls["length"]
                
                point["properties"]["l"] = ls["length"]
                point["properties"]["l_sum"] = ls["pref_length"]
    
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

def create_segment(file: str, segment_index: int, bus_stops: list[list]) -> list[str]:
    # file: assistant_points-raw-{ROUTE}-{segment_index}.geojson
    line_strings = filter_line_strings(file) # {"pref_length": S, "line_strings": [{}, {}, {}, ..., {}] }

    # find two bus_stops that from segment(current_segment)
    bus_stop_a_lon, bus_stop_a_lat = bus_stops[segment_index][-3], bus_stops[segment_index][-2]
    bus_stop_b_lon, bus_stop_b_lat = bus_stops[segment_index + 1][-3], bus_stops[segment_index + 1][-2]

    db = SessionLocal()
    bus_stop_a = db.query(BusStop).filter((BusStop.lon==bus_stop_a_lon) & (BusStop.lat==bus_stop_a_lat)).first()
    bus_stop_b = db.query(BusStop).filter((BusStop.lon==bus_stop_b_lon) & (BusStop.lat==bus_stop_b_lat)).first()
    
    # if segment is already exists -> return
    if db.query(exists().where(Segment.bus_stop_a==bus_stop_a.id, Segment.bus_stop_b==bus_stop_b.id)).scalar():
        return None

    # else -> create a list with data to create a Segment entry
    bus_stop_a_name = bus_stops[segment_index][2]
    bus_stop_b_name = bus_stops[segment_index + 1][2]

    segment_length = line_strings["pref_length"]
    segment_street = bus_stop_a_name + " -- " + bus_stop_b_name

    # Segment entry ["234.8", "street - antoher_street", "10", "40"]
    result_segment = {
        "length": segment_length, 
        "street": segment_street, 
        "bus_stop_a": bus_stop_a.id, 
        "bus_stop_b": bus_stop_b.id
        }
    return result_segment, line_strings

def geojson_to_route(ROUTE: str):
    # Read bus_stops.csv
    bus_stops = []
    with open(f"app/data/bus_stops/{ROUTE}/bus_stops.csv", "r") as rf:
        reader = list(csv.reader(rf))
        bus_stops = reader

    N_SEGMENTS = len(bus_stops) - 1
    db = SessionLocal()

    # Make sure files exist: because for loop runs for each file with the i-th segment_index
    for segment_index in range(N_SEGMENTS):
        file = f"app/data/points/{ROUTE}/assistant_points/assistant-points-raw-{ROUTE}-{segment_index}.geojson"

        segment, line_strings = create_segment(file, segment_index,bus_stops) # returns None the segment(and its assistant-points) exist in the db
        # If segment exists continue
        if segment is None:
            continue

        # Else create a new segment and add assistant-points
        new_segment = Segment(length=segment["length"], street=segment["street"], bus_stop_a=segment["bus_stop_a"], bus_stop_b=segment["bus_stop_b"])

        # Add a new Segment to the db
        try:
            db.add(new_segment)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Could not add a new segment: {e}")
        finally:
            db.close()
        
        # Get the id of the new segment
        new_segment_id: int = db.query(Segment).filter((Segment.bus_stop_a==int(segment["bus_stop_a"])) & (Segment.bus_stop_b==int(segment["bus_stop_b"]))).first().id

        # Calculate "l" and "l_sum" for assistant-points using line_strings, and add it to db
        # {"pref_length": S, "line_strings": [{}, {}, {}, ..., {}] }
        assistant_points = filter_assistant_points(file, new_segment_id) # { ... } - assistant points
        set_l_sum(assistant_points,line_strings)
        ap_to_db(assistant_points)

#==============================================================================================================
# EXECUTION:
#==============================================================================================================

# STEPS:
# 1. Create bus_stop_route(use bus_stops.csv from the data folder)
# 2. Create segment(using bus_stop_route and line_strings to identify the length of the segment)
# 3. Create(add) assistant-points to the db
# 4. Create route_segment

ROUTE = sys.argv[1]
geojson_to_route(ROUTE)