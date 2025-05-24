import math
import folium

from app.db.database import SessionLocal
from app.db.crud import get_db
from app.db.models import Route, Segment, RouteSegment, Point, BusStop
from app.core.point import PointEntity
from app.core.bus_stop import BusStopEntity

from sqlalchemy.exc import SQLAlchemyError

#===============================================================================================
# DEFINITION: plot_coords(), haversine(), get_segment_index()
#===============================================================================================

def calc_distance(point1: Point, point2: Point) -> float:
    """ Utilizes Haversine formula to calculate the distance between "point1" and "point2" in meters """
    EARTH_R = 6371000 # Earth's radius in meters

    # convert degrees to radians
    phi_1 = math.radians(point1.lat)
    phi_2 = math.radians(point2.lat)

    d_phi = math.radians(point2.lat - point1.lat)
    d_lambda = math.radians(point2.lng - point1.lng)

    # Haversine formula
    a = math.sin(d_phi / 2.0)**2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(d_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = EARTH_R * c

    return round(distance,2)

def search_segment(current: PointEntity, ROUTE:str) -> Segment:
    """ Identifies to which segment does the "current" point belong to """

    db = SessionLocal()
    try:
        segment = None
        ROUTE_ID = db.query(Route).filter(Route.route_name==ROUTE).first().route_id
        db_points = db.query(Point).filter(Point.route_name==ROUTE).all()
        points = [PointEntity.model_to_obj(db_point) for db_point in db_points]

        for point in points:
            if abs(calc_distance(current, point)) < 15:
                segment_id: int = db.query(RouteSegment).filter((RouteSegment.segment_index==point.segment_index) & (RouteSegment.route_id == ROUTE_ID)).first().segment_id
                segment: Segment = db.query(Segment).filter(Segment.segment_id==segment_id).first()
                break
    except SQLAlchemyError as e:
        print(f"{e}")
    finally:        
        db.close()

    return segment

def is_bus_stop(current: PointEntity, ROUTE: str):
    """ Checks if the current location is the bus stop """

    db = SessionLocal()
    result = False
    try:
        bus_stops = db.query(BusStop).filter(BusStop.bus_stop_name==ROUTE).all()
    except Exception as e:
        print("Error trying to query the database")
    finally:
        db.close()
    
    bus_stop_objects = [BusStopEntity.model_to_obj(m_object) for m_object in bus_stops]
    for bus_stop_obj in bus_stop_objects:
        if calc_distance(current, bus_stop_obj) < 15:
            result = True
            break

    return result

#===============================================================================================
# EXECUTION:
#===============================================================================================
# ROUTE = "7"
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