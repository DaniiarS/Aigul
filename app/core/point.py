from app.db.models import Point


import json
import folium

class PointEntity:
    def __init__(self, lng: float | str, lat: float | str, point_index = -1, segment_index = -1, ROUTE = None):
        self.lng: float = float(lng)
        self.lat: float = float(lat)
        self.point_index: int = int(point_index)
        self.segment_index: int = int(segment_index)
        self.ROUTE: str | None = ROUTE
    
    def __repr__(self):
        return f"Point(lng:{self.lng}, lat:{self.lat}, point_index:{self.point_index}, segment_index:{self.segment_index}, route:{self.ROUTE})"
    
    def to_dict(self, ROUTE: str):
        return {"route_name": ROUTE, "longitude": self.lng, "latitude": self.lat, "point_index": self.point_index, "segment_index": self.segment_index}
    
    @classmethod
    def json_to_obj(cls, json_point: dict):
        return cls(
            lng=float(json_point["geometry"]["coordinates"][0]),
            lat=float(json_point["geometry"]["coordinates"][-1]),
            point_index=int(json_point["point_index"]),
            segment_index=int(json_point["segment_index"]),
            ROUTE=str(json_point["route"])
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

#=======================================================================
# DEFINITIONS: filter_points(), plot_points()
#=======================================================================

def filter_points(file_path: str) -> list[dict]:
    """ Filters the GeoJson object leaving only json_point objects """

    with open(file_path, "r") as rf:
        data_raw: list = json.load(rf)["features"]
        points = []

        for data in data_raw:
            if data["geometry"]["type"] == "Point":
                points.append(data)

    return points

def plot_points(points: list, ROUTE: str):
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

#=======================================================================
# EXECUTION:
#=======================================================================















""" Filters points from raw_json_data. Creates a list of PointCls objects. Adds to the database """
# ROUTE: str = "7"
# CWD_PATH: str = "app/data/points/" #CGWD - Current Working Directory

# json_points: list[dict] = []
# for i in range(4):
#     json_points.extend(filter_points(CWD_PATH+f"{ROUTE}/assistant_points/points-proper{i+1}-7.geojson"))

# # Adds point_index and segment_index
# segment_index = 0

# for point_index, point in enumerate(json_points):
#     point["route"] = ROUTE
#     point["point_index"] = point_index
#     point["segment_index"] = segment_index
#     if point["properties"].get("end") is not None:
#         point["segment_index"] = segment_index
#         segment_index = point["properties"]["end"] + 1
    
# point_objects = [PointCls.json_to_obj(j_point) for j_point in json_points]