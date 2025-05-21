from app.db.database import SessionLocal
from app.db.models import BusStopRoute, Route, BusStop, Segment, RouteSegment, Point
import csv

from app.data.bus_stops.helper import BUS_STOP_ROUTE
from app.data.segments.helper import SEGMENT_ROUTE

# from utils.eta import point_objs

db = SessionLocal()

#================================================================================
# DEFINITIONS: add_routes(), add_bus_stops(), add_bus_stop_routes()
#================================================================================
def add_routes(file_path: str):
    with open(file_path, "r") as rf:
        routes = csv.reader(rf)
        for route in routes:
            route_name = route[0]
            route_type = route[-1]

            new_route_obj = Route(route_name=route_name, route_type=route_type)
            db.add(new_route_obj)
            db.commit()
            db.refresh(new_route_obj)
            db.close()

def add_bus_stops(file_path: str):
    with open(file_path, "r") as rf:
        bus_stops = csv.reader(rf)
        for bus_stop in bus_stops:
            bus_stop_name = bus_stop[1]
            bus_stop_addr = bus_stop[2]
            bus_stop_lng = bus_stop[3]
            bus_stop_lat = bus_stop[4]

            new_bus_stop_obj = BusStop(bus_stop_name=bus_stop_name, bus_stop_addr=bus_stop_addr, bus_stop_lng=bus_stop_lng, bus_stop_lat=bus_stop_lat)

            db.add(new_bus_stop_obj)
            db.commit()
            db.refresh(new_bus_stop_obj)
            db.close()

# Add check if the file extension is .csv
def add_bus_stop_routes(file_path: str, ROUTE: str):
    with open(file_path, "r") as rf:
        bus_stop_indexes = list(csv.reader(rf))
        bus_stop_objs = db.query(BusStop).filter(BusStop.bus_stop_name==f"{ROUTE}").all()

        # for bus_stop in bus_stop_objs:
        #     print(bus_stop)
        route_obj = db.query(Route).filter(Route.route_name==f"{ROUTE}").first()
        route_id = route_obj.route_id

        CONST = 100
        line = [0 for i in range(CONST)]

        for i, bus_stop in enumerate(bus_stop_objs):
            for row in bus_stop_indexes:
                if row[2] == bus_stop.bus_stop_addr: # row[2] - bus-stop's address
                    if line[int(row[-1])] == 1:      # row[-1] - bus-stop's index
                        continue

                    new_bus_stop_route_obj = BusStopRoute(bus_stop_id=bus_stop.bus_stop_id, route_id=route_id,bus_stop_index=int(row[-1]))
                    line[int(row[-1])] = 1

                    db.add(new_bus_stop_route_obj)
                    db.commit()
                    db.refresh(new_bus_stop_route_obj)
    
    db.close()

def read_bus_stops(bus_stop_name: str):
    bus_stops = db.query(BusStop).filter(BusStop.bus_stop_name==bus_stop_name).all()

    return bus_stops

def add_segment(file_path:str):
    with open(file_path, "r") as rf:
        reader = csv.reader(rf)
        for line in reader:
            segment = Segment(segment_length=line[-2], segment_street=line[1],segment_bus_stop_a=line[2],segment_bus_stop_b=line[3])
            db.add(segment)
            db.commit()
            db.refresh(segment)
    db.close()

def add_route_segment(file_path: str, SEGMENT_ROUTE: str) -> None:
    route = db.query(Route).filter(Route.route_name==SEGMENT_ROUTE).first()
    route_id = route.route_id
    segments = db.query(Segment).all()

    # for segment in segments:
    #     print(segment.segment_bus_stop_a, segment.segment_bus_stop_b)

    with open(file_path, "r") as rf:
        reader = list(csv.reader(rf))

        for segment in segments:
            for line in reader:
                if segment.segment_bus_stop_a == line[2] and segment.segment_bus_stop_b == line[3]:
                    route_segment = RouteSegment(route_id=route_id,segment_id = segment.segment_id, segment_index = line[-1])
                    db.add(route_segment)
                    db.commit()
                    db.refresh(route_segment)
    db.close()

    return None

def add_point(point_objs: list):
    for point_obj in point_objs:
        point = Point(route_name=point_obj.ROUTE, longitude=point_obj.lng, latitude=point_obj.lat, point_index=point_obj.point_index, segment_index=point_obj.segment_index)
        db.add(point)
        db.commit()
        db.refresh(point)
    db.close()

#================================================================================
# EXECUTION:
#================================================================================

# add_bus_stops(f"data/bus_stops/{BUS_STOP_ROUTE}/bus_stops.csv")
# add_bus_stop_routes(f"data/bus_stops/{BUS_STOP_ROUTE}/bus_stops.csv", ROUTE)

# add_segment(f"data/segments/{SEGMENT_ROUTE}/segments.csv")
# add_route_segment(f"data/segments/{SEGMENT_ROUTE}/segments.csv", f"{SEGMENT_ROUTE}")

# add_point(point_objs)