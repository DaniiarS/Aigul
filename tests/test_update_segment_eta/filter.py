import json

# Reads geojson file and filters test points from the file. Returns a list of coordinates (lat, lon)
def filter_test_points(file_path: str) -> list[tuple]:
    result = []
    with open(file_path, "r") as rf:
        geo_json: dict = json.load(rf)
        objects: list[dict] = geo_json["features"]

        for obj in objects:
            if obj["geometry"]["type"] == "Point" and (obj["properties"].get("marker-size") == None):
                lat = obj["geometry"]["coordinates"][-1]
                lon = obj["geometry"]["coordinates"][0]

                result.append((lat, lon))
    return result