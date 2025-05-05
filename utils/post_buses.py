import requests
import csv
import time


# Read data from the csv
with open("buses.csv", "r") as f:
    reader = csv.reader(f)
    header = next(reader)

    url = "http://localhost:8000/bus"

    for row in reader:
        new_bus = {
            "bus_lng": float(row[0]),
            "bus_lat": float(row[1]),
            "route_name": row[2],
            "bus_gov_num": row[3],
            "bus_current_segment": 0
        }
        print(new_bus)
        response = requests.post(url, json=new_bus)
        print(response)
        time.sleep(4)