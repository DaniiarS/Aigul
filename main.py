from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
# import schema # from this folder import schema
import schema, database, models
from sqlalchemy.orm import Session

app = FastAPI()

# When creating the database it is important to import Base from the "models.py" and not from the "database.py" directly
# Since if we do not import the Base from the "models.py" the classes defined there inheriting from the Base, are not registered in
# the Base's metadata, and, therefore calling database.Base.metadata.create_all(database.Engine) will not create tables in the database,
# because, it does not know about any tables defined using the Base
# And we are calling this function here, because it does not re-create the table if it already exist.
# If one wants to re-create the table, then use -> Base.metadata.drop_all(Engine)
# In the future, when the application is ready fo the production -> use Alembic, which is a "git" of databases
models.Base.metadata.create_all(database.Engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================================================
# GET End-Points: Home, bus_stop, bus, route, segment
# =========================================================

@app.get("/")
def home():
    return {"message": "Welcome! Wish a good start!"}

@app.get("/map/{route_id}")
def get_map(route_id: str):
    return FileResponse(f"data/bus_stops/{route_id}/bus_stops_map_{route_id}.html")

@app.get("/bus_stop/{bus_stop_id}")
def get_bus_stop(bus_stop_id: int, db: Session = Depends(get_db)):
    try:
        return db.query(models.BusStop).filter(models.BusStop.id == bus_stop_id)
    except:
        return {"message": "objest is not found"}

@app.get("/route/{route_id}")
def get_route(route_id: int, db: Session = Depends(get_db)):
    try:
        return db.query(models.Route).filter(models.Route.route_id == route_id).all()
    except:
        return {"message": "object is not found"}

@app.get("/bus/{bus_id}")
def get_bus(bus_id: int, db: Session = Depends(get_db)):
    try:
        return db.query(models.Bus).filter(models.Bus.bus_id == bus_id).all()
    except:
        return {"message": "object is not found"}

@app.get("/segment/{segement_id}")
def get_segment(segment_id: int, db: Session = Depends(get_db)):
    try:
        db.query(models.Segment).filter(models.Segment.segment_id == segment_id).all()
    except:
        return {"message": "object is not found"}

# =========================================================
# POST End-Points: Route, Segment, Bus, Bus_Stop
# =========================================================

@app.post("/route")
def create_route(route: schema.Route, db: Session = Depends(get_db)):

    # new_route = models.Route(
    #     route_name = route.route_name,
    #     bus_stops = [bs_1, bs_2]
    # )

    # db.add_all([new_route, bs_1, bs_2])
    # db.commit()
    # db.refresh(new_route)

    return {"message": "Route added successfully"}

@app.post("/bus_stop")
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

@app.post("/segment")
def create_segment(segment: schema.Segment, db: Session = Depends(get_db)):
    new_segment = models.Segment(
        segment_length = segment.segment_length,
        segment_speed = segment.segment_speed,
        segment_street = segment.segment_street,
        segment_bus_stop_a = segment.segment_bus_stop_a,
        segment_bus_stop_b = segment.segment_bus_stop_b,
        segment_bidirectional = segment.segment_bidirectional,
        segment_eta = segment.segment_eta
    )

    db.add(new_segment)
    db.commit()
    db.refresh(new_segment)

    return new_segment

@app.post("/bus")
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