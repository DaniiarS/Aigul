from app.utils.eta import get_points, get_segment
from app.db.crud import db
from app.db.models import Point, Segment, RouteSegment

from app.utils.eta import PointCls


def test_points(sample_points: list, ROUTE:str):
    # db_points = db.query(Point).filter(Point.route_name==ROUTE).all()
    # point_obj = [PointCls.model_to_obj(db_point) for db_point in db_points]

    with open(f"tests/test-results-{ROUTE}.txt", "w") as wf:
        failed = 0
        passed = 0
        sample_points = sample_points[0:-1]
        for s_point in sample_points:
            try:
                segment = get_segment(PointCls.raw_to_obj(s_point), ROUTE)
            except Exception as e2:
                print(e2)
            s_index= s_point["properties"]["id"]
            db_index = db.query(RouteSegment).filter(RouteSegment.segment_id==segment.segment_id).first().segment_index
            if s_index == db_index:
                wf.write(".\n")
                passed += 1
            else:
                wf.write(f"F - {s_point['id']} - {s_point['geometry']['coordinates'][0]}, {s_point['geometry']['coordinates'][1]} - {s_index} - {db_index} - {segment.segment_id}\n")
                failed += 1
        wf.write(f"Number of tests: {failed+passed}\n")
        wf.write(f"Passed:{passed}\tFailed:{failed}")

ROUTE = "7"
sample_points = get_points(f"app/data/points/{ROUTE}/map-{ROUTE}-for-test.geojson") 
""" points consists of the following type of raw_point objects """
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
test_points(sample_points, ROUTE)