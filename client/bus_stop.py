from app.db.database import SessionLocal
from app.db.models import Bus, Segment, BusStop, BusStopRoute

try:
    db = SessionLocal()

    bus_id = 1
    segment_id = 7
    # bus = db.query(Bus).filter(Bus.id==bus_id).first()
    # segments = bus.route.segments
    # for s in segments:
    #     print(s)

    # segment = db.query(Segment).filter(Segment.id == segment_id).first()
    # print(segment.routes)
    bus_stop = db.query(BusStop).filter(BusStop.id==1).first()
    index = db.query(BusStopRoute).filter(BusStopRoute.bus_stop_id==bus_stop.id).first().bus_stop_index
    print(index)
except Exception as e:
    print(f"{e}")
finally:
    db.close()