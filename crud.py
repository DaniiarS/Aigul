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

# Add check if the file extension is .csv
def add_bus_stop_routes(file_path: str):
    with open(file_path, "r") as rf:
        bus_stop_indexes = list(csv.reader(rf))
        bus_stop_objs = db.query(BusStop).filter(BusStop.bus_stop_name==f"{route_number}").all()

        # for bus_stop in bus_stop_objs:
        #     print(bus_stop)
        route_obj = db.query(Route).filter(Route.route_name==f"{route_number}").first()
        route_id = route_obj.route_id

        CONST = 100
        line = [0 for i in range(CONST)]

        for i, bus_stop in enumerate(bus_stop_objs):
            for row in bus_stop_indexes:
                if row[2] == bus_stop.bus_stop_addr:
                    if line[int(row[-1])] == 1:
                        continue

                    new_bus_stop_route_obj = BusStopRoute(bus_stop_id=bus_stop.bus_stop_id, route_id=route_id,bus_stop_index=int(row[-1]))
                    line[int(row[-1])] = 1

                    db.add(new_bus_stop_route_obj)
                    db.commit()
                    db.refresh(new_bus_stop_route_obj)
    
    db.close()

route_number = "8"
add_bus_stop_routes(f"data/bus_stops/{route_number}/bus_stops.csv")
