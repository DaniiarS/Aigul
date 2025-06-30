from app.db.database import SessionLocal
from app.db.models import Bus, Segment, BusStop, BusStopRoute

import requests
import time

url = "http://127.0.0.1:8000/bus_stop/23"
data = {
    "id": 23
}

while True:
    response = requests.post(url=url, json=data)
    print(response)
    time.sleep(2)
