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

async def sanitizer():
    bus_stop_id = 23
    db = SessionLocal()
    while True:
        try:
            print(f"[{datetime.datetime.now()}] Running periodic task...")
            BusStopClient = db.query(models.BusStop).filter(models.BusStop.id==bus_stop_id).first()
            # print((f"BusStopClient:{BusStopClient.routes}"))
            if r.exists(f"BusStopClient:{BusStopClient.id}:{BusStopClient.name}:14T:15"):
                print("Hello")
        except Exception as e:
            print(f"Error in sanitor: {e}")
        finally:
            db.close()
        await asyncio.sleep(2)

@app.on_event("startup")
def set_table():
    print("Server started")
    asyncio.create_task(sanitizer)

@app.get("/")
def home():
    return {"200": "Welcome! Wish a good start!"}