import requests
import time
import random
import sys

from app.db.redis_client import r
from app.db.database import SessionLocal
from app.db.models import Bus

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


coords = filter_test_points(f"tests/test_update_segment_eta/test-points-raw-{bus.route_name}-all.geojson")

for coord in coords:
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
    time.sleep(1)