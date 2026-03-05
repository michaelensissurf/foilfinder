from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# ── EVENT ──────────────────────────────────────────────────────────────────────

class EventBase(BaseModel):
    title:          str
    description:    Optional[str] = None
    start_datetime: datetime
    end_datetime:   Optional[datetime] = None
    person:         str = "family"
    color:          str = "#6366f1"
    all_day:        bool = False


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title:          Optional[str]      = None
    description:    Optional[str]      = None
    start_datetime: Optional[datetime] = None
    end_datetime:   Optional[datetime] = None
    person:         Optional[str]      = None
    color:          Optional[str]      = None
    all_day:        Optional[bool]     = None


class EventResponse(EventBase):
    model_config = ConfigDict(from_attributes=True)
    id:         int
    created_at: Optional[datetime] = None


# ── TODO ───────────────────────────────────────────────────────────────────────

class TodoBase(BaseModel):
    text:      str
    person:    str = "family"
    list_name: str = "Einkauf"
    due_date:  Optional[datetime] = None


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    text:      Optional[str]      = None
    person:    Optional[str]      = None
    list_name: Optional[str]      = None
    due_date:  Optional[datetime] = None
    done:      Optional[bool]     = None


class TodoResponse(TodoBase):
    model_config = ConfigDict(from_attributes=True)
    id:         int
    done:       bool
    created_at: Optional[datetime] = None


# ── REMINDER ───────────────────────────────────────────────────────────────────

class ReminderBase(BaseModel):
    title:     str
    remind_at: datetime
    event_id:  Optional[int] = None
    todo_id:   Optional[int] = None


class ReminderCreate(ReminderBase):
    pass


class ReminderResponse(ReminderBase):
    model_config = ConfigDict(from_attributes=True)
    id:   int
    sent: bool
