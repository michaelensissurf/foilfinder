import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import httpx
from fastapi import APIRouter
from sqlalchemy.orm import Session
from database import SessionLocal
from models import SensorReading

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    from dropbox_config import JAALEE_TOKEN
except ImportError:
    JAALEE_TOKEN = ""

router   = APIRouter(prefix="/jaalee", tags=["Jaalee"])
JAALEE_URL = "https://sensor.jaalee.com/v1/open/data/all"

_cache = {"data": [], "ts": 0}


def _save_readings(sensors: list):
    """Aktuelle Messwerte in lokale DB schreiben (max 1x pro 60s pro Sensor)."""
    now_ms = int(time.time() * 1000)
    cutoff = now_ms - 65_000  # nicht doppelt speichern
    db: Session = SessionLocal()
    try:
        for s in sensors:
            mac = s["mac"]
            last = (db.query(SensorReading)
                    .filter(SensorReading.mac == mac,
                            SensorReading.created_at >= cutoff)
                    .first())
            if last:
                continue  # bereits gespeichert in den letzten 65s
            db.add(SensorReading(
                mac=mac,
                temperature=s["temperature"],
                humidity=s["humidity"],
                created_at=now_ms,
            ))
        db.commit()
    finally:
        db.close()


@router.get("/sensors")
async def get_sensors():
    if _cache["data"] and (time.time() - _cache["ts"]) < 70:
        return _cache["data"]
    if not JAALEE_TOKEN:
        return _cache["data"]
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(JAALEE_URL, headers={"Authorization": JAALEE_TOKEN})
        data = r.json()
        if data.get("code") == 0:
            sensors = []
            for d in data.get("data", []):
                sensors.append({
                    "name":        d.get("alias", d.get("mac", "Sensor")),
                    "mac":         d.get("mac"),
                    "temperature": round(d.get("temperature", 0), 1),
                    "humidity":    round(d.get("humidity", 0), 1),
                    "power":       d.get("power"),
                    "updated":     d.get("time"),
                })
            _cache["data"] = sensors
            _cache["ts"]   = time.time()
            _save_readings(sensors)  # In DB speichern
    except Exception:
        pass
    return _cache["data"]


@router.get("/history")
async def get_history(mac: str, days: int = 7):
    cutoff_ms = int((time.time() - days * 86400) * 1000)
    db: Session = SessionLocal()
    try:
        rows = (db.query(SensorReading)
                .filter(SensorReading.mac == mac,
                        SensorReading.created_at >= cutoff_ms)
                .order_by(SensorReading.created_at)
                .all())
        return [{"t": r.created_at, "temp": r.temperature, "hum": r.humidity}
                for r in rows]
    finally:
        db.close()
