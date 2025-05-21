from app.db import models
from app.db.database import get_db
from app.api.schemas import schema

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/{bus_stop_id}")
def get_bus_stop(bus_stop_id: int, db: Session = Depends(get_db)):
    try:
        return db.query(models.BusStop).filter(models.BusStop.id == bus_stop_id)
    except:
        return {"message": "objest is not found"}

@router.post("/")
def create_bus_stop(bus_stop: schema.BusStop, db: Session = Depends(get_db)):
    new_bus_stop = models.BusStop(
        bus_stop_name = bus_stop.bus_stop_name,
        bus_stop_addr = bus_stop.bus_stop_addr,
        bus_stop_lng = bus_stop.bus_stop_lng,
        bus_stop_lat = bus_stop.bus_stop_lat
    )

    db.add(new_bus_stop)
    db.commit()
    db.refresh(new_bus_stop)

    return new_bus_stop