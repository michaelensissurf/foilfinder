import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import init_db
from routers import events, todos, reminders, jaalee

DASHBOARD_DIR = os.path.join(os.path.dirname(__file__), "..")

app = FastAPI(
    title="Familien-Dashboard API",
    version="1.0",
    description="Backend für das Familien-Dashboard – Events, Todos, Reminders",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)
app.include_router(todos.router)
app.include_router(reminders.router)
app.include_router(jaalee.router)


@app.on_event("startup")
async def on_startup():
    import asyncio
    from database import engine
    from sqlalchemy import text

    init_db()

    # Migration: gcal_uid Spalte hinzufügen falls noch nicht vorhanden
    with engine.connect() as conn:
        cols = [r[1] for r in conn.execute(text("PRAGMA table_info(events)")).fetchall()]
        if "gcal_uid" not in cols:
            conn.execute(text("ALTER TABLE events ADD COLUMN gcal_uid VARCHAR(500)"))
            conn.commit()

    async def collect_sensors():
        from routers.jaalee import get_sensors
        await asyncio.sleep(5)
        while True:
            try:
                await get_sensors()
            except Exception:
                pass
            await asyncio.sleep(70)

    async def sync_calendar():
        from routers.gcal import sync_gcal
        await asyncio.sleep(10)  # kurz nach Start
        while True:
            try:
                result = await sync_gcal()
                print(f"[gcal] Sync: {result}")
            except Exception as e:
                print(f"[gcal] Fehler: {e}")
            await asyncio.sleep(15 * 60)  # alle 15 Minuten

    asyncio.create_task(collect_sensors())
    asyncio.create_task(sync_calendar())


@app.post("/gcal/sync", tags=["Kalender"])
async def manual_gcal_sync():
    """Manueller Google Calendar Sync."""
    from routers.gcal import sync_gcal
    return await sync_gcal()


@app.get("/dashboard", tags=["Dashboard"])
def serve_dashboard():
    return FileResponse(os.path.join(DASHBOARD_DIR, "design_preview.html"))

app.mount("/assets", StaticFiles(directory=os.path.join(DASHBOARD_DIR, "assets")), name="assets")

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "app": "Familien-Dashboard API"}


# uvicorn main:app --reload --port 8000
