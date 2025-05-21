from fastapi.responses import FileResponse
from fastapi import APIRouter

router = APIRouter()

@router.get("/route/{route_id}")
def get_map(route_id: str):
    return FileResponse(f"app/data/bus_stops/{route_id}/bus_stops_map_{route_id}.html")

@router.get("/segment/{route_id}")
def get_segment_map(route_id: int):
    return FileResponse(f"app/data/segments/{route_id}/map_linestrings_{route_id}.html")