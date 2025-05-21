import folium
import json
# from points import points_raw
import math

from app.db.crud import db # - causes circular import error , need to solve
from app.db.models import Route, Segment, RouteSegment


class Point:
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

def haversine(point1: Point, point2: Point):
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

def format_point(coord: str) -> Point:
    # Turns "(74.123123, 43.2349203)" into Point() object
    lng, lat = coord[1:-1].split(",")

    return Point(lng=lng, lat=lat)

def get_points(file_path: str) -> list:
    """ Clears the GeoJson object leaving only points objects """

    with open(file_path, "r") as rf:
        data_raw: list = json.load(rf)["features"]
        points = []

        for data in data_raw:
            if data["geometry"]["type"] == "Point":
                points.append(data)

    return points

def get_segment(current: Point, ROUTE:str):
    segment = None
    ROUTE_ID = db.query(Route).filter(Route.route_name==ROUTE).first().route_id

    points = db.query(Point)

    # print(ROUTE_ID)
    # route_segments: list[RouteSegment] = db.query(RouteSegment).filter(RouteSegment.route_id==ROUTE_ID).all()
    for point in points:
        if abs(haversine(current, point)) < 50:
            segment_id: int = db.query(RouteSegment).filter((RouteSegment.segment_index==point.segment_index) & (RouteSegment.route_id == ROUTE_ID)).first().segment_id
            segment: Segment = db.query(Segment).filter(Segment.segment_id==segment_id).first()
            break
    return segment
    

#===============================================================================================
# EXECUTION:
#===============================================================================================
points = get_points("app/utils/map-7-for-test.geojson") # raw points
ROUTE = "7"
segment_index = 0
point_objs: list[Point] = []

for point in points:
    print(point)

#==========
# Stopped here to test the if the chosen points return correct segment index
#==========

# for point in points:
#     segment_index = get_segment()

# for point_index, point in enumerate(points):
#     """ Cretes a list of Assistant-Point objects - helps dentify segment_index given the coordinates of the transport """

#     if point["properties"].get("flag"):
#         segment_index += 1
#     point_objs.append(Point(lng=point["geometry"]["coordinates"][0], lat=point["geometry"]["coordinates"][-1], point_index=point_index,segment_index=segment_index, ROUTE=ROUTE))

# current_points = [Point(lng="74.6909", lat="42.8666"), Point(lng="74.6574", lat="42.8557"), Point(lng="74.5726", lat="42.8773"), Point(lng="74.5694", lat="42.8801"), Point(lng="74.5643", lat="42.8845")]
# segments: list[Segment] = [get_segment(current, point_objs, "7") for current in current_points]
# print([segment.segment_street for segment in segments])