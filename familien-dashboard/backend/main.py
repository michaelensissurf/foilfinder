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
    init_db()

    async def collect_sensors():
        """Alle 70s Sensordaten holen und in DB speichern."""
        from routers.jaalee import get_sensors
        await asyncio.sleep(5)  # kurz warten bis alles bereit ist
        while True:
            try:
                await get_sensors()
            except Exception:
                pass
            await asyncio.sleep(70)

    asyncio.create_task(collect_sensors())


@app.get("/dashboard", tags=["Dashboard"])
def serve_dashboard():
    return FileResponse(os.path.join(DASHBOARD_DIR, "design_preview.html"))

app.mount("/assets", StaticFiles(directory=os.path.join(DASHBOARD_DIR, "assets")), name="assets")

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "app": "Familien-Dashboard API"}


# uvicorn main:app --reload --port 8000
