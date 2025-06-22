import json
import csv

from app.db.database import SessionLocal
from app.db.models import Route, BusStop, Segment, BusStopRoute, Point, RouteSegment

from sqlalchemy.exc import IntegrityError

#====================================================================================
# DEFINITION: migrate_routes()
#====================================================================================

def migrate_routes(file_path: str):
    try:
        db = SessionLocal()
        with open(file_path, "r") as rf:
            data = json.load(rf)
            
        for obj in data:
            route = Route(name=obj["route_name"], type=obj["route_type"])
            db.add(route)
            
        db.commit()
    except IntegrityError as ie:
        db.rollback()
        print(f"Integrity error: {ie.orig}")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
    finally:
        db.close()

def migrate_buses():
    pass

def migrate_bus_stops(file_path: str):
    try:
        db = SessionLocal()

        with open(file_path, "r") as rf:
            data = json.load(rf)

        for obj in data:
            bus_stop = BusStop(name=obj["name"], lat=obj["lat"], lon=obj["lon"])
            db.add(bus_stop)
        db.commit()
    except IntegrityError as ie:
        db.rollback()
        print(f"Integrity error: {ie.orig}")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
    finally:
        db.close()

def migrate_segments(file_path: str):
    try:
        db = SessionLocal()

        with open(file_path, "r") as rf:
            data = json.load(rf)

        for obj in data:
            segment = Segment(length=obj["segment_length"], street=obj["segment_street"], bus_stop_a=obj["segment_bus_stop_a"], bus_stop_b=obj["segment_bus_stop_b"])
            db.add(segment)
        db.commit()
    except IntegrityError as ie:
        db.rollback()
        print(f"Integrity error: {ie.orig}")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
    finally:
        db.close()

def migrate_bus_stop_route():
    csv_file = "app/data/bus_stops/7/bus_stops.csv"
    try:
        db = SessionLocal()

        with open(csv_file, "r") as rf:
            reader = csv.reader(rf)
        
            for row in reader:
                lat, lon = str(float(row[4])), str(float(row[3]))
                route = str(row[1])
                bus_stop_index = int(row[5])

                bus_stop_id = db.query(BusStop).filter((BusStop.lat==lat) & (BusStop.lon==lon)).first().id
                route_id = db.query(Route).filter(Route.name==route).first().id

                bus_stop_route = BusStopRoute(bus_stop_id=bus_stop_id, route_id=route_id, bus_stop_index=bus_stop_index)
                db.add(bus_stop_route)
        
        db.commit()
    except IntegrityError as ie:
        db.rollback()
        print(f"Integrity error: {ie.orig}")    
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
    finally:
        db.close()

def migrate_points(file_path: str):
    try:
        db = SessionLocal()

        with open(file_path, "r") as rf:
            data = json.load(rf)

        for obj in data:
            lat, lon = str(float(obj["lat"])), str(float(obj["lon"]))
            point = Point(lat=lat, lon=lon, l_delta=obj["l_delta"], l_sum=obj["l_sum"], index=obj["index"], segment_id=obj["segment_id"])

            db.add(point)

        db.commit()
    except IntegrityError as ie:
        db.rollback()
        print(f"Integrity Error: {ie.orig}")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
    finally:
        db.close()
    
def migrate_route_segment(file_path: str):
    try:
        db = SessionLocal()
        route_id = db.query(Route).filter(Route.name=="7").first().id

        with open(file_path, "r") as rf:
            data = json.load(rf)

        for i, obj in enumerate(data):
            route_segment = RouteSegment(id=i, route_id=route_id, segment_id=obj["id"], segment_index=i)

            db.add(route_segment)
        
        db.commit()
    except IntegrityError as ie:
        db.rollback()
        print(f"Integrity Error: {ie.orig}")
    except Exception as e:
        db.rollback()
        print(f"Unexpected Error: {e}")
    finally:
        db.close()

#====================================================================================
# EXECUTION:
#====================================================================================
# migrate_routes("app/db/migrations/data/route-aigul.json")
# migrate_bus_stops("app/db/migrations/data/bus_stop-rmd.json")
# migrate_segments("app/db/migrations/data/segment-upd.json")
# migrate_bus_stop_route()
# migrate_points("app/db/migrations/data/point-aigul.json")
# migrate_route_segment("app/db/migrations/data/segment-psql.json")
