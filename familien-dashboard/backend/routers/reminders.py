from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import get_db

router = APIRouter(prefix="/reminders", tags=["Reminders"])


@router.get("/", response_model=List[schemas.ReminderResponse])
def get_reminders(db: Session = Depends(get_db)):
    return db.query(models.Reminder).order_by(models.Reminder.remind_at).all()


@router.post("/", response_model=schemas.ReminderResponse, status_code=201)
def create_reminder(payload: schemas.ReminderCreate, db: Session = Depends(get_db)):
    reminder = models.Reminder(**payload.model_dump())
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}", status_code=204)
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    reminder = db.get(models.Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder nicht gefunden")
    db.delete(reminder)
    db.commit()
