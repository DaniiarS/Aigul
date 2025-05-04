# ================================================================
# Define Schemas here using Pydantic
# Used for validation when doing requests and sending responses
# ================================================================

from pydantic import BaseModel
from typing import Optional

class Bus(BaseModel):
    bus_lng: Optional[float] = None
    bus_lat: Optional[float] = None
    route_name: str
    bus_gov_num: str
    bus_current_segment: Optional[int] = 10

class Route(BaseModel):
    route_name: str

class BusStop(BaseModel):
    bus_stop_name: str
    bus_stop_addr: str
    bus_stop_lng: float
    bus_stop_lat: float

class Segment(BaseModel):
    segment_length: float
    segment_speed: float
    segment_street: str
    segment_bus_stop_a: int
    segment_bus_stop_b: int
    segment_bidirectional: Optional[bool] = None
    segment_eta: float = 0