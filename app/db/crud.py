from app.db.database import get_db, SessionLocal
from app.db.models import BusStopRoute, Route, BusStop, Segment, RouteSegment, Point
from sqlalchemy.exc import SQLAlchemyError
import csv

from app.core.bus_stop import BUS_STOP_ROUTE
from app.core.segment import SEGMENT_ROUTE

#================================================================================
# DEFINITIONS: add_routes(), add_bus_stops(), add_bus_stop_routes()
#================================================================================
def add_routes(file_path: str) -> bool:
    db = SessionLocal()
    result = False
    try:
        with open(file_path, "r") as rf:
            routes = csv.reader(rf)
            for route in routes:
                route_name = route[0]
                route_type = route[-1]

                new_route_obj = Route(route_name=route_name, route_type=route_type)
                db.add(new_route_obj)
                db.commit()
                db.refresh(new_route_obj)
        result = True
    except SQLAlchemyError as e:
        print(f"{e}")
    finally:
        db.close()
    
    return result

def add_bus_stops(file_path: str) -> bool:
    db = SessionLocal()
    result = False

    try:
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
        result = True
    except SQLAlchemyError as e:
        print(f"{e}")
    finally:
        db.close()
    
    return result
    
# NOTE: with SessionLocal() as session:
# Add check if the file extension is .csv
def add_bus_stop_route(file_path: str, ROUTE: str) -> bool:
    db = SessionLocal()
    try:
        with open(file_path, "r") as rf:
            bus_stops = list(csv.reader(rf))

            # for bus_stop in bus_stop_objs:
            #     print(bus_stop)
            route_obj: Route = db.query(Route).filter(Route.name==f"{ROUTE}").first()
            route_id = route_obj.id

            for row in bus_stops:
                try:
                    bus_stop_obj: BusStop = db.query(BusStop).filter((BusStop.name==row[2]) & (BusStop.lon==row[-3]) & (BusStop.lat==row[-2])).first()
                    bus_stop_index = row[-1]

                    bus_stop_route: BusStopRoute = BusStopRoute(bus_stop_id=bus_stop_obj.id, route_id=route_id, bus_stop_index=bus_stop_index)

                    db.add(bus_stop_route)
                except Exception as e:
                    db.rollback()
                    print(f"Could not find BusStop object with give name: {e}")
            db.commit()
    except Exception as e1:
        db.rollback()
        print(f"Could not add bus_stop_route: {e1}")
    finally:
        db.close()
    
def read_bus_stops(bus_stop_name: str) -> list[BusStop]:
    db = SessionLocal()
    try:
        bus_stops = db.query(BusStop).filter(BusStop.bus_stop_name==bus_stop_name).all()
    except SQLAlchemyError as e:
        print(f"{e}")
    finally:
        db.close()

    return bus_stops

# Implements INSERT segment command: reades the csv file with ordered data and insrets those values to the db
# file_path: leads to the segment.csv file in the data folder
def add_segment(file_path:str) -> None:
    db = SessionLocal()
    try:
        with open(file_path, "r") as rf:
            reader = csv.reader(rf)

            for line in reader:
                segment = Segment(length=line[0], street=line[1],bus_stop_a=line[2],bus_stop_b=line[3])
                db.add(segment)
                
            db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Unexpected error: {e}")
    finally:    
        db.close()

def add_route_segment(file_path: str, ROUTE: str) -> bool:
    db = SessionLocal()
    result = False
    try:
        route: Route = db.query(Route).filter(Route.name==ROUTE).first()
        route_id = route.id
        segments: list[Segment] = db.query(Segment).all()

        with open(file_path, "r") as rf:
            reader = list(csv.reader(rf))

            for segment in segments:
                for line in reader:
                    if segment.bus_stop_a == int(line[-3]) and segment.bus_stop_b == int(line[-2]):
                        route_segment = RouteSegment(route_id=route_id,segment_id = segment.id, segment_index = line[-1])
                        db.add(route_segment)
                        result = True
            db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Unexpected error: {e}")
    finally:
        db.close()

    return result

def add_point(point_objs: list) -> bool:
    db = SessionLocal()
    result = False
    try:
        for point_obj in point_objs:
            point = Point(route_name=point_obj.ROUTE, longitude=point_obj.lng, latitude=point_obj.lat, point_index=point_obj.point_index, segment_index=point_obj.segment_index)
            db.add(point)
        db.commit()
        result = True
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Unexpected error: {e}")
    finally:
        db.close()
    
    return result

#================================================================================
# EXECUTION:
#================================================================================
ROUTE = "40"

# add_bus_stops(f"data/bus_stops/{BUS_STOP_ROUTE}/bus_stops.csv")
# add_bus_stop_route(f"app/data/bus_stops/{ROUTE}/bus_stops.csv", ROUTE)

# add_segment(f"app/data/segments/{ROUTE}/segments.csv")
# check = add_route_segment(f"app/data/segments/{ROUTE}/segments.csv", ROUTE)
# print(check)
# add_point(point_objs)

# add_bus_stop_route(f"app/data/bus_stops/{ROUTE}/bus_stops.csv", ROUTE)
