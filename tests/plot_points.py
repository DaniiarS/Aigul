from app.core.point import plot_points
from app.db.database import SessionLocal
from app.db.models import Point

db = SessionLocal()
try:
    points = db.query(Point).all()
    plot_points(points, "7")
except Exception as e:
    print(f"{e}")
finally:
    db.close()
