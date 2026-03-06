import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import httpx
from fastapi import APIRouter

try:
    from dropbox_config import JAALEE_TOKEN
except ImportError:
    JAALEE_TOKEN = ""

router = APIRouter(prefix="/jaalee", tags=["Jaalee"])

JAALEE_URL = "https://sensor.jaalee.com/v1/open/data/all"

# Cache: max 1x pro 70 Sekunden aufrufen
_cache = {"data": [], "ts": 0}

@router.get("/sensors")
async def get_sensors():
    # Gecachte Daten zurückgeben wenn < 70s alt
    if _cache["data"] and (time.time() - _cache["ts"]) < 70:
        return _cache["data"]

    if not JAALEE_TOKEN:
        return _cache["data"]  # leere Liste wenn kein Token

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
    except Exception:
        pass  # Bei Fehler alte Cache-Daten zurückgeben

    return _cache["data"]
