from app.db import models
from app.api.schemas import schema
from app.db.database import get_db
from app.utils.eta import search_segment, is_bus_stop
from app.core.point import Coord

from fastapi import Depends, HTTPException, APIRouter
from fastapi import WebSocket
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.redis_client import r
from datetime import datetime, timedelta
from typing import List
import asyncio
import json


router = APIRouter()
websocket_clients: List[WebSocket] = []
#==================================================================================================
# GET endpoints: get_segmnet()
#==================================================================================================
@router.get("/{segment_id}", response_model=schema.Segment, response_class=JSONResponse)
def get_segment(segment_id: int, db: Session = Depends(get_db)):
    segment = db.query(models.Segment).filter(models.Segment.segment_id == segment_id).first()
    if segment is None:
        raise HTTPException(status_code=404, detail="Segment is not found")
    segment_data = schema.Segment.from_orm(segment).dict()
    return JSONResponse(content=segment_data, media_type="application/json; charset=utf-8")

#==================================================================================================
""" Created this endpoints for testing purposes """
#==================================================================================================

@router.post("/update-coordinates")
async def update_coordinates(busInfo: schema.BusInfo):
    for ws in websocket_clients[:]:  # Use a copy to safely remove disconnected sockets
        try:
            await ws.send_json({"id": busInfo.id, "lat": busInfo.lat, "lon": busInfo.lon})
        except:
            websocket_clients.remove(ws)
    return {"status": "received"}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except:
        pass
    finally:
        if websocket in websocket_clients:
            websocket_clients.remove(websocket)

#============================================================================================================
# POST endpoints: get_segmnet()
#============================================================================================================











@router.post("/update-segment-eta")
def eta(busInfo: schema.BusInfo, db: Session = Depends(get_db)):

    #=========================================================================================================
    # PRE-INITIALIZATION REDIS:
    #=========================================================================================================
    ALLOWED_SPEED = 25 * 1000 / 3600
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f"
    CURRENT_SEGMENT = None
    BUS = None
    SEGMENTS = None

    """ GET DATA for INITIALIZATION """
    try:
        # Bus object from psql
        BUS = db.query(models.Bus).filter(models.Bus.id==busInfo.id).first()

        # Get the route of the bus -> 7, 153 or else
        ROUTE = BUS.route           # Route object -> (7, bus)
        BUS_STOPS = ROUTE.bus_stops # all the BusStop objects on the route of the Bus

        SEGMENTS = ROUTE.segments   # all the Segment objects on the route of the Bus
        N_SEGMENTS = len(SEGMENTS) # Number of segments on the route of the Bus

        # Identify current segment, and the closest assitant point to the (lat, lon)
        SEGMENT_POINT_PAIR = search_segment(Coord(busInfo.lat, busInfo.lon), ROUTE.name) # db Segment, Point objects

        CURRENT_SEGMENT = SEGMENT_POINT_PAIR[0] # Segment on which the Bus is on
        CURRENT_POINT = SEGMENT_POINT_PAIR[1]   # The closest assistant-point within a segment

        CURRENT_SEGMENT_INDEX = db.query(models.RouteSegment).filter((models.RouteSegment.segment_id == CURRENT_SEGMENT.id) & (models.RouteSegment.route_id==ROUTE.id)).first().segment_index # Index of the current segment

    except Exception as e1:
        print(f"In Data Initialization: {e1}")

    #=========================================================================================================
    # INITIALIZATION REDIS:
    #=========================================================================================================
    # Set redis keys: Bus and Segment
    R_SEGMENT_NAME = f"segment:{CURRENT_SEGMENT.id}"
    R_BUS_NAME = f"bus:{busInfo.id}"

    # Check bus existence:
    if not r.exists(R_BUS_NAME):
        # If the BUS does NOT EXIST exist in Redis -> initialize new one
        data = {
            "bus_id": busInfo.id,
            "gov_num": BUS.gov_num, # This line may be cause inconsistency with busInfo.id. It's better to use either BUS or busInfo
            "lat": busInfo.lat,
            "lon": busInfo.lon,
            "speed": round(float(busInfo.speed),2),
            "first_modified": str(datetime.now()),
            "last_modified": str(datetime.now()),
            "route": ROUTE.name,
            "last_segment_index": CURRENT_SEGMENT_INDEX,
            "last_segment_name": CURRENT_SEGMENT.street,
            "current_segment_index": CURRENT_SEGMENT_INDEX,
            "current_segment_name": CURRENT_SEGMENT.street
        }

        r.hset(R_BUS_NAME,mapping=data)
        
        segment_flags = [0] * N_SEGMENTS
        bus_stop_flags = [0] * (N_SEGMENTS + 1)

        # Set flags
        r.rpush(f"{R_BUS_NAME}:bus_stop_flags",*bus_stop_flags)
        r.rpush(f"{R_BUS_NAME}:segment_flags", *segment_flags)
        r.lset(f"{R_BUS_NAME}:bus_stop_flags", 0, 1)        # Check this logic later
        r.lset(f"{R_BUS_NAME}:segment_flags", CURRENT_SEGMENT_INDEX, 1)

        # Initialize BusStopClients on every BusStop on the route
        for bs in BUS_STOPS:
            try:
                bsr_index = db.query(models.BusStopRoute).filter((models.BusStopRoute.bus_stop_id==bs.id) & (models.BusStopRoute.route_id==ROUTE.id)).first().bus_stop_index
                r.rpush(f"BusStopClient:{bs.id}:{bs.name}:{ROUTE.name}:{bsr_index}", BUS.gov_num) # Think of storing BUS.id(or consider serializing into json)
            except Exception as e:
                print(f"In Redis Initialization, bus: {e}")  
    else:
        # If the BUS DO EXIST in Redis -> update coordinates, its speed, and received time
        updated_data = {
            "lat": busInfo.lat,
            "lon": busInfo.lon,
            "speed": round(float(busInfo.speed),2),
            "last_modified": str(datetime.now()),
            "current_segment_index": CURRENT_SEGMENT_INDEX,
            "current_segment_name": CURRENT_SEGMENT.street,
            "route": ROUTE.name
        }
        r.hset(R_BUS_NAME, mapping=updated_data)

        # Set flag to the current segment
        r.lset(f"{R_BUS_NAME}:segment_flags", CURRENT_SEGMENT_INDEX, 1)

    
    # Initialize Default Segment ETA values to all of the segments on the route
    for i, segment in enumerate(SEGMENTS):
        # Check segment existence:
        r_segment_name = f"segment:{segment.id}"
        # segment = db.query(models.Segment).filter(models.Segment.id==segment.segment_id).first()
        if not r.exists(r_segment_name):
            if i == 0:
                eta_sum = segment.length/ALLOWED_SPEED
            else:
                eta_sum = float(r.hget(f"segment:{prev_id}", "eta_sum")) + segment.length/ALLOWED_SPEED
            r.hset(r_segment_name, mapping={
                                        "id": segment.id,
                                        "name": segment.street,
                                        "eta": segment.length/ALLOWED_SPEED,
                                        "eta_sum": eta_sum,
                                        "first_modified": str(datetime.now()), 
                                        "last_modified": str(datetime.now()),
                                        "length": segment.length,
                                        "counter": 0})
        prev_id = segment.id

    #=========================================================================================================
    # SEGMENT and BUS ETA UPDATE LOGIC:
    #=========================================================================================================

    # The following part of the code consists of two parts:
    # 1. The Bus is on the BusStop:
    # 2. The Bus is on the Segment

    # NOTE 1: If the Bus on a BusStop -> Update the ETA of the BusStooClient and reset the timer of the Bus
    is_near_bus_stop, bus_stop_obj, bus_stop_route = is_bus_stop(Coord(busInfo.lat, busInfo.lon), ROUTE.name)
    if is_near_bus_stop:
        print(f"Arrived to BusStop: {bus_stop_obj}, {bus_stop_route.bus_stop_index}")
        # If BusStop object is NOT found -> throw error
        if bus_stop_obj is None:
            return {"msg": "Error ocurred while executing is_bus_stop(): bus_stop_obj is 'None'"}
        
        # If the Bus reaches BusStop -> pop Bus from the BusStopClient Queue
        if r.hget(R_BUS_NAME, "current_segment_index") == "24":
            print("Reached the BusStopClient", bus_stop_obj.name)
        
        # QUEUE: bus_stop_id, route_name, bus_stop_index
        bsr_index = db.query(models.BusStopRoute).filter((models.BusStopRoute.bus_stop_id==bus_stop_obj.id) & (models.BusStopRoute.route_id==ROUTE.id)).first().bus_stop_index
        r.lpop(f"BusStopClient:{bus_stop_obj.id}:{bus_stop_obj.name}:{ROUTE.name}:{bsr_index}")
        


        # CASE: Bus Stop Loop 
        # The bus hasn't left the bus stop yet, but another request was made -> eta shouldn't be updated
        # Update only once at first visit

        # If the Bus visits the BusStop the first time-> Calculate the ETA for the previous segment
        if r.lindex(f"{R_BUS_NAME}:bus_stop_flags", int(bus_stop_route.bus_stop_index)) == "0":

            # Pre-calculate average eta
            start_t: datetime = datetime.strptime(r.hget(R_BUS_NAME, "first_modified"), DATETIME_FORMAT)
            delta: float = (datetime.now() - start_t).total_seconds()
            current_eta: float = float(r.hget(R_SEGMENT_NAME, "eta"))
            current_counter: int = int(r.hget(R_SEGMENT_NAME, "counter")) + 1

            avg_eta = ( current_eta + delta ) / current_counter
            # Increse the segment counter by 1
            r.hincrby(R_SEGMENT_NAME, "counter", 1)

            # Modify Redis-Segment:
            try:
                left_segment = None
                right_segment = None

                # Case when the Bus reaches the last BusStop: find left segment
                if bus_stop_route.bus_stop_index == N_SEGMENTS:
                    for segment in SEGMENTS:
                        if segment.end_stop.id == bus_stop_obj.id:
                            left_segment: models.Segment =  segment
                            
                    # Update Redis-Segment on the left
                    r.hset(f"segment:{left_segment.id}", "last_modified", str(datetime.now()))
                    r.hset(f"segment:{left_segment.id}", "eta", avg_eta)

                    left_segment_index = db.query(models.RouteSegment).filter((models.RouteSegment.segment_id == left_segment.
                id) & (models.RouteSegment.route_id==ROUTE.id)).first().segment_index
                    
                    r.hset(R_BUS_NAME, "last_modified", str(datetime.now()))

                    # SET FLAGS
                    r.lset(f"{R_BUS_NAME}:bus_stop_flags", int(bus_stop_route.bus_stop_index), 1)
                    r.lset(f"{R_BUS_NAME}:segment_flags", int(left_segment_index), 1)

                    r.delete(f"bus:{bus_stop_obj.id}")
                else:
                    # Case when the Bus is NOT on the last BusStop: find left and right segments
                    for segment in SEGMENTS:
                        if segment.end_stop.id == bus_stop_obj.id:
                            left_segment: models.Segment = segment
                        elif segment.start_stop.id == bus_stop_obj.id:
                            right_segment: models.Segment = segment
                    # Update segment on the left: consider later the case when the segment might not exist. For example, from bus-stop to bus-stop
                    r.hset(f"segment:{left_segment.id}", "last_modified", str(datetime.now()))
                    r.hset(f"segment:{left_segment.id}", "eta", avg_eta)

                    # Initialize the segment on the right side of the bus stop
                    if not r.exists(f"segment:{right_segment.id}"):
                        r.hset(f"segment:{right_segment.id}", mapping={
                                                    "id": right_segment.id,
                                                    "eta": right_segment.length/ALLOWED_SPEED, 
                                                    "first_modified": str(datetime.now()), 
                                                    "last_modified": str(datetime.now()),
                                                    "length": right_segment.length,
                                                    "counter": 0})
                    

                    # Modify Redis-Bus:
                    right_segment_index = db.query(models.RouteSegment).filter((models.RouteSegment.segment_id == right_segment.
                    id) & (models.RouteSegment.route_id==ROUTE.id)).first().segment_index
                    left_segment_index = db.query(models.RouteSegment).filter((models.RouteSegment.segment_id == left_segment.
                    id) & (models.RouteSegment.route_id==ROUTE.id)).first().segment_index

                    r.hset(R_BUS_NAME, "last_modified", str(datetime.now()))
                    r.hset(R_BUS_NAME, "last_start_segment", right_segment_index)

                    # SET FLAGS
                    r.lset(f"{R_BUS_NAME}:bus_stop_flags", int(bus_stop_route.bus_stop_index), 1)
                    r.lset(f"{R_BUS_NAME}:segment_flags", int(left_segment_index), 1)
                    r.lset(f"{R_BUS_NAME}:segment_flags", int(right_segment_index), 1)
            except Exception as e:
                print(f"In Redis Set Up, bus: {e}")
        if int(r.hget(R_BUS_NAME, "current_segment_index")) == len(SEGMENTS) - 1:
            r.delete(R_BUS_NAME)
            r.delete(R_BUS_NAME+":segment_flags")
            r.delete(R_BUS_NAME+":bus_stop_flags")
    # NOTE 2: If the Bus on a Segment -> Assure Segment Consistency
    else:
        r.hset(R_BUS_NAME, "last_segment_name", CURRENT_SEGMENT.street)

        # CASE: Bus-Stop is skipped -> Update only the CURRENT SEGMENT
        current_segment_index = r.hget(f"{R_BUS_NAME}", "current_segment_index")
        last_segment_index = r.hget(f"{R_BUS_NAME}", "last_segment_index")

        if  current_segment_index != last_segment_index:
            # Pre-calculations -> upadte first_modified and calculate PARTIAL ETA
            current_segment_eta: float = float(r.hget(R_SEGMENT_NAME, "eta"))
            current_segment_length: float = float(r.hget(R_SEGMENT_NAME, "length"))
            length_percentage: float = (CURRENT_POINT.l_sum)/current_segment_length
            jumped_assumption: float = current_segment_eta * length_percentage
            delta_t = timedelta(seconds=jumped_assumption)
            result = datetime.now() - delta_t # maybe "last_modified" instead of datetime.now()?
            
            # MODIFY REDIS BUS:
            r.hset(R_BUS_NAME,"first_modified", str(result))
            r.hset(R_BUS_NAME, "last_segment_index", current_segment_index) # Check this logic later

    #=========================================================================================================
    # RETURN VALUES:
    #=========================================================================================================
    try:
        bus_data = r.hgetall(R_BUS_NAME)
        segment_data = r.hgetall(R_SEGMENT_NAME)
    except Exception as e:
        return {"e": f"{e}"}
    
    return {"message": "success"}