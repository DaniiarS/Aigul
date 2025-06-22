from app.db.database import SessionLocal
from app.db.models import BusStopRoute

db = SessionLocal()

# try: 
#     bsr = db.query(BusStopRoute).filter(BusStopRoute.route_id==5).all()

#     for item in bsr:
#         if item.bus_stop_index >= 21:
#             item.bus_stop_index += 1
#     db.commit()
# except Exception as e:
#     print(f"Unexpected error: {e}")

# try:
#     bsr = BusStopRoute(bus_stop_id=140, route_id=5, bus_stop_index=21)
#     db.add(bsr)
#     db.commit()
# except Exception as e:
#     print(f"Unexpected error: {e}")
# finally:
#     db.close()
