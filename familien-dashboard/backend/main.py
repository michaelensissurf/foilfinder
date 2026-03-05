from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers import events, todos, reminders

app = FastAPI(
    title="Familien-Dashboard API",
    version="1.0",
    description="Backend für das Familien-Dashboard – Events, Todos, Reminders",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React (CRA)
        "http://localhost:5173",   # React (Vite)
        "http://localhost:8080",   # Allgemein
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)
app.include_router(todos.router)
app.include_router(reminders.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "app": "Familien-Dashboard API"}


# uvicorn main:app --reload --port 8000
