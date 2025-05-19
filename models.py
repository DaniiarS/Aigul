# ================================================================
# Define Actual database tables here
# Used for validation when doing requests and sending responses
# ================================================================

from database import Base
from sqlalchemy import Column
from sqlalchemy import Integer, String, Float, Boolean
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship



# ====================================================
# Table definitions: Bus, Route, Bus_Stop, Segment
# ====================================================

class Bus(Base):
    __tablename__ = "bus"

    bus_id = Column(Integer, primary_key=True, index=True)
    bus_lng = Column(Float)  # 5.123769843    
    bus_lat = Column(Float)  # 4.123123123
    bus_gov_num = Column(String, index=True)    # Example: 01-123-ABC
    bus_current_segment = Column(Integer)      # id of the current segment

    route_name = Column(String, ForeignKey("route.route_name"))

    route = relationship("Route", back_populates="buses")
    bus_stops = relationship("BusStop", secondary="bus_stop_bus", back_populates="buses")
    

class Route(Base):
    __tablename__ = "route"

    route_id = Column(Integer, primary_key=True, index=True)
    route_name = Column(String, index=True, unique=True)
    route_type = Column(String, index=True)

    buses = relationship("Bus", back_populates="route")
    bus_stops = relationship("BusStop", secondary="bus_stop_route", back_populates="routes")
    segments = relationship("Segment", secondary="route_segment", back_populates="routes")


class BusStop(Base):
    __tablename__ = "bus_stop"

    bus_stop_id = Column(Integer, primary_key=True, index=True)
    bus_stop_name = Column(String, index=True)
    bus_stop_addr = Column(String, index=True)
    bus_stop_lng = Column(Float)
    bus_stop_lat = Column(Float)

    routes = relationship("Route", secondary="bus_stop_route", back_populates="bus_stops")
    buses = relationship("Bus", secondary="bus_stop_bus", back_populates="bus_stops")

class Segment(Base):
    __tablename__ = "segment"
    __table_args__ = (
        UniqueConstraint("segment_bus_stop_a", "segment_bus_stop_b", name="unique_segment_bus_stop_a_segment_bus_stop_b"),
    )

    segment_id = Column(Integer, primary_key=True, index=True)
    segment_length = Column(Float)
    segment_street = Column(String, default="N/A")
    segment_bus_stop_a = Column(String(50))
    segment_bus_stop_b = Column(String(50))
    segment_eta = Column(Float,default=0.0)


    routes = relationship("Route", secondary="route_segment", back_populates="segments")

    def __repr__(self):
        return f"Segment id:{self.segment_id},\tSegment street:{self.segment_street},\tSegment distance:{self.segment_length}"

class Point(Base):
    __tablename__ = "point"
    __table_args__ = (
        UniqueConstraint("route_name", "point_index", "segment_index", name="unique_route_name_point_index_segment_index"),
    )

    point_id = Column(Integer, primary_key=True, index=True)
    route_name = Column(String, index=True)
    longitude = Column(Float)
    latitude = Column(Float)
    point_index = Column(Integer)
    segment_index = Column(Integer)

# ====================================================
# Assocciation Tables: Many-to-Many Relationships
# ====================================================

class BusStopRoute(Base):
    __tablename__ = "bus_stop_route"

    bus_stop_route_id = Column(Integer, primary_key=True, index=True)
    bus_stop_id = Column(Integer, ForeignKey("bus_stop.bus_stop_id"))
    route_id = Column(Integer, ForeignKey("route.route_id"))
    bus_stop_index = Column(Integer, autoincrement=True)

class BusStopBus(Base):
    __tablename__ = "bus_stop_bus"

    bus_stop_bus_id = Column(Integer, primary_key=True, index=True)
    bus_stop_id = Column(Integer, ForeignKey("bus_stop.bus_stop_id"))
    bus_id = Column(Integer, ForeignKey("bus.bus_id"))

class RouteSegment(Base):
    __tablename__ = "route_segment"

    route_segment_id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("route.route_id"))
    segment_id = Column(Integer, ForeignKey("segment.segment_id"))
    segment_index = Column(Integer)