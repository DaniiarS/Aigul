from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

import app.db.database as database
from app.db.redis_client import r
from app.api.endpoints import bus, bus_stop, route, segment, map

app = FastAPI()
scheduler = BackgroundScheduler()

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
database.Base.metadata.create_all(database.Engine)

#==========================================================================================
# Start Page
#==========================================================================================

# @app.on_event("startup")
# def set_table():
#     r.rpush("BusStopClient:23:7:24",)

@app.get("/")
def home():
    return {"200": "Welcome! Wish a good start!"}