from app.utils.eta import search_segment, calc_distance, is_bus_stop
from app.db.database import SessionLocal
from app.db.models import Point, Segment, RouteSegment, BusStop

from app.core.point import PointEntity, filter_points
from app.core.bus_stop import BusStopEntity, plot_bus_stops

from sqlalchemy.exc import SQLAlchemyError


#========================================================================
# DEFINITIONS: test_get_segment() 
#========================================================================

def test_get_segment(sample_points: list[PointEntity], ROUTE:str):
    db = SessionLocal()

    try:
        db_points = db.query(Point).filter(Point.route_name==ROUTE).all()
        point_objects = [PointEntity.model_to_obj(db_point) for db_point in db_points]

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
    except SQLAlchemyError as e:
        print(f"{e}")
    finally:
        db.close()

    
def test_is_bus_stop(sample_points: list[PointEntity], ROUTE: str):
    db = SessionLocal()

    try:
        bus_stops = db.query(BusStop).filter(BusStop.bus_stop_name==ROUTE).all()
        bus_stops_objects = [(BusStopEntity.model_to_obj(m_object), "blue") for m_object in bus_stops]

        passed = 0
        failed = 0
        failed_points = []
        passed_points = []
        with open(f"tests/test_is_bus_stop/{ROUTE}/output.txt", "w") as wf:
            for s_point in sample_points:
                if is_bus_stop(s_point, ROUTE):
                    wf.write(".\n")
                    passed_points.append((BusStopEntity(s_point.point_index,lat=s_point.lat, lng=s_point.lng), "green"))
                    passed += 1
                else:
                    wf.write(f"F - {s_point.point_index} - ({s_point.lat},{s_point.lng})\n")
                    failed_points.append((BusStopEntity(s_point.point_index,lat=s_point.lat, lng=s_point.lng), "red"))
                    failed += 1
            wf.write(f"Total tests: {passed + failed}\n")
            wf.write(f"Passed:{passed}\tFailed:{failed}\n")
            wf.write(f"Passed_percentage:{(passed/(passed+failed)*100)}\n")
    except SQLAlchemyError as e:
        print(f"{e}")
    finally:
        db.close()
    
    bus_stops_objects.extend(passed_points)
    bus_stops_objects.extend(failed_points)

    plot_bus_stops(bus_stops_objects, ROUTE,f"tests/test_is_bus_stop/{ROUTE}")

#========================================================================
# EXECUTION:
#========================================================================

""" Preprocessing data to perform tests """
# ROUTE = "7"
# CWD_PATH = "tests/"

# json_points = filter_points(CWD_PATH+f"test_is_bus_stop/{ROUTE}/test_is_bus_stop-{ROUTE}.geojson")
# segment_index = 0
# for point_index, j_point in enumerate(json_points):
#     j_point["route"] = ROUTE
#     j_point["point_index"] = point_index
#     j_point["segment_index"] = segment_index
#     # if j_point["properties"].get("end") is not None:
#     #     j_point["segment_index"] = segment_index
#     #     segment_index = j_point["properties"]["end"] + 1

# point_objects =[PointEntity.json_to_obj(j_point) for j_point in json_points]

# test_is_bus_stop(point_objects, ROUTE)