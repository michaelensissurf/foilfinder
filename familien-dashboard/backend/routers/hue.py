import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx

router = APIRouter(prefix="/hue", tags=["Hue"])

_dir      = os.path.dirname(__file__)
_ip_file  = os.path.join(_dir, "..", "hue_bridge.txt")
_key_file = os.path.join(_dir, "..", "hue_api_key.txt")

def _load(path: str) -> str:
    if os.path.exists(path):
        return open(path).read().strip()
    return ""

# Bridge nutzt HTTPS mit self-signed cert → verify=False
def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(verify=False, follow_redirects=True, timeout=10)

def _base() -> str:
    ip  = _load(_ip_file)
    key = _load(_key_file)
    if not ip:
        raise HTTPException(400, "hue_bridge.txt nicht gefunden")
    if not key:
        raise HTTPException(400, "Kein API-Key – bitte /hue/setup aufrufen")
    return f"https://{ip}/api/{key}"


class HueAction(BaseModel):
    on:  Optional[bool] = None
    bri: Optional[int]  = None   # 1–254


@router.post("/setup", tags=["Hue"])
async def hue_setup():
    """API-Key erstellen. Vorher Knopf auf der Bridge drücken!"""
    ip = _load(_ip_file)
    if not ip:
        raise HTTPException(400, "hue_bridge.txt nicht gefunden – Bridge-IP eintragen")

    async with _client() as client:
        resp = await client.post(
            f"https://{ip}/api",
            json={"devicetype": "familien_dashboard#server"},
        )
        resp.raise_for_status()

    data = resp.json()
    if isinstance(data, list) and "success" in data[0]:
        username = data[0]["success"]["username"]
        with open(_key_file, "w") as f:
            f.write(username)
        return {"ok": True, "username": username}
    elif isinstance(data, list) and "error" in data[0]:
        err = data[0]["error"]
        if err.get("type") == 101:
            raise HTTPException(403, "Bridge-Knopf nicht gedrückt – bitte drücken und nochmal versuchen")
        raise HTTPException(500, str(err))
    raise HTTPException(500, f"Unbekannte Antwort: {data}")


@router.get("/status", tags=["Hue"])
def hue_status():
    return {
        "bridge_ip": _load(_ip_file) or None,
        "api_key":   bool(_load(_key_file)),
    }


@router.get("/rooms", tags=["Hue"])
async def get_rooms():
    base = _base()
    async with _client() as client:
        resp = await client.get(f"{base}/groups")
        resp.raise_for_status()

    groups = resp.json()
    rooms = []
    for gid, g in groups.items():
        if g.get("type") not in ("Room", "Zone", "LightGroup"):
            continue
        state = g.get("action", {})
        rooms.append({
            "id":     gid,
            "name":   g.get("name", f"Raum {gid}"),
            "type":   g.get("type", "Room"),
            "on":     state.get("on", False),
            "bri":    state.get("bri", 254),
            "lights": len(g.get("lights", [])),
        })
    rooms.sort(key=lambda r: r["name"])
    return rooms


@router.put("/rooms/{group_id}", tags=["Hue"])
async def set_room(group_id: str, payload: HueAction):
    base = _base()
    body = {}
    if payload.on  is not None: body["on"]  = payload.on
    if payload.bri is not None: body["bri"] = max(1, min(254, payload.bri))
    if not body:
        raise HTTPException(400, "on oder bri angeben")

    async with _client() as client:
        resp = await client.put(f"{base}/groups/{group_id}/action", json=body)
        resp.raise_for_status()
    return resp.json()
