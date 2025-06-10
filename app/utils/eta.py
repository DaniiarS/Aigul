import math

from app.db.database import SessionLocal
from app.db.crud import get_db
from app.db.models import Route, Segment, RouteSegment, Point, BusStop, BusStopRoute
from app.core.point import Coord

from sqlalchemy.exc import SQLAlchemyError

#===============================================================================================
# DEFINITION: plot_coords(), haversine(), get_segment_index()
#===============================================================================================

def calc_distance(point1: Coord, point2: Coord) -> float:
    """ Utilizes Haversine formula to calculate the distance between "point1" and "point2" in meters """
    EARTH_R = 6371000 # Earth's radius in meters

    # convert degrees to radians
    phi_1 = math.radians(point1.lat)
    phi_2 = math.radians(point2.lat)

    d_phi = math.radians(point2.lat - point1.lat)
    d_lambda = math.radians(point2.lon - point1.lon)

    # Haversine formula
    a = math.sin(d_phi / 2.0)**2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(d_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = EARTH_R * c

    return round(distance,2)

def search_segment(current: Coord, ROUTE:str) -> Segment:
    """ Identifies to which segment does the "current" point belong to """

    db = SessionLocal()
    segment = None
    point = None
    try:
        ROUTE_ID = db.query(Route).filter(Route.route_name==ROUTE).first().route_id
        segments = db.query(RouteSegment).filter(RouteSegment.route_id==ROUTE_ID).all()

        for route_segment in segments:
            points = db.query(Point).filter(Point.segment_id==route_segment.segment_id).all()
            for p in points:
                if abs(calc_distance(current, Coord(p.lat, p.lon))) <= 15:
                    segment: Segment = db.query(Segment).filter(Segment.segment_id==p.segment_id).first()
                    point: Point = p
                    break
    except SQLAlchemyError as e:
        print(f"{e}")
    finally:        
        db.close()

    return (segment, point)

def is_bus_stop(current: Coord, ROUTE: str) -> tuple[bool,BusStop]:
    """ Checks if the current location is the bus stop """

    db = SessionLocal()
    result = False
    target_bus_stop = None
    target_bus_stop_route = None
    try:
        bus_stops = db.query(BusStop).filter(BusStop.route==ROUTE).all()
    except Exception as e:
        print(f"Error trying to query the database: {e}")
        return result
    finally:
        db.close()
    
    # bus_stop_objects = [BusStopEntity.model_to_obj(m_object) for m_object in bus_stops]
    for bus_stop in bus_stops:
        if calc_distance(current, Coord(bus_stop.lat, bus_stop.lon)) <= 15:
            result = True
            target_bus_stop = bus_stop
            try:
                target_bus_stop_route = db.query(BusStopRoute).filter(BusStopRoute.bus_stop_id==bus_stop.id).first()
            except Exception as e:
                print(f"{e}")
            finally:
                break
    return (result, target_bus_stop, target_bus_stop_route)

def update_ETA(bus_stop: BusStop, time_traveled: float) -> bool:
    db = SessionLocal()
    result = False
    try:
        segment_to_update = db.query(Segment).filter((Segment.lat_b == bus_stop.lat) & (Segment.lon_b == bus_stop.lon)).first()
        segment_to_update.segment_eta  = (segment_to_update.segment_eta + time_traveled)/(segment_to_update.updated_times + 1)
        db.commit()
        result = True
    except Exception as e:
        print(f"{e}")
    finally:
        db.close()
    
    return result

#===============================================================================================
# EXECUTION:
#===============================================================================================
ROUTE = "7"
# get_segment(Point(""))
# points = get_points("app/utils/map-7-for-test.geojson") 
# """ points consists of the following type of raw_point objects """
#      {
#             "type": "Feature",
#             "properties": {
#                 "id": 38
#             },
#             "geometry": {
#                 "coordinates": [
#                     74.50887286454531,
#                     42.93679223807791
#                 ],
#                 "type": "Point"
#             },
#             "id": 140
#      }

# print(get_segment(PointEntity(lng=74.6920, lat=42.8551), ROUTE))

p = Coord(lon=74.6899,lat=42.8739)
p1 = Coord(lon=74.6900,lat=42.8739)
p2 = Coord(lon=74.6900,lat=42.8739)
p3 = Coord(lon=74.6900,lat=42.8739)
p4 = Coord(74.6903, 42.8739)

p5 = Coord(74.6905, 42.8718)
p6 = Coord(74.6906,42.8695)
p7 = Coord(74.6906, 42.8690)
p8 = Coord(74.6906, 42.8689)
p9 = Coord(74.6906, 42.8688)
p10 = Coord(74.6906, 42.8688)


# print(is_bus_stop(p, ROUTE))
# print(is_bus_stop(p1, ROUTE))
# print(is_bus_stop(p2, ROUTE))
# print(is_bus_stop(p3, ROUTE))
# print(is_bus_stop(p4, ROUTE))

# print(is_bus_stop(p5, ROUTE))
# print(is_bus_stop(p6, ROUTE))
# print(is_bus_stop(p7, ROUTE))
# print(is_bus_stop(p8, ROUTE))
# print(is_bus_stop(p9, ROUTE))
# print(is_bus_stop(p10, ROUTE))

# info = search_segment(p7, ROUTE)
# print(info[0].segment_street)
# print(round(info[0].segment_length - info[1].l_sum,2))
# print(calc_distance(p7,info[1]) + (info[0].segment_length - info[1].l_sum))
# print(search_segment(p1, ROUTE).segment_street)
# print(search_segment(p2, ROUTE).segment_street)
# print(search_segment(p3, ROUTE).segment_street)
# print(search_segment(p4, ROUTE).segment_street)
# print(search_segment(p5, ROUTE).segment_street)
# print(search_segment(p6, ROUTE).segment_street)
# print(search_segment(p7, ROUTE).segment_street)
# print(search_segment(p8, ROUTE).segment_street)
# print(search_segment(p9, ROUTE).segment_street)
# print(search_segment(p10, ROUTE).segment_street)

