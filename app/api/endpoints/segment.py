from app.db import models
from app.api.schemas import schema
from app.db.database import get_db

from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/{segment_id}", response_model=schema.Segment, response_class=JSONResponse)
def get_segment(segment_id: int, db: Session = Depends(get_db)):
    segment = db.query(models.Segment).filter(models.Segment.segment_id == segment_id).first()
    if segment is None:
        raise HTTPException(status_code=404, detail="Segment is not found")
    segment_data = schema.Segment.from_orm(segment).dict()
    return JSONResponse(content=segment_data, media_type="application/json; charset=utf-8")

@router.post("/")
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