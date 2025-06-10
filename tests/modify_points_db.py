from app.db.database import SessionLocal
from app.db.models import Point

db = SessionLocal()
try:
    points = db.query(Point).all()
    for point in points:
        if point.segment_id >= 20 and point.segment_id <= 26:
            point.segment_id += 2
    db.commit()
except Exception as e:
    print(f"{e}")
finally:
    db.close()
