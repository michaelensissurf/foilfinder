from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

import models
import schemas
from database import get_db

router = APIRouter(prefix="/todos", tags=["Todos"])


@router.get("/", response_model=List[schemas.TodoResponse])
def get_todos(list: Optional[str] = None, db: Session = Depends(get_db)):
    """Alle Todos laden. Optionaler Filter: ?list=Einkauf"""
    query = db.query(models.Todo)
    if list:
        query = query.filter(models.Todo.list_name == list)
    return query.order_by(models.Todo.created_at.desc()).all()


@router.get("/{todo_id}", response_model=schemas.TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(models.Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo nicht gefunden")
    return todo


@router.post("/", response_model=schemas.TodoResponse, status_code=201)
def create_todo(payload: schemas.TodoCreate, db: Session = Depends(get_db)):
    todo = models.Todo(**payload.model_dump())
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.put("/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, payload: schemas.TodoUpdate, db: Session = Depends(get_db)):
    todo = db.get(models.Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo nicht gefunden")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo


@router.put("/{todo_id}/done", response_model=schemas.TodoResponse)
def toggle_done(todo_id: int, db: Session = Depends(get_db)):
    """Erledigt-Status umschalten"""
    todo = db.get(models.Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo nicht gefunden")
    todo.done = not todo.done
    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(models.Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo nicht gefunden")
    db.delete(todo)
    db.commit()
