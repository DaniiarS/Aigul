import folium
import json
# from points import points_raw
import math

from app.db.crud import db # - causes circular import error , need to solve
from app.db.models import Route, Segment, RouteSegment, Point


class PointCls:
    def __init__(self, lng: float | str, lat: float | str, point_index = -1, segment_index = -1, ROUTE = None):
        self.lng: float = float(lng)
        self.lat: float = float(lat)
        self.point_index: int = int(point_index)
        self.segment_index: int = int(segment_index)
        self.ROUTE: str | None = ROUTE
    
    def __repr__(self):
        return f"Point(lng:{self.lng}, lat:{self.lat}, point_index:{self.point_index}, segment_index:{self.segment_index})"
    
    def to_dict(self, ROUTE: str):
        return {"route_name": ROUTE, "longitude": self.lng, "latitude": self.lat, "point_index": self.point_index, "segment_index": self.segment_index}
    
    @classmethod
    def raw_to_obj(cls, raw_point: dict):
        return cls(
            lng=float(raw_point["geometry"]["coordinates"][0]),
            lat=float(raw_point["geometry"]["coordinates"][-1]),
            point_index=int(raw_point["id"]),
            segment_index=int(raw_point["properties"]["id"]) + 1,
            ROUTE="7"
        )
    
    @classmethod
    def model_to_obj(cls, db_point: Point):
        return cls(
            lng=float(db_point.longitude),
            lat=float(db_point.latitude),
            point_index=int(db_point.point_index),
            segment_index=int(db_point.segment_index),
            ROUTE=str(db_point.route_name)
        )

#===============================================================================================
# DEFINITION: plot_coords(), haversine(), get_segment_index()
#===============================================================================================

def plot_coords(points: list, ROUTE: str):
    BISHKEK_COORDS = [42.8746, 74.5698]
    m = folium.Map(location=BISHKEK_COORDS, zoom_start=13)
    
    # Add markers
    for i, point in enumerate(points):
        folium.Marker(
            [point["lat"], point["lng"]],
            popup=f"lng:{point['lng']}, lat:{point['lat']}, index={i}",
            # tooltip="Click me"
        ).add_to(m)

    # Save to HTML file
    m.save(f"points_map_{ROUTE}-2.html")

    return None

def get_points(file_path: str) -> list[dict]:
    """ Filters the GeoJson object leaving only raw_point objects """

    with open(file_path, "r") as rf:
        data_raw: list = json.load(rf)["features"]
        points = []

        for data in data_raw:
            if data["geometry"]["type"] == "Point":
                points.append(data)

    return points

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

def get_segment(current: Point, ROUTE:str):
    """ Identifies to which segment does the "current" point belong to """
    segment = None
    ROUTE_ID = db.query(Route).filter(Route.route_name==ROUTE).first().route_id

    db_points = db.query(Point).filter(Point.route_name==ROUTE).all()
    points = [PointCls.model_to_obj(db_point) for db_point in db_points]

    for point in points:
        if abs(calc_distance(current, point)) < 35:
            segment_id: int = db.query(RouteSegment).filter((RouteSegment.segment_index==point.segment_index) & (RouteSegment.route_id == ROUTE_ID)).first().segment_id
            segment: Segment = db.query(Segment).filter(Segment.segment_id==segment_id).first()
            break
    return segment
    

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