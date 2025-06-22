# ================================================================
# Define Actual database tables here
# Used for validation when doing requests and sending responses
# ================================================================

from app.db.database import Base
from sqlalchemy import Column
from sqlalchemy import Integer, String, Float, Boolean
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship



# ====================================================
# Table definitions: Bus, Route, Bus_Stop, Segment
# ====================================================

class Bus(Base):
    __tablename__ = "bus"

    id = Column(Integer, primary_key=True, index=True)
    gov_num = Column(String, index=True)    # Example: 01-123-ABC

    route_name = Column(String, ForeignKey("route.name"))

    route = relationship("Route", back_populates="buses")
    bus_stops = relationship("BusStop", secondary="bus_stop_bus", back_populates="buses")
    

class Route(Base): # Done
    __tablename__ = "route"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    type = Column(String, index=True)

    buses = relationship("Bus", back_populates="route")

    bus_stops = relationship("BusStop", secondary="bus_stop_route", back_populates="routes")
    segments = relationship("Segment", secondary="route_segment", back_populates="routes")

    def __repr__(self):
        return f"type: {type(self)}, id:{self.id}, name:{self.name}"

class BusStop(Base): # Done
    __tablename__ = "bus_stop"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    lon = Column(String)
    lat = Column(String)

    routes = relationship("Route", secondary="bus_stop_route", back_populates="bus_stops")
    buses = relationship("Bus", secondary="bus_stop_bus", back_populates="bus_stops")

    def __repr__(self):
        return f"name:{self.name} lat:{self.lat} lon:{self.lon}"

class Segment(Base):
    __tablename__ = "segment"
    __table_args__ = (
        UniqueConstraint("bus_stop_a", "bus_stop_b", name="unique_bus_stop_a_bus_stop_b"),
    )

    id = Column(Integer, primary_key=True, index=True)
    length = Column(Float)
    street = Column(String, default="N/A")
    bus_stop_a = Column(Integer, ForeignKey("bus_stop.id"), nullable=False)
    bus_stop_b = Column(Integer, ForeignKey("bus_stop.id"), nullable=False)


    # Relationships for convenient access (optional)
    start_stop = relationship("BusStop", foreign_keys=[bus_stop_a])
    end_stop = relationship("BusStop", foreign_keys=[bus_stop_b])

    routes = relationship("Route", secondary="route_segment", back_populates="segments")

    def __repr__(self):
        return f"Segment id:{self.id},\tSegment street:{self.street},\tSegment distance:{self.length},\ta:{self.bus_stop_a},\tb:{self.bus_stop_b}"

class Point(Base):
    __tablename__ = "point"
    # __table_args__ = (
    #     UniqueConstraint("route_name", "point_index", "segment_index", name="unique_route_name_point_index_segment_index"),
    # )

    id = Column(Integer, primary_key=True, index=True)
    lat = Column(String)
    lon = Column(String)
    l_delta = Column(Float)
    l_sum = Column(Float)
    index = Column(Integer)
    segment_id = Column(Integer, ForeignKey("segment.id"), nullable=False)

    def __repr__(self):
        return f"lat:{self.lat}, lon:{self.lon}, l_delta:{self.l_delta}, l_sum:{self.l_sum}, index:{self.index}, segment_id:{self.segment_id}"
# ====================================================
# Assocciation Tables: Many-to-Many Relationships
# ====================================================

class BusStopRoute(Base):
    __tablename__ = "bus_stop_route"

    id = Column(Integer, primary_key=True, index=True)
    bus_stop_id = Column(Integer, ForeignKey("bus_stop.id"))
    route_id = Column(Integer, ForeignKey("route.id"))
    bus_stop_index = Column(Integer, autoincrement=True)

class BusStopBus(Base):
    __tablename__ = "bus_stop_bus"

    id = Column(Integer, primary_key=True, index=True)
    bus_stop_id = Column(Integer, ForeignKey("bus_stop.id"))
    bus_id = Column(Integer, ForeignKey("bus.id"))

class RouteSegment(Base):
    __tablename__ = "route_segment"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("route.id"))
    segment_id = Column(Integer, ForeignKey("segment.id"))
    segment_index = Column(Integer)