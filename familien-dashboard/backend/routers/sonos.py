import os
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    import soco
    SOCO_OK = True
except ImportError:
    SOCO_OK = False

router = APIRouter(prefix="/sonos", tags=["Sonos"])

_dir      = os.path.dirname(__file__)
_ip_file  = os.path.join(_dir, "..", "sonos_devices.txt")

# In-memory cache: uid → soco.SoCo object
_cache: dict = {"devices": {}, "ts": 0.0}


def _load_ips() -> list[str]:
    if os.path.exists(_ip_file):
        return [l.strip() for l in open(_ip_file).readlines() if l.strip()]
    return []


def _save_ips(devices: dict):
    ips = [d.ip_address for d in devices.values()]
    with open(_ip_file, "w") as f:
        f.write("\n".join(ips))


def _connect_from_file() -> dict:
    """Direkt per IP verbinden – sofort, kein Multicast nötig."""
    ips = _load_ips()
    if not ips:
        return {}
    result = {}
    for ip in ips:
        try:
            d = soco.SoCo(ip)
            _ = d.player_name   # Verbindung testen
            result[d.uid] = d
        except Exception:
            pass
    return result


def _discover_and_save() -> dict:
    """Multicast-Discovery, danach IPs speichern."""
    found = soco.discover(timeout=5) or set()
    devices = {d.uid: d for d in found}
    if devices:
        _save_ips(devices)
    return devices


def _get_devices() -> dict:
    if _cache["devices"] and (time.time() - _cache["ts"]) < 60:
        return _cache["devices"]
    if not SOCO_OK:
        return {}

    # 1. Direkt per gespeicherte IPs versuchen (schnell + zuverlässig)
    devices = _connect_from_file()

    # 2. Falls keine IPs gespeichert: einmalig Discovery
    if not devices:
        devices = _discover_and_save()

    _cache["devices"] = devices
    _cache["ts"] = time.time()
    return devices


def _get_device(uid: str):
    devices = _get_devices()
    if uid not in devices:
        _cache["ts"] = 0
        devices = _get_devices()
    if uid not in devices:
        raise HTTPException(404, f"Gerät {uid} nicht gefunden")
    return devices[uid]


def _coordinator(d):
    """Gibt den Gruppen-Coordinator zurück (oder das Gerät selbst)."""
    try:
        return d.group.coordinator
    except Exception:
        return d


def _device_state(d) -> dict:
    try:
        coord = _coordinator(d)
        info = coord.get_current_track_info()
        transport = coord.get_current_transport_info()
        state = transport.get("current_transport_state", "STOPPED")
        art = info.get("album_art", "") or ""
        if art and art.startswith("/"):
            art = f"http://{coord.ip_address}:1400{art}"
        return {
            "uid":            d.uid,
            "name":           d.player_name,
            "ip":             d.ip_address,
            "coordinator_uid": coord.uid,
            "is_coordinator": d.uid == coord.uid,
            "state":          state,
            "volume":         d.volume,
            "track": {
                "title":  info.get("title", ""),
                "artist": info.get("artist", ""),
                "album":  info.get("album", ""),
                "art":    art,
            },
        }
    except Exception as e:
        return {
            "uid":            d.uid,
            "name":           d.player_name,
            "ip":             d.ip_address,
            "coordinator_uid": d.uid,
            "is_coordinator": True,
            "state":          "UNKNOWN",
            "volume":         0,
            "track":          {"title": "", "artist": "", "album": "", "art": ""},
            "error":          str(e),
        }


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/devices")
def get_devices():
    if not SOCO_OK:
        raise HTTPException(503, "soco nicht installiert – pip install soco")
    return [_device_state(d) for d in _get_devices().values()]


@router.post("/rediscover")
def rediscover():
    """Multicast-Discovery erzwingen und IPs neu speichern."""
    if not SOCO_OK:
        raise HTTPException(503, "soco nicht installiert")
    _cache["ts"] = 0
    _cache["devices"] = {}
    # Temporär IP-Datei löschen damit _get_devices() Discovery macht
    if os.path.exists(_ip_file):
        os.remove(_ip_file)
    devices = _discover_and_save()
    _cache["devices"] = devices
    _cache["ts"] = time.time()
    return {"ok": True, "found": [{"uid": d.uid, "name": d.player_name, "ip": d.ip_address}
                                   for d in devices.values()]}


@router.post("/devices/{uid}/play")
def play(uid: str):
    d = _coordinator(_get_device(uid))
    try:
        d.play()
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": True}


@router.post("/devices/{uid}/pause")
def pause(uid: str):
    d = _coordinator(_get_device(uid))
    try:
        d.pause()
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": True}


@router.post("/devices/{uid}/stop")
def stop(uid: str):
    d = _coordinator(_get_device(uid))
    try:
        d.stop()
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": True}


class VolumePayload(BaseModel):
    volume: int  # 0–100


@router.put("/devices/{uid}/volume")
def set_volume(uid: str, payload: VolumePayload):
    d = _get_device(uid)
    vol = max(0, min(100, payload.volume))
    try:
        d.volume = vol
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": True, "volume": vol}


@router.get("/favorites")
def get_favorites():
    if not SOCO_OK:
        raise HTTPException(503, "soco nicht installiert")
    devices = _get_devices()
    if not devices:
        raise HTTPException(503, "Keine Sonos-Geräte gefunden")
    d = next(iter(devices.values()))
    try:
        favs = d.music_library.get_sonos_favorites()
        result = []
        for fav in favs:
            art = getattr(fav, "album_art_uri", "") or ""
            if art and art.startswith("/"):
                art = f"http://{d.ip_address}:1400{art}"
            result.append({
                "title": fav.title,
                "uri":   fav.get_uri() if hasattr(fav, "get_uri") else "",
                "meta":  fav.resource_meta_data if hasattr(fav, "resource_meta_data") else "",
                "art":   art,
            })
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


class FavoritePayload(BaseModel):
    title: str


@router.post("/devices/{uid}/play_favorite")
def play_favorite(uid: str, payload: FavoritePayload):
    d = _get_device(uid)
    try:
        favs = d.music_library.get_sonos_favorites()
        match = next((f for f in favs if f.title == payload.title), None)
        if not match:
            raise HTTPException(404, f"Favorit '{payload.title}' nicht gefunden")
        uri  = match.get_uri() if hasattr(match, "get_uri") else match.resources[0].uri
        meta = match.resource_meta_data if hasattr(match, "resource_meta_data") else ""
        d.play_uri(uri, meta=meta)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": True}
