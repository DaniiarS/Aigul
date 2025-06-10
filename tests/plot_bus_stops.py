from app.db.database import SessionLocal
from app.db import models
from app.core.bus_stop import plot_bus_stops

db = SessionLocal()
try:
    bus_stop_route = db.query(models.BusStopRoute).filter(models.BusStopRoute.route_id==5).all()
    bus_stops = [db.query(models.BusStop).filter(models.BusStop.id==bsr.bus_stop_id).first() for bsr in bus_stop_route]
    plot_bus_stops(bus_stops,"7")
except Exception as e:
    print(f"{e}")
finally:
    db.close()