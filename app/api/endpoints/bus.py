from app.db import models
from app.db.database import get_db
from app.api.schemas import schema

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session


router = APIRouter()

@router.get("/{bus_id}")
def get_bus(bus_id: int, db: Session = Depends(get_db)):
    try:
        return db.query(models.Bus).filter(models.Bus.bus_id == bus_id).all()
    except:
        return {"message": "object is not found"}
    
@router.post("/")
def create_bus(bus: schema.Bus, db: Session = Depends(get_db)):
    
    # Create a new tuple to add to database
    new_bus = models.Bus(
        # bus_id = bus.bus_id,
        bus_lng = bus.bus_lng,
        bus_lat = bus.bus_lat,
        route_name = bus.route_name,
        bus_gov_num = bus.bus_gov_num,
        bus_current_segment = bus.bus_current_segment
    )

    # Commands to update the database
    db.add(new_bus)
    db.commit()
    db.refresh(new_bus)

    return new_bus