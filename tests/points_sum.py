import json

from app.db.database import SessionLocal
# from tests.generate_geojson import assistant_points

def filter_ap(file_path: str)-> list: # ap - assitant point
    result = []
    with open(file_path, "r") as rf:
        geo_json = json.load(rf)
        objects = geo_json["features"]

        for obj in objects:
            if obj["properties"].get("assistant-point") is not None:
                result.append(obj)
    return result

# filtered_points = filter_ap("tests/distance-points.geojson")
# filtered_points_coords = [[point["geometry"]["coordinates"][1], point["geometry"]["coordinates"][0]] for point in filtered_points]

# filtered_points[0]["properties"]["l_sum"] = float(filtered_points[0]["properties"]["l"])
# filtered_points[0]["properties"]["segment_id"] = 1
# size = len(filtered_points)
# for i in range(1, size):
#     filtered_points[i]["properties"]["l_sum"] = round(filtered_points[i-1]["properties"]["l_sum"] + float(filtered_points[i]["properties"]["l"]),2)
#     filtered_points[i]["properties"]["segment_id"] = 1

# with open("app/data/points/7/assitant_points/filtered_points-7-0.geojson", "w") as wf:
#     json.dump(filtered_points, wf)
# ap_to_db(filtered_points)

