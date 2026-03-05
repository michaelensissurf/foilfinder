from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func
from database import Base


class Event(Base):
    __tablename__ = "events"

    id             = Column(Integer, primary_key=True, index=True)
    title          = Column(String(200), nullable=False)
    description    = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime   = Column(DateTime, nullable=True)
    person         = Column(String(20), default="family")  # mama | papa | kind | family
    color          = Column(String(10), default="#6366f1")
    all_day        = Column(Boolean, default=False)
    created_at     = Column(DateTime, server_default=func.now())


class Todo(Base):
    __tablename__ = "todos"

    id         = Column(Integer, primary_key=True, index=True)
    text       = Column(String(500), nullable=False)
    done       = Column(Boolean, default=False)
    person     = Column(String(20), default="family")  # mama | papa | kind | family
    list_name  = Column(String(50), default="Einkauf")  # Einkauf | Haushalt | Erledigung
    due_date   = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class Reminder(Base):
    __tablename__ = "reminders"

    id        = Column(Integer, primary_key=True, index=True)
    title     = Column(String(200), nullable=False)
    remind_at = Column(DateTime, nullable=False)
    event_id  = Column(Integer, ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    todo_id   = Column(Integer, ForeignKey("todos.id",  ondelete="SET NULL"), nullable=True)
    sent      = Column(Boolean, default=False)
