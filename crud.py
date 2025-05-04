from database import SessionLocal
from models import BusStopRoute, Route
import csv


db = SessionLocal()

# with open("utils/write_bus_stop_route.csv", "r") as rf:
#     reader = csv.reader(rf)
#     data = list(reader)

#     for row in data:
#         bus_stop_route = BusStopRoute(
#             bus_stop_id = row[0],
#             route_id = row[1],
#             bus_stop_index = row[2]
#         )

#         db.add(bus_stop_route)
#         db.commit()
#         db.refresh(bus_stop_route)
#         db.close()


# new_route = Route(route_name = "7")
# db.add(new_route)
# db.commit()
# db.refresh(new_route)
# db.close()
