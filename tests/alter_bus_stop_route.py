from app.db import models
from app.db.database import SessionLocal

db = SessionLocal()
try:
    bus_stop_routes = db.query(models.BusStopRoute).filter(models.BusStopRoute.route_id==5).all()

    for bsr in bus_stop_routes:
        if bsr.bus_stop_index >= 22:
            bsr.bus_stop_index += 1
    new_bsr = models.BusStopRoute(bus_stop_id=28,route_id=5,bus_stop_index=22)
    db.add(new_bsr)
    db.commit()
    db.refresh(new_bsr)
except Exception as e:
    print(f"{e}")
finally:
    db.close()