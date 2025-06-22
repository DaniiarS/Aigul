from app.db import models
from app.db.database import SessionLocal, get_db
from app.api.schemas import schema
from app.db.redis_client import r

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

router = APIRouter()

#==================================================================================================
# LOGIC: update_eta_one(), update_eta_all()
#==================================================================================================
def printl(item_list: list):
    for item in item_list:
        print(item.bus_stop_index)

def update_eta_one(bus_stop_id: int):
    """ 
    Updates the ETA table at the certain bus stop. 
    It updates the expected time of arrival for all of the routes that goes through this bus stop.
    """
    # For testing pruposes IDs and other variables are HARD CODED
    # Bus Stop Indexes may not be consistent, instead use segment indexes
    # Find out a method to obtain all the routes that go through the current bus stop
    # Iterate through routes that go via current bus stop and get the list of routes: [7, 8, 9, ... , 153]

    BUS_STOP_CLIENT_KEY = f"BusStopClient:{bus_stop_id}:{7}:{24}"
    BUS_STOP_INDEX = 24
    db = SessionLocal()
    end_segment_index = -1
    try:
        bus_stop = db.query(models.BusStop).filter(models.BusStop.id==bus_stop_id).first()
        bus_stops = db.query(models.BusStopRoute).filter(models.BusStopRoute.route_id == 5).all()
        end_segment = db.query(models.Segment).filter((models.Segment.lat_b==str(bus_stop.lat)) & (models.Segment.lon_b==str(bus_stop.lon))).first()
        print(end_segment)
        end_segment_index = db.query(models.RouteSegment).filter((models.RouteSegment.route_id==5) & (models.RouteSegment.segment_id==end_segment.segment_id)).first().segment_index
        print(end_segment_index)
        bus_stops.sort(key=lambda item : item.bus_stop_index)
    except Exception as e:
        print(f"{e}")
    finally:
        db.close()

    current_segment_index = int(r.hget("bus:1", "current_segment_index"))
    eta = 0
    for i in range(end_segment_index-current_segment_index + 1):
        eta += r.hget(f"segment:{current_segment_index + i}","eta")

    # bus_client = r.hgetall("bus:1")
    # print(bus_client)
    # print(bus_client["current_segment_index"])

    return {f"{bus_stop_id}": eta}



def upadte_eta_all():
    """ 
    Updates the ETA table for all of the bus stops.
    It iterates over all of the bus stops, and updates the expected time of aarival for each of them.
    """
    pass

#==================================================================================================
# GET endpoints: get_segmnet()
#==================================================================================================
@router.get("/{bus_stop_id}")
def get_bus_stop(bus_stop_id: int, db: Session = Depends(get_db)):
    try:
        return db.query(models.BusStop).filter(models.BusStop.id == bus_stop_id).first()
    except:
        return {"message": "objest is not found"}

@router.get("/{route}/bus-stops")
def get_bus_stops(route: int):
    return update_eta_one(23)