from app.utils.eta import get_segment, calc_distance
from app.db.crud import db
from app.db.models import Point, Segment, RouteSegment

from app.data.points.helper import PointCls, filter_points


#========================================================================
# DEFINITIONS: test_get_segment() 
#========================================================================

def test_get_segment(sample_points: list[PointCls], ROUTE:str):
    db_points = db.query(Point).filter(Point.route_name==ROUTE).all()
    point_objects = [PointCls.model_to_obj(db_point) for db_point in db_points]

    with open(f"tests/test-results-{ROUTE}.txt", "w") as wf:
        failed = 0
        passed = 0
        
        for sample_point in sample_points:
            found = False

            for point_object in point_objects:
                if calc_distance(sample_point, point_object) < 15:
                    found = True
                    segment_index_test = sample_point.segment_index
                    segment_index_db = point_object.segment_index
                    break

            """ Need to re-write better """
            if found:
                if (segment_index_test == segment_index_db):
                    passed += 1
                    wf.write(".\n")
                else:
                    wf.write(f"F - {sample_point.segment_index} - ({sample_point.lat},{sample_point.lng})\n")
                    failed += 1
            else:
                wf.write("Not found\n")
                failed += 1

        wf.write(f"Number of tests: {failed+passed}\n")
        wf.write(f"Passed:{passed}\tFailed:{failed}\n")
        wf.write(f"{round(passed/(passed+failed)*100,2)}\n")

#========================================================================
# EXECUTION:
#========================================================================

ROUTE = "7"
CWD_PATH = "tests/"

json_points = filter_points(CWD_PATH+f"test-points-{ROUTE}.geojson")
segment_index = 0
for point_index, j_point in enumerate(json_points):
    j_point["route"] = ROUTE
    j_point["point_index"] = point_index
    j_point["segment_index"] = segment_index
    if j_point["properties"].get("end") is not None:
        j_point["segment_index"] = segment_index
        segment_index = j_point["properties"]["end"] + 1

point_objects =[PointCls.json_to_obj(j_point) for j_point in json_points]
test_get_segment(point_objects, ROUTE)