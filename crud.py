from database import SessionLocal
from models import BusStopRoute, Route, BusStop
import csv


db = SessionLocal()

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


