"""
Familien-Dashboard – Surfer House Edition
Kein Node.js nötig – öffnet sich direkt im Browser

Voraussetzung: Backend läuft auf http://localhost:8000
  cd familien-dashboard/backend
  python -m uvicorn main:app --reload --port 8000
"""

import webbrowser
import os

HTML = r"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>🏄 Familien-Dashboard</title>
  <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Inter', 'Segoe UI', sans-serif;
      background: #071526;
      min-height: 100vh;
    }
    input, select, textarea { font-family: inherit; }

    /* Ocean background with subtle wave gradient */
    #root {
      background:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(6,182,212,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(249,115,22,0.08) 0%, transparent 50%),
        linear-gradient(160deg, #071526 0%, #0a1e35 50%, #071a2e 100%);
      min-height: 100vh;
    }

    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(6,182,212,0.3); border-radius: 3px; }

    /* Glassmorphism card base */
    .glass {
      background: rgba(255,255,255,0.04);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 20px;
    }

    /* Smooth transitions */
    button { transition: all 0.15s ease; }
    button:active { transform: scale(0.97); }

    input:focus, select:focus, textarea:focus {
      outline: none;
      border-color: rgba(6,182,212,0.5) !important;
      box-shadow: 0 0 0 3px rgba(6,182,212,0.1);
    }

    details > summary { list-style: none; }
    details > summary::-webkit-details-marker { display: none; }
  </style>
</head>
<body>
<div id="root"></div>

<script type="text/babel">
const { useState, useEffect, useCallback } = React;

// ── API CLIENT ────────────────────────────────────────────────────────────────
const API = "http://localhost:8000";
const apiFetch = async (path, options = {}) => {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (res.status === 204) return null;
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
};
const apiGet  = (path)       => apiFetch(path);
const apiPost = (path, body) => apiFetch(path, { method: "POST",   body: JSON.stringify(body) });
const apiPut  = (path, body) => apiFetch(path, { method: "PUT",    body: body ? JSON.stringify(body) : undefined });
const apiDel  = (path)       => apiFetch(path, { method: "DELETE" });

// ── DESIGN TOKENS ─────────────────────────────────────────────────────────────
const C = {
  ocean:   "#06b6d4",   // cyan / turquoise
  coral:   "#f97316",   // sunset orange
  seafoam: "#34d399",   // mint green
  sand:    "#fbbf24",   // warm yellow
  wave:    "#818cf8",   // soft indigo
  reef:    "#fb7185",   // pink coral

  bg:       "#071526",
  cardBg:   "rgba(255,255,255,0.04)",
  cardHover:"rgba(255,255,255,0.07)",
  border:   "rgba(255,255,255,0.08)",
  borderHi: "rgba(6,182,212,0.35)",

  text:     "#f0f8ff",
  textSub:  "rgba(240,248,255,0.6)",
  textMute: "rgba(240,248,255,0.35)",
};

const PERSON_COLORS = { mama: C.wave, papa: C.ocean, kind: C.sand, family: C.seafoam };
const PERSON_EMOJI  = { mama: "👩", papa: "👨", kind: "👶", family: "🌊" };
const TODO_LISTS    = ["Einkauf", "Haushalt", "Erledigung"];

// Static data
const weatherData = {
  temp: 12, icon: "🌧️", desc: "Bedeckt, 18 km/h Wind",
  forecast: [{ day: "Fr", icon: "⛅", temp: 15 }, { day: "Sa", icon: "☀️", temp: 20 }, { day: "So", icon: "☀️", temp: 21 }],
};
const meals = { breakfast: "🥣 Açaí Bowl", lunch: "🌮 Fish Tacos", dinner: "🥗 Poke Bowl" };
const quickButtons = [
  { label: "🛒 Einkauf",  color: C.ocean  },
  { label: "🍕 Pizza",    color: C.coral  },
  { label: "🏥 Arzt",     color: C.seafoam},
  { label: "🚗 Fahrt",    color: C.sand   },
  { label: "📦 Paket",    color: C.wave   },
  { label: "🏄 Strand",   color: C.reef   },
];
const weekMeals = [
  { day: "Mo", meal: "🍝 Pasta" }, { day: "Di", meal: "🌮 Tacos" },
  { day: "Mi", meal: "🐟 Fisch" }, { day: "Do", meal: "🍜 Ramen" },
  { day: "Fr", meal: "🍕 Pizza" }, { day: "Sa", meal: "🍔 Burger" },
  { day: "So", meal: "🥩 Braten" },
];
const stundenplan = [
  { fach: "Deutsch",  icon: "📖", color: C.wave   },
  { fach: "Mathe",    icon: "🔢", color: C.ocean  },
  { fach: "Turnen",   icon: "⚽", color: C.coral  },
  { fach: "Musik",    icon: "🎵", color: C.sand   },
  { fach: "Kunst",    icon: "🎨", color: C.reef   },
];

// ── HELPERS ───────────────────────────────────────────────────────────────────
const fmtTime    = (dt) => dt ? new Date(dt).toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" }) : "";
const fmtDate    = (dt) => dt ? new Date(dt).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit" }) : "";
const todayStr   = () => { const n = new Date(); return `${n.getFullYear()}-${String(n.getMonth()+1).padStart(2,"0")}-${String(n.getDate()).padStart(2,"0")}`; };
const isToday    = (dt) => dt && dt.startsWith(todayStr());

// ── GLASS CARD ────────────────────────────────────────────────────────────────
const Card = ({ children, style = {}, glow = null }) => (
  <div className="glass" style={{
    padding: 24,
    boxShadow: glow ? `0 0 40px ${glow}18, 0 4px 24px rgba(0,0,0,0.3)` : "0 4px 24px rgba(0,0,0,0.25)",
    ...style,
  }}>
    {children}
  </div>
);

const Label = ({ children }) => (
  <div style={{ color: C.textMute, fontSize: 11, fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 14 }}>
    {children}
  </div>
);

const Badge = ({ children, color }) => (
  <span style={{ background: color + "22", color, border: `1px solid ${color}44`, borderRadius: 20, padding: "3px 10px", fontSize: 11, fontWeight: 700 }}>
    {children}
  </span>
);

// ── MODAL ─────────────────────────────────────────────────────────────────────
function Modal({ onClose, title, children }) {
  useEffect(() => {
    const h = (e) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [onClose]);

  return (
    <div onClick={onClose} style={{
      position: "fixed", inset: 0, zIndex: 200,
      background: "rgba(7,21,38,0.85)",
      backdropFilter: "blur(8px)",
      display: "flex", alignItems: "center", justifyContent: "center", padding: 20,
    }}>
      <div onClick={e => e.stopPropagation()} className="glass" style={{
        width: "100%", maxWidth: 460, padding: 28,
        border: `1px solid ${C.borderHi}`,
        boxShadow: `0 0 60px rgba(6,182,212,0.12), 0 20px 60px rgba(0,0,0,0.5)`,
      }}>
        <div style={{ color: C.text, fontSize: 18, fontWeight: 700, marginBottom: 22 }}>{title}</div>
        {children}
      </div>
    </div>
  );
}

// ── INPUT STYLE ───────────────────────────────────────────────────────────────
const inputSx = {
  width: "100%",
  background: "rgba(255,255,255,0.05)",
  border: `1px solid ${C.border}`,
  borderRadius: 12,
  padding: "11px 14px",
  color: C.text,
  fontSize: 14,
  marginTop: 6,
};

// ── EVENT MODAL ───────────────────────────────────────────────────────────────
function EventModal({ onClose, onSave, initialDate }) {
  const [f, setF] = useState({
    title: "", start_datetime: `${initialDate || todayStr()}T08:00`,
    end_datetime: "", person: "family", color: C.ocean, description: "", all_day: false,
  });
  const s = (k, v) => setF(x => ({ ...x, [k]: v }));

  return (
    <Modal onClose={onClose} title="🌊 Neues Event">
      <div style={{ marginBottom: 14 }}>
        <div style={{ color: C.textMute, fontSize: 11, fontWeight: 700, letterSpacing: "0.08em" }}>TITEL *</div>
        <input style={inputSx} value={f.title} onChange={e => s("title", e.target.value)} placeholder="z.B. Surfkurs" autoFocus />
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 14 }}>
        <div>
          <div style={{ color: C.textMute, fontSize: 11, fontWeight: 700, letterSpacing: "0.08em" }}>START *</div>
          <input style={inputSx} type="datetime-local" value={f.start_datetime} onChange={e => s("start_datetime", e.target.value)} />
        </div>
        <div>
          <div style={{ color: C.textMute, fontSize: 11, fontWeight: 700, letterSpacing: "0.08em" }}>ENDE</div>
          <input style={inputSx} type="datetime-local" value={f.end_datetime} onChange={e => s("end_datetime", e.target.value)} />
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 14 }}>
        <div>
          <div style={{ color: C.textMute, fontSize: 11, fontWeight: 700, letterSpacing: "0.08em" }}>PERSON</div>
          <select style={inputSx} value={f.person} onChange={e => s("person", e.target.value)}>
            {Object.keys(PERSON_COLORS).map(p => <option key={p} value={p}>{PERSON_EMOJI[p]} {p}</option>)}
          </select>
        </div>
        <div>
          <div style={{ color: C.textMute, fontSize: 11, fontWeight: 700, letterSpacing: "0.08em" }}>FARBE</div>
          <input style={{ ...inputSx, padding: 6, height: 44, cursor: "pointer" }} type="color" value={f.color} onChange={e => s("color", e.target.value)} />
        </div>
      </div>
      <div style={{ marginBottom: 20 }}>
        <div style={{ color: C.textMute, fontSize: 11, fontWeight: 700, letterSpacing: "0.08em" }}>NOTIZ</div>
        <textarea style={{ ...inputSx, height: 72, resize: "vertical" }} value={f.description} onChange={e => s("description", e.target.value)} placeholder="Optional..." />
      </div>
      <div style={{ display: "flex", gap: 10 }}>
        <button onClick={onClose} style={{ flex: 1, background: "rgba(255,255,255,0.05)", border: `1px solid ${C.border}`, borderRadius: 12, padding: 13, color: C.textSub, cursor: "pointer", fontSize: 14 }}>Abbrechen</button>
        <button onClick={async () => {
          if (!f.title.trim()) return;
          await onSave({ title: f.title, description: f.description || null, start_datetime: f.start_datetime, end_datetime: f.end_datetime || null, person: f.person, color: f.color, all_day: f.all_day });
          onClose();
        }} style={{ flex: 2, background: `linear-gradient(135deg, ${C.ocean}, #0284c7)`, border: "none", borderRadius: 12, padding: 13, color: "#fff", cursor: "pointer", fontSize: 14, fontWeight: 700, boxShadow: `0 4px 20px ${C.ocean}44` }}>
          Speichern 🌊
        </button>
      </div>
    </Modal>
  );
}

// ── MAIN ─────────────────────────────────────────────────────────────────────
function Dashboard() {
  const [page,      setPage]      = useState("heute");
  const [backendOk, setBackendOk] = useState(null);
  const now = new Date();

  useEffect(() => {
    apiGet("/").then(() => setBackendOk(true)).catch(() => setBackendOk(false));
  }, []);

  const dateStr = now.toLocaleDateString("de-DE", { weekday: "long", day: "numeric", month: "long" });

  // ── HEUTE ──────────────────────────────────────────────────────────────────
  function HeutePage() {
    const [events,    setEvents]    = useState([]);
    const [todos,     setTodos]     = useState([]);
    const [loading,   setLoading]   = useState(true);
    const [showModal, setShowModal] = useState(false);

    useEffect(() => {
      const ym = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,"0")}`;
      Promise.all([apiGet(`/events/?date=${ym}`), apiGet("/todos/")])
        .then(([evts, tds]) => {
          setEvents(evts.filter(e => isToday(e.start_datetime)));
          setTodos(tds.filter(t => !t.done));
          setLoading(false);
        }).catch(() => setLoading(false));
    }, []);

    const saveEvent = async (payload) => {
      const created = await apiPost("/events/", payload);
      if (isToday(created.start_datetime)) setEvents(e => [...e, created].sort((a,b) => a.start_datetime.localeCompare(b.start_datetime)));
    };

    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {showModal && <EventModal onClose={() => setShowModal(false)} onSave={saveEvent} />}

        {/* Hero Banner */}
        <div style={{
          background: `linear-gradient(135deg, rgba(6,182,212,0.25) 0%, rgba(249,115,22,0.2) 100%)`,
          border: `1px solid rgba(6,182,212,0.2)`,
          borderRadius: 24, padding: "20px 24px",
          display: "flex", alignItems: "center", justifyContent: "space-between",
        }}>
          <div>
            <div style={{ color: C.text, fontWeight: 800, fontSize: 22, letterSpacing: "-0.03em" }}>Guten Morgen 🤙</div>
            <div style={{ color: C.textSub, fontSize: 14, marginTop: 3 }}>{dateStr}</div>
          </div>
          <div style={{ fontSize: 48, lineHeight: 1 }}>🏄</div>
        </div>

        {/* Wetter + Mahlzeiten */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
          <Card glow={C.ocean}>
            <Label>Wetter</Label>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <span style={{ fontSize: 40 }}>{weatherData.icon}</span>
              <div>
                <div style={{ color: C.text, fontSize: 30, fontWeight: 800, letterSpacing: "-0.04em" }}>{weatherData.temp}°</div>
                <div style={{ color: C.textMute, fontSize: 11 }}>{weatherData.desc}</div>
              </div>
            </div>
            <div style={{ display: "flex", gap: 8, marginTop: 14, paddingTop: 14, borderTop: `1px solid ${C.border}` }}>
              {weatherData.forecast.map(f => (
                <div key={f.day} style={{ flex: 1, textAlign: "center" }}>
                  <div style={{ color: C.textMute, fontSize: 11 }}>{f.day}</div>
                  <div style={{ fontSize: 18, margin: "3px 0" }}>{f.icon}</div>
                  <div style={{ color: C.text, fontSize: 13, fontWeight: 600 }}>{f.temp}°</div>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <Label>Essen heute</Label>
            {[["🌅 Früh", meals.breakfast], ["☀️ Mittag", meals.lunch], ["🌙 Abend", meals.dinner]].map(([l, m]) => (
              <div key={l} style={{ marginBottom: 10 }}>
                <div style={{ color: C.textMute, fontSize: 10, fontWeight: 600 }}>{l}</div>
                <div style={{ color: C.textSub, fontSize: 13, fontWeight: 500, marginTop: 1 }}>{m}</div>
              </div>
            ))}
          </Card>
        </div>

        {/* Termine */}
        <Card glow={C.wave}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
            <Label>Termine heute</Label>
            <button onClick={() => setShowModal(true)} style={{
              background: `linear-gradient(135deg, ${C.ocean}22, ${C.ocean}11)`,
              border: `1px solid ${C.ocean}44`, color: C.ocean, borderRadius: 10,
              padding: "5px 14px", cursor: "pointer", fontSize: 13, fontWeight: 700,
            }}>+ Event</button>
          </div>
          {loading ? (
            <div style={{ color: C.textMute, fontSize: 14 }}>Laden...</div>
          ) : events.length === 0 ? (
            <div style={{ display: "flex", alignItems: "center", gap: 10, color: C.textMute, fontSize: 14 }}>
              <span style={{ fontSize: 24 }}>🌊</span> Keine Termine – freier Tag!
            </div>
          ) : events.map((e, i) => (
            <div key={e.id ?? i} style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 10, padding: "10px 14px", background: (e.color || C.ocean) + "0d", borderRadius: 12, border: `1px solid ${(e.color || C.ocean)}22` }}>
              <div style={{ color: e.color || C.ocean, fontSize: 13, fontWeight: 800, minWidth: 44, fontVariantNumeric: "tabular-nums" }}>{fmtTime(e.start_datetime)}</div>
              <div style={{ flex: 1, color: C.text, fontSize: 14, fontWeight: 500 }}>{e.title}</div>
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: e.color || PERSON_COLORS[e.person] || C.ocean, flexShrink: 0 }} />
            </div>
          ))}
        </Card>

        {/* Offene Todos */}
        <Card>
          <Label>Offene Todos</Label>
          {loading ? <div style={{ color: C.textMute, fontSize: 14 }}>Laden...</div>
            : todos.length === 0
            ? <div style={{ color: C.textMute, fontSize: 14, display: "flex", gap: 8, alignItems: "center" }}><span>✨</span> Alles erledigt – nice!</div>
            : todos.slice(0, 6).map(t => (
              <div key={t.id} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                <div style={{ width: 6, height: 6, borderRadius: "50%", background: PERSON_COLORS[t.person] || C.textMute, flexShrink: 0 }} />
                <div style={{ flex: 1, color: C.textSub, fontSize: 14 }}>{t.text}</div>
                <Badge color={PERSON_COLORS[t.person] || C.textMute}>{t.list_name}</Badge>
              </div>
            ))
          }
        </Card>

        {/* Quick Buttons */}
        <Card>
          <Label>Schnell-Buttons</Label>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 10 }}>
            {quickButtons.map((btn, i) => (
              <button key={i} style={{
                background: `linear-gradient(135deg, ${btn.color}18, ${btn.color}0a)`,
                border: `1px solid ${btn.color}33`,
                borderRadius: 14, padding: "14px 8px",
                color: btn.color, fontSize: 13, fontWeight: 700, cursor: "pointer",
              }}
                onMouseEnter={e => { e.currentTarget.style.background = `linear-gradient(135deg, ${btn.color}30, ${btn.color}18)`; e.currentTarget.style.borderColor = `${btn.color}66`; }}
                onMouseLeave={e => { e.currentTarget.style.background = `linear-gradient(135deg, ${btn.color}18, ${btn.color}0a)`; e.currentTarget.style.borderColor = `${btn.color}33`; }}
              >{btn.label}</button>
            ))}
          </div>
        </Card>
      </div>
    );
  }

  // ── KALENDER ──────────────────────────────────────────────────────────────
  function KalenderPage() {
    const [year,      setYear]      = useState(now.getFullYear());
    const [month,     setMonth]     = useState(now.getMonth() + 1);
    const [events,    setEvents]    = useState([]);
    const [loading,   setLoading]   = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [selDay,    setSelDay]    = useState(null);
    const [popup,     setPopup]     = useState(null);

    const loadEvents = useCallback(() => {
      setLoading(true);
      const ym = `${year}-${String(month).padStart(2,"0")}`;
      apiGet(`/events/?date=${ym}`).then(d => { setEvents(d); setLoading(false); }).catch(() => setLoading(false));
    }, [year, month]);

    useEffect(() => { loadEvents(); }, [loadEvents]);

    const prev = () => { if (month === 1) { setYear(y => y-1); setMonth(12); } else setMonth(m => m-1); };
    const next = () => { if (month === 12) { setYear(y => y+1); setMonth(1); } else setMonth(m => m+1); };

    const saveEvent  = async (p) => { await apiPost("/events/", p); loadEvents(); };
    const delEvent   = async (id) => { await apiDel(`/events/${id}`); setPopup(null); loadEvents(); };

    const MONTHS = ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"];
    const daysInMonth = new Date(year, month, 0).getDate();
    const startDow    = (new Date(year, month-1, 1).getDay() + 6) % 7;

    const evDay = (d) => events.filter(e => {
      const dt = new Date(e.start_datetime);
      return dt.getFullYear() === year && (dt.getMonth()+1) === month && dt.getDate() === d;
    });

    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {showModal && <EventModal onClose={() => setShowModal(false)} onSave={saveEvent}
          initialDate={selDay ? `${year}-${String(month).padStart(2,"0")}-${String(selDay).padStart(2,"0")}` : null} />}

        {popup && (
          <div onClick={() => setPopup(null)} style={{ position: "fixed", inset: 0, background: "rgba(7,21,38,0.85)", backdropFilter: "blur(8px)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 200, padding: 20 }}>
            <div onClick={e => e.stopPropagation()} className="glass" style={{ width: "100%", maxWidth: 360, padding: 24, border: `1px solid ${C.borderHi}`, boxShadow: `0 0 40px rgba(6,182,212,0.15)` }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
                <div style={{ width: 12, height: 12, borderRadius: "50%", background: popup.event.color || C.ocean, boxShadow: `0 0 8px ${popup.event.color || C.ocean}` }} />
                <div style={{ color: C.text, fontSize: 17, fontWeight: 700 }}>{popup.event.title}</div>
              </div>
              <div style={{ color: C.textSub, fontSize: 13, marginBottom: 6 }}>📅 {fmtDate(popup.event.start_datetime)} · {fmtTime(popup.event.start_datetime)}{popup.event.end_datetime && ` – ${fmtTime(popup.event.end_datetime)}`}</div>
              <div style={{ color: C.textSub, fontSize: 13, marginBottom: popup.event.description ? 12 : 0 }}>{PERSON_EMOJI[popup.event.person]} {popup.event.person}</div>
              {popup.event.description && <div style={{ color: C.textMute, fontSize: 13, marginBottom: 12, padding: "10px 14px", background: "rgba(255,255,255,0.04)", borderRadius: 10 }}>{popup.event.description}</div>}
              <div style={{ display: "flex", gap: 10, marginTop: 18 }}>
                <button onClick={() => setPopup(null)} style={{ flex: 1, background: "rgba(255,255,255,0.05)", border: `1px solid ${C.border}`, borderRadius: 10, padding: 11, color: C.textSub, cursor: "pointer", fontSize: 13 }}>Schließen</button>
                <button onClick={() => delEvent(popup.event.id)} style={{ flex: 1, background: "rgba(251,113,133,0.1)", border: "1px solid rgba(251,113,133,0.3)", borderRadius: 10, padding: 11, color: C.reef, cursor: "pointer", fontSize: 13, fontWeight: 700 }}>🗑 Löschen</button>
              </div>
            </div>
          </div>
        )}

        <Card>
          {/* Navigation */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 22 }}>
            <button onClick={prev} style={{ background: "rgba(255,255,255,0.05)", border: `1px solid ${C.border}`, color: C.text, width: 38, height: 38, borderRadius: 10, fontSize: 18, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}>‹</button>
            <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
              <div style={{ color: C.text, fontSize: 19, fontWeight: 800, letterSpacing: "-0.03em" }}>{MONTHS[month-1]} {year}</div>
              <button onClick={() => { setSelDay(null); setShowModal(true); }} style={{ background: `linear-gradient(135deg, ${C.ocean}22, ${C.ocean}11)`, border: `1px solid ${C.ocean}44`, color: C.ocean, borderRadius: 10, padding: "5px 14px", cursor: "pointer", fontSize: 13, fontWeight: 700 }}>+ Event</button>
            </div>
            <button onClick={next} style={{ background: "rgba(255,255,255,0.05)", border: `1px solid ${C.border}`, color: C.text, width: 38, height: 38, borderRadius: 10, fontSize: 18, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}>›</button>
          </div>

          {/* Weekday headers */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: 4, marginBottom: 6 }}>
            {["Mo","Di","Mi","Do","Fr","Sa","So"].map(d => (
              <div key={d} style={{ color: C.textMute, fontSize: 11, textAlign: "center", fontWeight: 700, letterSpacing: "0.05em" }}>{d}</div>
            ))}
          </div>

          {/* Days */}
          {loading ? (
            <div style={{ color: C.textMute, textAlign: "center", padding: 30, fontSize: 14 }}>Laden...</div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: 4 }}>
              {Array.from({ length: startDow }).map((_, i) => <div key={"e"+i} />)}
              {Array.from({ length: daysInMonth }, (_, i) => i+1).map(d => {
                const dayEvts  = evDay(d);
                const isTodayD = year === now.getFullYear() && month === (now.getMonth()+1) && d === now.getDate();
                return (
                  <div key={d} onClick={() => { setSelDay(d); setShowModal(true); }} style={{
                    background:   isTodayD ? `linear-gradient(135deg, ${C.ocean}, #0284c7)` : "rgba(255,255,255,0.03)",
                    border:       isTodayD ? `1px solid ${C.ocean}` : `1px solid ${C.border}`,
                    borderRadius: 12, padding: "6px 4px", textAlign: "center", cursor: "pointer",
                    minHeight: 58, display: "flex", flexDirection: "column", alignItems: "center",
                    transition: "all 0.12s",
                    boxShadow: isTodayD ? `0 4px 16px ${C.ocean}44` : "none",
                  }}
                    onMouseEnter={e => { if (!isTodayD) e.currentTarget.style.background = "rgba(255,255,255,0.07)"; }}
                    onMouseLeave={e => { if (!isTodayD) e.currentTarget.style.background = "rgba(255,255,255,0.03)"; }}
                  >
                    <div style={{ color: isTodayD ? "#fff" : C.text, fontSize: 13, fontWeight: isTodayD ? 800 : 400 }}>{d}</div>
                    {dayEvts.slice(0, 2).map((e, ei) => (
                      <div key={ei} onClick={ev => { ev.stopPropagation(); setPopup({ event: e }); }} style={{
                        width: "88%", background: (e.color || C.ocean) + "33",
                        color: e.color || C.ocean, borderRadius: 4, fontSize: 9,
                        padding: "2px 3px", marginTop: 3, overflow: "hidden",
                        whiteSpace: "nowrap", textOverflow: "ellipsis", lineHeight: 1.4, fontWeight: 600,
                      }}>{e.title}</div>
                    ))}
                    {dayEvts.length > 2 && <div style={{ color: C.textMute, fontSize: 9, marginTop: 2 }}>+{dayEvts.length - 2}</div>}
                  </div>
                );
              })}
            </div>
          )}

          {/* Legend */}
          <div style={{ marginTop: 18, paddingTop: 16, borderTop: `1px solid ${C.border}`, display: "flex", gap: 16, flexWrap: "wrap" }}>
            {Object.entries(PERSON_COLORS).map(([p, c]) => (
              <div key={p} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <div style={{ width: 10, height: 10, borderRadius: "50%", background: c, boxShadow: `0 0 6px ${c}88` }} />
                <span style={{ color: C.textMute, fontSize: 12 }}>{PERSON_EMOJI[p]} {p}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    );
  }

  // ── TODOS ──────────────────────────────────────────────────────────────────
  function TodosPage() {
    const [todos,    setTodos]    = useState([]);
    const [loading,  setLoading]  = useState(true);
    const [newText,  setNewText]  = useState({});
    const [addingTo, setAddingTo] = useState(null);

    useEffect(() => {
      apiGet("/todos/").then(d => { setTodos(d); setLoading(false); }).catch(() => setLoading(false));
    }, []);

    const toggle  = async (id) => { const u = await apiPut(`/todos/${id}/done`); setTodos(ts => ts.map(t => t.id === id ? u : t)); };
    const del     = async (id) => { await apiDel(`/todos/${id}`); setTodos(ts => ts.filter(t => t.id !== id)); };
    const addTodo = async (list) => {
      const txt = (newText[list] || "").trim();
      if (!txt) return;
      const c = await apiPost("/todos/", { text: txt, list_name: list, person: "family" });
      setTodos(ts => [c, ...ts]);
      setNewText(n => ({ ...n, [list]: "" }));
      setAddingTo(null);
    };

    const LIST_ICONS = { Einkauf: "🛒", Haushalt: "🏠", Erledigung: "✅" };
    const LIST_COLORS = { Einkauf: C.ocean, Haushalt: C.seafoam, Erledigung: C.coral };

    if (loading) return <Card><div style={{ color: C.textMute }}>Laden...</div></Card>;

    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {TODO_LISTS.map(list => {
          const all  = todos.filter(t => t.list_name === list);
          const open = all.filter(t => !t.done);
          const done = all.filter(t => t.done);
          const lc   = LIST_COLORS[list] || C.ocean;
          return (
            <Card key={list} glow={lc} style={{ borderTop: `3px solid ${lc}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ fontSize: 18 }}>{LIST_ICONS[list]}</span>
                  <span style={{ color: C.text, fontSize: 15, fontWeight: 700 }}>{list}</span>
                  {open.length > 0 && <Badge color={lc}>{open.length}</Badge>}
                </div>
                <button onClick={() => setAddingTo(addingTo === list ? null : list)} style={{
                  background: `linear-gradient(135deg, ${lc}22, ${lc}0a)`, border: `1px solid ${lc}44`,
                  color: lc, borderRadius: 10, padding: "5px 14px", cursor: "pointer", fontSize: 13, fontWeight: 700,
                }}>+ Hinzufügen</button>
              </div>

              {addingTo === list && (
                <div style={{ display: "flex", gap: 8, marginBottom: 14 }}>
                  <input autoFocus value={newText[list] || ""}
                    onChange={e => setNewText(n => ({ ...n, [list]: e.target.value }))}
                    onKeyDown={e => { if (e.key === "Enter") addTodo(list); if (e.key === "Escape") setAddingTo(null); }}
                    placeholder="Neues Todo hinzufügen..."
                    style={{ flex: 1, background: "rgba(255,255,255,0.05)", border: `1px solid ${lc}44`, borderRadius: 12, padding: "11px 14px", color: C.text, fontSize: 14 }} />
                  <button onClick={() => addTodo(list)} style={{ background: `linear-gradient(135deg, ${lc}, ${lc}bb)`, border: "none", borderRadius: 12, padding: "11px 18px", color: "#fff", cursor: "pointer", fontWeight: 700, boxShadow: `0 4px 12px ${lc}44` }}>OK</button>
                </div>
              )}

              {open.length === 0 && done.length === 0 && (
                <div style={{ color: C.textMute, fontSize: 14, padding: "8px 0" }}>Noch keine Einträge</div>
              )}

              {open.map(t => (
                <div key={t.id} style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8, padding: "8px 10px", borderRadius: 10, background: "rgba(255,255,255,0.02)" }}>
                  <div onClick={() => toggle(t.id)} style={{
                    width: 22, height: 22, borderRadius: 6, flexShrink: 0, cursor: "pointer",
                    border: `2px solid ${PERSON_COLORS[t.person] || lc}`,
                    background: "transparent",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    transition: "all 0.15s",
                  }}
                    onMouseEnter={e => e.currentTarget.style.background = `${lc}22`}
                    onMouseLeave={e => e.currentTarget.style.background = "transparent"}
                  />
                  <div style={{ flex: 1, color: C.textSub, fontSize: 14 }}>{t.text}</div>
                  <div style={{ width: 8, height: 8, borderRadius: "50%", background: PERSON_COLORS[t.person] || C.textMute, boxShadow: `0 0 6px ${PERSON_COLORS[t.person] || C.textMute}88` }} />
                  <button onClick={() => del(t.id)} style={{ background: "transparent", border: "none", color: C.textMute, cursor: "pointer", fontSize: 18, lineHeight: 1, padding: "0 2px" }}
                    onMouseEnter={e => e.currentTarget.style.color = C.reef}
                    onMouseLeave={e => e.currentTarget.style.color = C.textMute}>×</button>
                </div>
              ))}

              {done.length > 0 && (
                <details style={{ marginTop: 8 }}>
                  <summary style={{ color: C.textMute, fontSize: 12, cursor: "pointer", userSelect: "none", padding: "6px 0" }}>
                    ✓ Erledigt ({done.length})
                  </summary>
                  <div style={{ marginTop: 8 }}>
                    {done.map(t => (
                      <div key={t.id} style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 7 }}>
                        <div onClick={() => toggle(t.id)} style={{ width: 22, height: 22, borderRadius: 6, border: `2px solid ${PERSON_COLORS[t.person] || lc}`, background: PERSON_COLORS[t.person] || lc, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                          <span style={{ color: "#fff", fontSize: 12, fontWeight: 800 }}>✓</span>
                        </div>
                        <div style={{ flex: 1, color: C.textMute, fontSize: 13, textDecoration: "line-through" }}>{t.text}</div>
                        <button onClick={() => del(t.id)} style={{ background: "transparent", border: "none", color: C.textMute, cursor: "pointer", fontSize: 18, padding: "0 2px" }}>×</button>
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </Card>
          );
        })}
      </div>
    );
  }

  // ── SPEISEPLAN ─────────────────────────────────────────────────────────────
  const todayDow = ["So","Mo","Di","Mi","Do","Fr","Sa"][now.getDay()];
  function SpeisePage() {
    return (
      <Card>
        <Label>Speiseplan diese Woche</Label>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {weekMeals.map(m => (
            <div key={m.day} style={{
              display: "flex", alignItems: "center", gap: 16,
              background: m.day === todayDow ? `linear-gradient(90deg, ${C.ocean}18, transparent)` : "rgba(255,255,255,0.02)",
              border: m.day === todayDow ? `1px solid ${C.ocean}33` : "1px solid transparent",
              borderRadius: 12, padding: "11px 16px",
              transition: "all 0.15s",
            }}>
              <div style={{ color: m.day === todayDow ? C.ocean : C.textMute, fontWeight: m.day === todayDow ? 800 : 500, fontSize: 13, minWidth: 26 }}>{m.day}</div>
              {m.day === todayDow && <Badge color={C.ocean}>HEUTE</Badge>}
              <div style={{ color: C.textSub, fontSize: 15 }}>{m.meal}</div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  // ── STUNDENPLAN ────────────────────────────────────────────────────────────
  function StundenplanPage() {
    return (
      <Card>
        <Label>Stundenplan – heute</Label>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {stundenplan.map((s, i) => (
            <div key={i} style={{
              display: "flex", alignItems: "center", gap: 14,
              background: `linear-gradient(90deg, ${s.color}10, transparent)`,
              border: `1px solid ${s.color}22`,
              borderRadius: 14, padding: "13px 18px",
            }}>
              <span style={{ fontSize: 22 }}>{s.icon}</span>
              <div style={{ color: C.text, fontSize: 15, fontWeight: 600 }}>{s.fach}</div>
              <div style={{ marginLeft: "auto", color: C.textMute, fontSize: 13, fontVariantNumeric: "tabular-nums" }}>{8+i}:00 – {9+i}:00</div>
              <div style={{ width: 4, height: 28, background: s.color, borderRadius: 2, boxShadow: `0 0 8px ${s.color}` }} />
            </div>
          ))}
        </div>
      </Card>
    );
  }

  // ── NAV ────────────────────────────────────────────────────────────────────
  const nav = [
    { id: "heute",       icon: "🏠", label: "Heute" },
    { id: "kalender",    icon: "📅", label: "Kalender" },
    { id: "todos",       icon: "✅", label: "Todos" },
    { id: "speise",      icon: "🍽️", label: "Essen" },
    { id: "stundenplan", icon: "🎒", label: "Schule" },
  ];

  const pageMap = { heute: <HeutePage />, kalender: <KalenderPage />, todos: <TodosPage />, speise: <SpeisePage />, stundenplan: <StundenplanPage /> };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>

      {/* ── HEADER ── */}
      <div style={{
        position: "sticky", top: 0, zIndex: 50,
        background: "rgba(7,21,38,0.85)",
        backdropFilter: "blur(20px)",
        borderBottom: `1px solid ${C.border}`,
        padding: "14px 20px",
        display: "flex", justifyContent: "space-between", alignItems: "center",
      }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 20 }}>🏄</span>
            <span style={{ color: C.text, fontSize: 19, fontWeight: 800, letterSpacing: "-0.03em" }}>Family Surf House</span>
          </div>
          <div style={{ color: C.textMute, fontSize: 12, marginTop: 2, display: "flex", alignItems: "center", gap: 8 }}>
            {dateStr}
            {backendOk === true  && <span style={{ background: `${C.seafoam}22`, color: C.seafoam, borderRadius: 20, padding: "1px 8px", fontSize: 10, fontWeight: 700 }}>● LIVE</span>}
            {backendOk === false && <span style={{ background: `${C.reef}22`,    color: C.reef,    borderRadius: 20, padding: "1px 8px", fontSize: 10, fontWeight: 700 }}>⚠ OFFLINE</span>}
          </div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          {Object.entries(PERSON_EMOJI).map(([p, e]) => (
            <div key={p} title={p} style={{
              width: 34, height: 34, borderRadius: "50%",
              background: `linear-gradient(135deg, ${PERSON_COLORS[p]}cc, ${PERSON_COLORS[p]}88)`,
              display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16,
              boxShadow: `0 0 10px ${PERSON_COLORS[p]}44`,
              border: `1px solid ${PERSON_COLORS[p]}44`,
            }}>{e}</div>
          ))}
        </div>
      </div>

      {/* ── CONTENT ── */}
      <div style={{ flex: 1, overflowY: "auto", padding: "20px 16px 100px", maxWidth: 640, margin: "0 auto", width: "100%" }}>
        {pageMap[page]}
      </div>

      {/* ── BOTTOM NAV ── */}
      <div style={{
        position: "fixed", bottom: 0, left: 0, right: 0, zIndex: 50,
        background: "rgba(7,21,38,0.9)",
        backdropFilter: "blur(20px)",
        borderTop: `1px solid ${C.border}`,
        display: "flex", justifyContent: "space-around",
        padding: "10px 0 16px",
      }}>
        {nav.map(n => {
          const active = page === n.id;
          return (
            <button key={n.id} onClick={() => setPage(n.id)} style={{
              background: "transparent", border: "none", cursor: "pointer",
              display: "flex", flexDirection: "column", alignItems: "center", gap: 4,
              padding: "6px 18px", borderRadius: 14,
              position: "relative",
            }}>
              <span style={{ fontSize: 22, filter: active ? "none" : "grayscale(30%) opacity(60%)", transition: "filter 0.15s" }}>{n.icon}</span>
              <span style={{ fontSize: 10, fontWeight: active ? 700 : 400, color: active ? C.ocean : C.textMute, letterSpacing: "0.03em", transition: "color 0.15s" }}>{n.label}</span>
              {active && (
                <div style={{
                  position: "absolute", bottom: -2, width: 24, height: 3,
                  background: `linear-gradient(90deg, ${C.ocean}, #0284c7)`,
                  borderRadius: 2, boxShadow: `0 0 8px ${C.ocean}`,
                }} />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<Dashboard />);
</script>
</body>
</html>
"""

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(HTML)

print("Dashboard erstellt:", output_path)
print("Öffne Browser...")
webbrowser.open(f"file:///{output_path.replace(os.sep, '/')}")
