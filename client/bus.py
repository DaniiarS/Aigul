import requests
import time
import random
import sys

from app.db.redis_client import r
from app.db.database import SessionLocal
from app.db.models import Bus
from app.utils.gps_filter import filter_point

from tests.test_update_segment_eta.filter import filter_test_points

url_1= "http://127.0.0.1:8000/segment/update-segment-eta"
url_2 = "http://127.0.0.1:8000/segment/update-coordinates"


# coords = [(42.8739, 74.6900), (42.8739, 74.6905), (42.8720, 74.6906), (42.8704, 74.6906), (42.8676, 74.6906), (42.8656, 74.6907), (42.8643, 74.6909)]
bus_id = sys.argv[1]
bus = None
try:
    db = SessionLocal()
    bus = db.query(Bus).filter(Bus.id==int(bus_id)).first()
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    db.close()


coords = filter_test_points(f"tests/test_update_segment_eta/test-points-raw-{bus.route_name}-bus_stops-{bus_id}.geojson")

use_gps_filter = True

for coord in coords:
    if use_gps_filter:
        R_BUS_NAME = f"bus:{bus_id}"

        prev_lat = prev_lon = prev_time_str = None
        if r.exists(R_BUS_NAME):
            try:
                prev_lat = float(r.hget(R_BUS_NAME, "lat"))
                prev_lon = float(r.hget(R_BUS_NAME, "lon"))
                prev_time_str = r.hget(R_BUS_NAME, "last_modified")  # may be None
            except Exception:
                # If anything goes wrong we simply treat this as the very first fix.
                prev_lat = prev_lon = prev_time_str = None

        smoothed_lat, smoothed_lon, accepted = filter_point(
            coord[0],
            coord[1],
            prev_lat,
            prev_lon,
            prev_time_str,
        )
    
        data = {
            "id": int(sys.argv[1]),
            "lat": smoothed_lat, 
            "lon": smoothed_lon, 
            "speed": random.random()
        }
    else:
        data = {
            "id": int(sys.argv[1]),
            "lat": coord[0], 
            "lon": coord[1], 
            "speed": random.random()
        }

    response = requests.post(url_1,json=data)
    requests.post(url_2, json=data)
    # print(response.status_code)
    print(response.text)
    time.sleep(5)