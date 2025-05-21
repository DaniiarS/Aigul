from app.db import models
from app.db.database import get_db
from app.api.schemas import schema

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/{route_id}")
def get_route(route_id: int, db: Session = Depends(get_db)):
    try:
        return db.query(models.Route).filter(models.Route.route_id == route_id).all()
    except:
        return {"message": "object is not found"}

@router.post("/{route_id}")
def create_route(route: schema.Route, db: Session = Depends(get_db)):

    # new_route = models.Route(
    #     route_name = route.route_name,
    #     bus_stops = [bs_1, bs_2]
    # )

    # db.add_all([new_route, bs_1, bs_2])
    # db.commit()
    # db.refresh(new_route)

    return {"message": "Route added successfully"}