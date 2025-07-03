from fastapi import FastAPI
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from sqlalchemy.orm import Session

import datetime
import time
import asyncio

import app.db.database as database
from app.db import models
from app.db.database import SessionLocal
from app.db.redis_client import r
from app.api.endpoints import bus, bus_stop, route, segment, map

app = FastAPI()
scheduler = BackgroundScheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow POST, OPTIONS, etc.
    allow_headers=["*"],  # Allow custom headers like Content-Type
)



# =========================================================================================
# GET and POST End-Points: bus_stop, bus, route, segment. Please refer to app/api/endpoints
# =========================================================================================
app.include_router(bus.router, prefix="/bus", tags=["Bus"])
app.include_router(bus_stop.router, prefix="/bus_stop", tags=["BusStop"])
app.include_router(route.router, prefix="/route", tags=["Route"])
app.include_router(segment.router, prefix="/segment", tags=["Segment"])
app.include_router(map.router, prefix="/map", tags=["Map"])

# When creating the database it is important to import Base from the "models.py" and not from the "database.py" directly
# Since if we do not import the Base from the "models.py" the classes defined there inheriting from the Base, are not registered in
# the Base's metadata, and, therefore calling database.Base.metadata.create_all(database.Engine) will not create tables in the database,
# because, it does not know about any tables defined using the Base
# And we are calling this function here, because it does not re-create the table if it already exist.
# If one wants to re-create the table, then use -> Base.metadata.drop_all(Engine)
# In the future, when the application is ready fo the production -> use Alembic, which is a "git" of databases
database.Base.metadata.create_all(database.Engine)  # TODO: replace with Alembic

#==========================================================================================
# Start Page
#==========================================================================================

def printl(array: list):
    for obj in array:
        print(obj)

def pop_all_routes(ROUTE: str):
    pass

async def sanitizer():
    db = SessionLocal()
    bus_stop_routes: models.BusStop = db.query(models.BusStopRoute).all()
    db.close()

    while True:

        bus_stops = [bsr.bus_stop_id for bsr in bus_stop_routes]
        printl(bus_stops)
        for bus_stop_id in bus_stops:

            pattern = f"BusStopClient:{bus_stop_id}:*"
            try:
                print(f"[{datetime.datetime.now()}] Running periodic task...")            
                # Find all redis-keys that match the pattern
                keys = list(r.scan_iter(pattern))
                print(keys)
                # for key in keys: iterates through each route in BusStopClient(same as for route in routes)
                for key in keys:
                    if key:
                        if r.exists(key):
                            # Using the gov_num of the Bus find its id
                            db = SessionLocal()
                            gov_num = r.lindex(key, 0)
                            Bus: models.Bus = db.query(models.Bus).filter(models.Bus.gov_num==gov_num).first()
                            bus_id: int  = Bus.id
                            db.close()
                            # get the current segment index and compare it with BusStopClient index
                            if r.exists(f"bus:{bus_id}"):
                                bus_index, bus_stop_index = int(r.hget(f"bus:{bus_id}", "current_segment_index")), int(key.split(":")[-1])
                                delta = bus_stop_index - bus_index

                                if delta < 0:
                                    r.lpop(key)
                            else: # If bus doesn't exist
                                r.lpop(key)
            except Exception as e:
                print(f"Error in sanitor: {e}")
            finally:
                db.close()
        await asyncio.sleep(5)

@app.on_event("startup")
def set_table():
    print("Server started")
    asyncio.create_task(sanitizer())

@app.get("/")
def home():
    return {"200": "Welcome! Wish a good start!"}