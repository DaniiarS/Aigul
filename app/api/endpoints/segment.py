from app.db import models
from app.api.schemas import schema
from app.db.database import get_db
from app.utils.eta import search_segment, is_bus_stop, update_ETA
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
            await ws.send_json({"lat": busInfo.lat, "lon": busInfo.lon})
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

#==================================================================================================
# POST endpoints: get_segmnet()
#==================================================================================================

@router.post("/update-segment-eta")
def eta(busInfo: schema.BusInfo, db: Session = Depends(get_db)):

    #=====================================================================
    # PRE-INITIALIZATION REDIS:
    #=====================================================================
    ALLOWED_SPEED = 40 * 1000 / 3600
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f"

    """ GET DATA for INITIALIZATION """
    try:
        route_name = db.query(models.Bus).filter(models.Bus.bus_id==busInfo.id).first().route_name # "7"
        ROUTE = db.query(models.Route).filter(models.Route.route_name==route_name).first() # db Route Object
        ROUTE_SIZE = len(db.query(models.RouteSegment).filter(models.RouteSegment.route_id==ROUTE.route_id).all()) # 40
        SEGMENT_POINT_PAIR = search_segment(Coord(busInfo.lat, busInfo.lon), route_name) # db Segment, Point objects
        SEGMENT = SEGMENT_POINT_PAIR[0]
        ASSISTANT_POINT = SEGMENT_POINT_PAIR[1]
        SEGMENT_INDEX = db.query(models.RouteSegment).filter((models.RouteSegment.segment_id == SEGMENT.segment_id) & (models.RouteSegment.route_id==ROUTE.route_id)).first().segment_index # 3
    except Exception as e1:
        print(f"{e1}")

    #=====================================================================
    # INITIALIZATION REDIS:
    #=====================================================================
    # set redis keys: Bus and Segment
    R_SEGMENT_NAME = f"segment:{SEGMENT.segment_id}"
    R_BUS_NAME = f"bus:{busInfo.id}"

    # check bus existence:
    if not r.exists(R_BUS_NAME):
        # If the BUS does NOT EXIST exist in Redis -> initialize new one
        data = {
            "bus_id": busInfo.id,
            "lat": busInfo.lat,
            "lon": busInfo.lon,
            "speed": round(float(busInfo.speed),2),
            "first_modified": str(datetime.now()),
            "last_modified": str(datetime.now()),
            "route": ROUTE.route_name,
            "last_segment_index": SEGMENT_INDEX,
            "last_segment_name": SEGMENT.segment_street,
            "current_segment_index": SEGMENT_INDEX,
            "current_segment_name": SEGMENT.segment_street
        }
        
        flags = [0] * ROUTE_SIZE
        r.hset(R_BUS_NAME,mapping=data)
        r.rpush(f"{R_BUS_NAME}:bus_stop_flags",*flags)
        r.rpush(f"{R_BUS_NAME}:segment_flags", *flags)
        r.lset(f"{R_BUS_NAME}:bus_stop_flags", 0, 1)        # Check this logic later
        r.lset(f"{R_BUS_NAME}:segment_flags", SEGMENT_INDEX, 1)
    else:
        # If the BUS DO EXIST in Redis -> update coordinates, its speed, and received time
        updated_data = {
            "lat": busInfo.lat,
            "lon": busInfo.lon,
            "speed": round(float(busInfo.speed),2),
            "last_modified": str(datetime.now()),
            "current_segment_index": SEGMENT_INDEX,
            "current_segment_name": SEGMENT.segment_street,
            "route": ROUTE.route_name
        }
        r.hset(R_BUS_NAME, mapping=updated_data)
        r.lset(f"{R_BUS_NAME}:segment_flags", SEGMENT_INDEX, 1)

    # check segment existence:
    if not r.exists(R_SEGMENT_NAME):
        r.hset(R_SEGMENT_NAME, mapping={
                                    "id": SEGMENT.segment_id,
                                    "name": SEGMENT.segment_street,
                                    "eta": SEGMENT.segment_length/ALLOWED_SPEED, 
                                    "first_modified": str(datetime.now()), 
                                    "last_modified": str(datetime.now()),
                                    "length": SEGMENT.segment_length,
                                    "counter": 0})

    #=====================================================================
    # SEGMENT and BUS ETA UPDATE LOGIC:
    #=====================================================================
    is_near_bus_stop, bus_stop_obj, bus_stop_route = is_bus_stop(Coord(busInfo.lat, busInfo.lon), ROUTE.route_name)
    # NOTE 1: on a bus stop -> Update the ETA of the bus stop and reset the timer
    if is_near_bus_stop: 
        # BusStop: models.BusStop object is NOT found -> throw error
        if bus_stop_obj is None:
            return {"msg": "Error ocurred while executing is_bus_stop(): bus_stop_obj is 'None'"}
        
        # CASE: Bus Stop Loop 
        # The bus hasn't left the bus stop yet, but another request was made -> eta shouldn't be updated
        # Update only once at first visit
        if r.lindex(f"{R_BUS_NAME}:bus_stop_flags", int(bus_stop_route.bus_stop_index)) == "0":
            # PRE-CALCULATE AVG_ETA
            start_t: datetime = datetime.strptime(r.hget(R_BUS_NAME, "first_modified"), DATETIME_FORMAT)
            delta: float = (datetime.now() - start_t).total_seconds()
            current_eta: float = float(r.hget(R_SEGMENT_NAME, "eta"))
            current_counter: int = int(r.hget(R_SEGMENT_NAME, "counter")) + 1

            avg_eta = ( current_eta + delta ) / current_counter
            r.hincrby(R_SEGMENT_NAME, "counter", 1)

            # MODIFY REDIS SEGMENT: I guess it is better to make search one more time and get the left and rigth segments
            try:
                left_segment = None
                right_segment = None
                segment_objs: models.Segment = db.query(models.Segment).all()
                
                # OPTIMIZE: Later think about searching in Route_Segment
                for segment_obj in segment_objs:
                    print(segment_obj)
                    if (segment_obj.lat_b == str(bus_stop_obj.lat)) and (segment_obj.lon_b == str(bus_stop_obj.lon)):
                        left_segment: models.Segment =  segment_obj
                    elif (segment_obj.lat_a == str(bus_stop_obj.lat)) and (segment_obj.lon_a == str(bus_stop_obj.lon)):
                        right_segment: models.Segment = segment_obj

                # print(bus_stop_obj)
                # print(left_segment, right_segment)

                # update segment on the left: consider later the case when the segment might not exist. For example, from bus-stop to bus-stop
                r.hset(f"segment:{left_segment.segment_id}", "last_modified", str(datetime.now()))
                r.hset(f"segment:{left_segment.segment_id}", "eta", avg_eta)
                # initialize the segment on the right side of the bus stop
                if not r.exists(f"segment:{right_segment.segment_id}"):
                    r.hset(f"segment:{right_segment.segment_id}", mapping={
                                                "id": right_segment.segment_id,
                                                "eta": right_segment.segment_length/ALLOWED_SPEED, 
                                                "first_modified": str(datetime.now()), 
                                                "last_modified": str(datetime.now()),
                                                "length": right_segment.segment_length,
                                                "counter": 0})
                

                # MODIFY REDIS BUS:
                right_segment_index = db.query(models.RouteSegment).filter((models.RouteSegment.segment_id == right_segment.
                segment_id) & (models.RouteSegment.route_id==ROUTE.route_id)).first().segment_index
                left_segment_index = db.query(models.RouteSegment).filter((models.RouteSegment.segment_id == left_segment.
                segment_id) & (models.RouteSegment.route_id==ROUTE.route_id)).first().segment_index

                r.hset(R_BUS_NAME, "last_modified", str(datetime.now()))
                r.hset(R_BUS_NAME, "last_start_segment", right_segment_index)

                # SET FLAGS
                r.lset(f"{R_BUS_NAME}:bus_stop_flags", int(bus_stop_route.bus_stop_index), 1)
                r.lset(f"{R_BUS_NAME}:segment_flags", int(left_segment_index), 1)
                r.lset(f"{R_BUS_NAME}:segment_flags", int(right_segment_index), 1)
            except Exception as e:
                return {f"{e}"}
    # NOTE 2: on a segment -> Assure Segment Consistency
    else:
        current_segment_index = r.hget(f"{R_BUS_NAME}", "current_segment_index")
        last_segment_index = r.hget(f"{R_BUS_NAME}", "last_segment_index")
        r.hset(R_BUS_NAME, "last_segment_name", SEGMENT.segment_street)

        # CASE: Bus-Stop is skipped -> Update only the CURRENT SEGMENT
        if  current_segment_index != last_segment_index:
            # PRE-CALCULATIONS -> upadte first_modified and calculate PARTIAL ETA
            current_segment_eta: float = float(r.hget(R_SEGMENT_NAME, "eta"))
            current_segment_length: float = float(r.hget(R_SEGMENT_NAME, "length"))
            length_percentage: float = (ASSISTANT_POINT.l_sum)/current_segment_length
            jumped_assumption: float = current_segment_eta * length_percentage
            delta_t = timedelta(seconds=jumped_assumption)
            result = datetime.now() - delta_t # maybe "last_modified" instead of datetime.now()?
            
            # MODIFY REDIS BUS:
            r.hset(R_BUS_NAME,"first_modified", str(result))
            r.hset(R_BUS_NAME, "last_segment_index", current_segment_index) # Check this logic later

    #=====================================================================
    # RETURN VALUES:
    #=====================================================================
    try:
        bus_data = r.hgetall(R_BUS_NAME)
        segment_data = r.hgetall(R_SEGMENT_NAME)
    except Exception as e:
        return {"e": f"{e}"}
    
    return (bus_data, segment_data)