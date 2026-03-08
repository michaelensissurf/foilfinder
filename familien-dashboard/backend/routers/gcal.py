import os
from datetime import datetime, date, timedelta, timezone

import httpx
import icalendar
import recurring_ical_events
from sqlalchemy.orm import Session

import models
from database import SessionLocal

# ICS-URL aus Datei lesen (nicht im Git)
_url_file = os.path.join(os.path.dirname(__file__), "..", "gcal_ics_url.txt")
GCAL_ICS_URL = ""
if os.path.exists(_url_file):
    GCAL_ICS_URL = open(_url_file).read().strip()

GCAL_COLOR = "#4285f4"   # Google Blau
SYNC_DAYS_PAST   = 30    # Vergangene Tage synchronisieren
SYNC_DAYS_FUTURE = 180   # Zukünftige Tage synchronisieren


def _to_naive_local(dt_val) -> datetime | None:
    """Konvertiert icalendar date/datetime → naive lokale datetime (Europe/Zurich)."""
    if dt_val is None:
        return None
    if isinstance(dt_val, datetime):
        if dt_val.tzinfo:
            from zoneinfo import ZoneInfo
            dt_val = dt_val.astimezone(ZoneInfo("Europe/Zurich")).replace(tzinfo=None)
        return dt_val
    if isinstance(dt_val, date):
        return datetime(dt_val.year, dt_val.month, dt_val.day)
    return None


async def sync_gcal() -> dict:
    if not GCAL_ICS_URL:
        return {"synced": 0, "error": "Keine ICS-URL konfiguriert"}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(GCAL_ICS_URL, timeout=30)
        resp.raise_for_status()

    cal = icalendar.Calendar.from_ical(resp.content)

    now = datetime.now()
    range_start = now - timedelta(days=SYNC_DAYS_PAST)
    range_end   = now + timedelta(days=SYNC_DAYS_FUTURE)

    components = recurring_ical_events.of(cal).between(range_start, range_end)

    db: Session = SessionLocal()
    try:
        synced = 0
        for comp in components:
            if comp.name != "VEVENT":
                continue

            uid     = str(comp.get("UID", ""))
            dtstart = comp.get("DTSTART")
            dtend   = comp.get("DTEND")
            summary = str(comp.get("SUMMARY", "Kein Titel"))

            if not uid or not dtstart:
                continue

            start_dt = _to_naive_local(dtstart.dt)
            end_dt   = _to_naive_local(dtend.dt) if dtend else None
            all_day  = not isinstance(dtstart.dt, datetime)

            # Für wiederkehrende Events: UID + Startdatum als eindeutiger Key
            gcal_uid = f"{uid}_{start_dt.date()}" if start_dt else uid

            existing = db.query(models.Event).filter(
                models.Event.gcal_uid == gcal_uid
            ).first()

            if existing:
                existing.title          = summary
                existing.start_datetime = start_dt
                existing.end_datetime   = end_dt
                existing.all_day        = all_day
            else:
                db.add(models.Event(
                    title          = summary,
                    start_datetime = start_dt,
                    end_datetime   = end_dt,
                    all_day        = all_day,
                    person         = "family",
                    color          = GCAL_COLOR,
                    gcal_uid       = gcal_uid,
                ))
            synced += 1

        db.commit()
        return {"synced": synced}

    finally:
        db.close()
