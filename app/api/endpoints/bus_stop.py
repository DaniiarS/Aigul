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

@router.post("/{bus_stop_id}")
def update_eta_one(bus_stop_id: int, db: Session = Depends(get_db)):
    """ 
    Updates the ETA table at the certain bus stop.
    It updates the expected time of arrival for all of the routes that goes through this bus stop.
    """
    # Bus Stop Indexes may not be consistent, instead use segment indexes
    # Find out a method to obtain all the routes that go through the current bus stop
    # Iterate through routes that go via current bus stop and get the list of routes: [7, 8, 9, ... , 153]

    # BUS_STOP_CLIENT_KEY = f"BusStopClient:{bus_stop_id}:{7}:{24}"
    # BUS_STOP_INDEX = 24
    eta = {}

    try:
        bus_stop: models.BusStop = db.query(models.BusStop).filter(models.BusStop.id==bus_stop_id).first()
        routes: list[models.Route] = bus_stop.routes

        for route in routes:
            """ For each given route that passes through this BusStop find out the bus that is first in the queue and calculate eta """
            bus_stop_index: int = db.query(models.BusStopRoute).filter((models.BusStopRoute.bus_stop_id==bus_stop.id) & (models.BusStopRoute.route_id==route.id)).first().bus_stop_index
            BUS_STOP_CLIENT_KEY: str = f"BusStopClient:{bus_stop.id}:{bus_stop.name}:{route.name}:{bus_stop_index}"

            if r.exists(BUS_STOP_CLIENT_KEY):
                gov_num = r.lindex(BUS_STOP_CLIENT_KEY, 0)
                eta_sum = 0
                distance_sum = 0
                
                #============================================================================
                # Compute eta: try to implement prefix sum to calcualte eta fast
                #============================================================================
                try:
                    BUS: models.Bus = db.query(models.Bus).filter(models.Bus.gov_num==gov_num).first()
                    if BUS:
                        bus_index: str = int(r.hget(f"bus:{BUS.id}", "current_segment_index"))
                        delta: int = bus_stop_index - bus_index

                        if delta > 0:
                            for i in range(delta-1):
                                segment_id = None
                                try:
                                    # seems like inccorect logic -> work with RouteSegmnet
                                    segment_id = db.query(models.RouteSegment).filter((models.RouteSegment.route_id==route.id) & (models.RouteSegment.segment_index==bus_stop_index-i)).first().segment_id
                                except Exception as e1:
                                    print(f"Error when trying to figure out a segment: {e1}")
                                
                                
                                if segment_id:
                                    eta_sum += float(r.hget(f"segment:{segment_id}", "eta"))
                                    distance_sum += float(r.hget(f"segment:{segment_id}", "length"))
                                else:
                                    print("segment was not found")
                                    break
                        
                            if eta_sum > 0:
                                r.hset(f"BusStopClientETA:{bus_stop.id}", route.name, int(eta_sum//60))
                                r.hset(f"BusStopClientDISTANCE:{bus_stop.id}", route.name, round(distance_sum/1000,2))
                        else:
                            # If Bus passes the BusStop we can clear the ETA
                            if r.hexists(f"BusStopClientETA:{bus_stop_id}", route.name):
                                r.hdel(f"BusStopClientETA:{bus_stop_id}", route.name)
                                r.hdel(f"BusStopClientDISTANCE:{bus_stop_id}", route.name)

                except Exception as e2:
                    print(f"Error when trying to update eta for a bus: {e2}")

    except Exception as e:
        print(f"Here: {e}")

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