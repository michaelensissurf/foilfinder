from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

import models
import schemas
from database import get_db

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/", response_model=List[schemas.EventResponse])
def get_events(date: Optional[str] = None, db: Session = Depends(get_db)):
    """Alle Events laden. Optionaler Filter: ?date=2026-03 (Jahr-Monat)"""
    query = db.query(models.Event)
    if date:
        try:
            year, month = int(date[:4]), int(date[5:7])
            from sqlalchemy import extract
            query = query.filter(
                extract("year",  models.Event.start_datetime) == year,
                extract("month", models.Event.start_datetime) == month,
            )
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="date muss im Format YYYY-MM sein")
    return query.order_by(models.Event.start_datetime).all()


@router.get("/{event_id}", response_model=schemas.EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event nicht gefunden")
    return event


@router.post("/", response_model=schemas.EventResponse, status_code=201)
def create_event(payload: schemas.EventCreate, db: Session = Depends(get_db)):
    event = models.Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.put("/{event_id}", response_model=schemas.EventResponse)
def update_event(event_id: int, payload: schemas.EventUpdate, db: Session = Depends(get_db)):
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event nicht gefunden")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event nicht gefunden")
    db.delete(event)
    db.commit()
