"""
Familien-Dashboard – Inspiriert von den Referenz-Fotos
Pastell-Cards + dunkle Sidebar + optionaler Kreide-Font
"""
import webbrowser, os, base64, json, mimetypes, sys

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

def load_images(folder, as_path=False):
    result = {}
    path = os.path.join(ASSETS, folder)
    if not os.path.exists(path):
        return result
    for fname in sorted(os.listdir(path)):
        if not os.path.splitext(fname)[1].lower() in {".jpg",".jpeg",".png",".gif",".webp"}:
            continue
        fpath = os.path.join(path, fname)
        if as_path:
            # Direkte file://-URL – kein Base64, sofort ladend
            url = "file:///" + fpath.replace("\\", "/")
            name = os.path.splitext(fname)[0].lower()
            result[name] = url
        else:
            mime  = mimetypes.guess_type(fpath)[0] or "image/png"
            with open(fpath, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            name = os.path.splitext(fname)[0].lower()
            result[name] = f"data:{mime};base64,{b64}"
        print(f"  Bild geladen: {folder}/{fname}")
    return result

HTML = r"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Family Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;600;700&family=Inter:wght@300;400;500;600;700;800;900&family=Lora:wght@400;500;600;700&display=swap" rel="stylesheet">
  <!-- Twemoji = Twitter/WhatsApp-style Emojis (kostenlos, CDN) -->
  <script src="https://twemoji.maxcdn.com/v/latest/twemoji.min.js" crossorigin="anonymous"></script>

  <style>
    /* Twemoji: alle Emojis als hübsche SVG-Bilder */
    img.emoji {
      height: 1.2em;
      width: 1.2em;
      vertical-align: -0.15em;
      display: inline-block;
    }
    * { margin:0; padding:0; box-sizing:border-box; }

    /* ── BASIS-THEMES ──────────────────────────────────────────────────────── */
    body { background:#e2dbd0; }

    /* Pastell Cards */
    .card-yellow  { background:#fdf0e8; border:1.5px solid #e8c4a0; }
    .card-pink    { background:#fce7f3; border:1.5px solid #fbcfe8; }
    .card-green   { background:#d1fae5; border:1.5px solid #a7f3d0; }
    .card-blue    { background:#dbeafe; border:1.5px solid #bfdbfe; }
    .card-purple  { background:#ede9fe; border:1.5px solid #ddd6fe; }
    .card-peach   { background:#ffedd5; border:1.5px solid #fed7aa; }
    .card-cream   { background:#faf7f2; border:1.5px solid #e8e0d0; }
    .card-teal    { background:#6bbdb5; border:1.5px solid #5aada5; color:#1d4a46; }
    .card-teal-light { background:#e8f5f4; border:1.5px solid #a8dbd7; }

    /* ── FONTS ──────────────────────────────────────────────────────────────── */
    .font-chalk  { font-family: 'Caveat', cursive; }
    .font-modern { font-family: 'Inter', sans-serif; }

    /* ── TRANSITIONS ─────────────────────────────────────────────────────── */
    * { transition-property: background,color,border-color,box-shadow,opacity;
        transition-duration: 0.15s; transition-timing-function: ease; }

    /* Sidebar */
    .sidebar-item { cursor:pointer; border-radius:12px; padding:10px 14px;
                    display:flex; align-items:center; gap:10px; }
    .sidebar-item:hover { background:rgba(0,0,0,0.08); }
    .sidebar-item.active { background:rgba(0,0,0,0.18); }

    /* Calendar day */
    .cal-day { border-radius:10px; min-height:52px; cursor:pointer;
               display:flex; flex-direction:column; align-items:center;
               padding:4px 2px; }
    .cal-day:hover { filter:brightness(0.93); }

    /* Checkbox custom */
    .check-box { width:20px; height:20px; border-radius:5px; border:2px solid;
                 display:flex; align-items:center; justify-content:center;
                 cursor:pointer; flex-shrink:0; }

    ::-webkit-scrollbar { width:4px; }
    ::-webkit-scrollbar-thumb { background:#d1c4b0; border-radius:2px; }
  </style>
</head>
<body>
<div id="root"></div>

<script type="text/babel">
const { useState, useEffect } = React;

// ── API CLIENT ────────────────────────────────────────────────────────────────
const API = "http://localhost:8000";
const apiGet  = (p)    => fetch(API+p).then(r=>r.json()).catch(()=>[]);
const apiPost = (p,b)  => fetch(API+p,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)}).then(r=>r.json()).catch(()=>null);
const apiPut  = (p)    => fetch(API+p,{method:"PUT"}).then(r=>r.json()).catch(()=>null);
const apiDel  = (p)    => fetch(API+p,{method:"DELETE"}).catch(()=>null);

// ── THEMES ───────────────────────────────────────────────────────────────────
const THEMES = {
  familie: {
    name: "🏡 Familie",
    bg: "#ede8dc",        // warmes Creme wie im Bild
    sidebar: "#5aada5",   // Teal wie im Bild
    sidebarText: "#f0faf9",
    text: "#3d2b1f",      // dunkles Braun
    textSub: "#7a6050",
    card: "#faf6f0",      // helles Creme
    border: "#c8b89a",
    accent: "#6bbdb5",    // Teal
    headFont: "'Lora', serif",
  },
  planner: {
    name: "📓 Planner",
    bg: "#e2dbd0",
    sidebar: "#2d2d2d",
    sidebarText: "#e2dbd0",
    text: "#2d2015",
    textSub: "#6b5a40",
    card: "#faf7f2",
    border: "#e0d5c0",
    accent: "#c2855a",
    headFont: "'Lora', serif",
  },
  pastel: {
    name: "🎨 Pastell",
    bg: "#fef9f5",
    sidebar: "#1a1a2e",
    sidebarText: "#f0f0ff",
    text: "#1a1020",
    textSub: "#5a4060",
    card: "#ffffff",
    border: "#e8d5f0",
    accent: "#7c3aed",
  },
  coastal: {
    name: "🌊 Coastal",
    bg: "#f0f7ff",
    sidebar: "#0c2340",
    sidebarText: "#e0f0ff",
    text: "#0c2340",
    textSub: "#2c5070",
    card: "#ffffff",
    border: "#c0ddf0",
    accent: "#0ea5e9",
  },
  chalk: {
    name: "🖊 Kreidetafel",
    bg: "#2a3a2a",        // dunkelgrüne Tafel
    sidebar: "#1a2a1a",
    sidebarText: "#d8e8d0",
    text: "#e8f0e0",
    textSub: "#a0b890",
    card: "#354535",
    border: "#4a6040",
    accent: "#c8e080",    // Kreide-Gelb
  },
};

// ── EVENT COLORS ──────────────────────────────────────────────────────────────
const CAL_COLORS = [
  "#c2855a","#f87171","#34d399","#60a5fa","#a78bfa","#fb923c","#f472b6",
];

// ── DATA ──────────────────────────────────────────────────────────────────────
const CARD_STYLES = ["card-yellow","card-pink","card-green","card-blue","card-purple","card-peach","card-cream"];
const TODO_LISTS  = [
  { name:"Einkauf",    icon:"🛒", color:"#fdf0e8", border:"#e8c4a0", check:"#c2855a" },
  { name:"Haushalt",   icon:"🏡", color:"#d1fae5", border:"#a7f3d0", check:"#10b981" },
  { name:"Erledigung", icon:"✅", color:"#ede9fe", border:"#ddd6fe", check:"#7c3aed" },
];

const weekMeals = [
  {d:"Mo",m:"🍝 Pasta"},  {d:"Di",m:"🌮 Tacos"}, {d:"Mi",m:"🐟 Fisch"},
  {d:"Do",m:"🍜 Ramen"},  {d:"Fr",m:"🍕 Pizza"},  {d:"Sa",m:"🍔 Burger"}, {d:"So",m:"🥩 Braten"},
];

const fmtTime = (dt) => dt ? new Date(dt).toLocaleTimeString("de-DE",{hour:"2-digit",minute:"2-digit"}) : "";
const todayStr = () => { const n=new Date(); return `${n.getFullYear()}-${String(n.getMonth()+1).padStart(2,"0")}-${String(n.getDate()).padStart(2,"0")}`; };
const isToday  = (dt) => dt && dt.startsWith(todayStr());

// ── EMOJI SETS ────────────────────────────────────────────────────────────────
const EMOJI_SETS = [
  { key:"twemoji",  label:"Twitter / WhatsApp", icon:"https://twemoji.maxcdn.com/v/latest/svg/1f600.svg" },
  { key:"system",   label:"System (Standard)",  icon:null },
  { key:"openmoji", label:"OpenMoji (bunt)",    icon:"https://openmoji.org/data/color/svg/1F600.svg" },
  { key:"noto",     label:"Google Noto",        icon:"https://raw.githubusercontent.com/googlefonts/noto-emoji/main/svg/emoji_u1f600.svg" },
];

function EmojiToggle({ sidebarText }) {
  const [current, setCurrent] = useState("twemoji");
  const [open, setOpen]       = useState(false);

  const apply = (key) => {
    window._emojiSet = key;
    setCurrent(key);
    setOpen(false);
    if (key === "system") {
      // Twemoji-Bilder entfernen → originale Unicode-Emojis zeigen
      document.querySelectorAll("img.emoji").forEach(img => {
        const span = document.createElement("span");
        span.textContent = img.alt;
        img.replaceWith(span);
      });
    } else if (key === "twemoji") {
      twemoji.parse(document.body, { folder:"svg", ext:".svg" });
    } else if (key === "openmoji") {
      twemoji.parse(document.body, {
        base:"https://openmoji.org/data/color/svg/",
        folder:"", ext:".svg",
        callback:(icon) => icon.toUpperCase(),
      });
    } else if (key === "noto") {
      twemoji.parse(document.body, {
        base:"https://raw.githubusercontent.com/googlefonts/noto-emoji/main/svg/",
        folder:"", ext:".svg",
        callback:(icon) => `emoji_u${icon.replace(/-/g,"_")}`,
      });
    }
  };

  const cur = EMOJI_SETS.find(e=>e.key===current);
  return (
    <div style={{ position:"relative" }}>
      <button onClick={()=>setOpen(!open)} style={{
        width:"100%", background: open?"rgba(255,255,255,0.15)":"transparent",
        border:"1px solid rgba(255,255,255,0.1)", borderRadius:8,
        padding:"6px 10px", color:sidebarText, cursor:"pointer",
        textAlign:"left", fontSize:12, display:"flex", alignItems:"center", gap:6,
      }}>
        <span style={{ fontSize:16 }}>😀</span>
        <span style={{ flex:1, opacity:.8 }}>{cur?.label}</span>
        <span style={{ opacity:.4 }}>{open?"▲":"▼"}</span>
      </button>
      {open && (
        <div style={{
          position:"absolute", bottom:"calc(100% + 6px)", left:0, right:0,
          background:"#1a1a1a", border:"1px solid rgba(255,255,255,0.15)",
          borderRadius:12, padding:6, zIndex:200,
          boxShadow:"0 8px 24px rgba(0,0,0,0.4)",
        }}>
          {EMOJI_SETS.map(es => (
            <button key={es.key} onClick={()=>apply(es.key)} style={{
              width:"100%", background: current===es.key?"rgba(255,255,255,0.12)":"transparent",
              border:"none", borderRadius:8, padding:"8px 10px", cursor:"pointer",
              display:"flex", alignItems:"center", gap:8, textAlign:"left",
            }}>
              {es.icon
                ? <img src={es.icon} style={{width:20,height:20}} alt="emoji preview"/>
                : <span style={{fontSize:18}}>😀</span>}
              <span style={{ color:"#f0f0f0", fontSize:12, fontWeight: current===es.key?700:400 }}>{es.label}</span>
              {current===es.key && <span style={{ marginLeft:"auto", fontSize:10, color:"#a0a0a0" }}>✓ aktiv</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ── FOTO SLIDER ───────────────────────────────────────────────────────────────
function PhotoSlider({ cardBase, T, ff, hf, chalk }) {
  const photos = window.PHOTOS || [];
  const [idx,  setIdx] = useState(0);
  const [fade, setFade] = useState(true);
  const acc = T.accent || "#c2855a";

  useEffect(() => {
    if (photos.length < 2) return;
    const t = setInterval(() => go(1), 5000);
    return () => clearInterval(t);
  }, [idx, photos.length]);

  const go = (dir) => {
    setFade(false);
    setTimeout(() => { setIdx(i => (i + dir + photos.length) % photos.length); setFade(true); }, 180);
  };

  return (
    <div style={{ ...cardBase, background:T.card, border:`1.5px solid ${T.border}`,
                  flex:1, minHeight:0, display:"flex", flexDirection:"column" }}>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:12 }}>
        <div style={{ fontSize: chalk?14:11, fontWeight:700, color:T.textSub, opacity:.7,
                      textTransform:"uppercase", letterSpacing:"0.1em", fontFamily:ff }}>Familienfotos</div>
        {photos.length > 1 &&
          <span style={{ color:T.textSub, fontSize: chalk?13:10, fontFamily:ff }}>{idx+1} / {photos.length}</span>}
      </div>

      {photos.length === 0 ? (
        <div style={{ flex:1, minHeight:200, display:"flex", flexDirection:"column", alignItems:"center",
                      justifyContent:"center", gap:10, background:T.border+"44", borderRadius:14 }}>
          <div style={{ fontSize:40 }}>📷</div>
          <div style={{ color:T.textSub, fontSize: chalk?15:12, fontFamily:ff, textAlign:"center" }}>
            Fotos in <strong>assets/photos/</strong> ablegen
          </div>
        </div>
      ) : (
        <div style={{ position:"relative", flex:1, minHeight:0, display:"flex", flexDirection:"column",
                      background:"#ffffff", borderRadius:14, overflow:"hidden",
                      alignItems:"center", justifyContent:"center" }}>
          <img src={photos[idx]} alt="" style={{
            maxWidth:"100%", maxHeight:"100%", objectFit:"contain", borderRadius:10, display:"block",
            opacity: fade?1:0, transition:"opacity 0.18s ease",
          }}/>
          {photos.length > 1 && (<>
            <button onClick={()=>go(-1)} style={{
              position:"absolute", left:8, top:"50%", transform:"translateY(-50%)",
              width:34, height:34, borderRadius:10, border:"none",
              background:"rgba(0,0,0,0.38)", color:"#fff", fontSize:20,
              cursor:"pointer", display:"flex", alignItems:"center", justifyContent:"center",
            }}>‹</button>
            <button onClick={()=>go(1)} style={{
              position:"absolute", right:8, top:"50%", transform:"translateY(-50%)",
              width:34, height:34, borderRadius:10, border:"none",
              background:"rgba(0,0,0,0.38)", color:"#fff", fontSize:20,
              cursor:"pointer", display:"flex", alignItems:"center", justifyContent:"center",
            }}>›</button>
            <div style={{ display:"flex", justifyContent:"center", gap:6, marginTop:10 }}>
              {photos.map((_,i) => (
                <div key={i} onClick={()=>{setFade(false);setTimeout(()=>{setIdx(i);setFade(true);},150);}}
                  style={{ width:i===idx?20:7, height:7, borderRadius:4, cursor:"pointer",
                            background:i===idx?acc:T.border, transition:"all 0.3s" }}/>
              ))}
            </div>
          </>)}
        </div>
      )}
    </div>
  );
}

// ── MAIN ──────────────────────────────────────────────────────────────────────
function App() {
  const [themeKey, setThemeKey] = useState("planner");
  const [chalk,    setChalk]    = useState(false);
  const [page,     setPage]     = useState("heute");
  const [events,   setEvents]   = useState([]);
  const [todos,    setTodos]    = useState([]);
  const [loading,  setLoading]  = useState(true);

  const T = THEMES[themeKey];
  const ff = chalk ? "'Caveat', cursive" : "'Inter', sans-serif";
  const hf = chalk ? "'Caveat', cursive" : (T.headFont || "'Inter', sans-serif");

  const now     = new Date();
  const dateStr = now.toLocaleDateString("de-DE",{weekday:"long",day:"numeric",month:"long"});
  const dow     = ["So","Mo","Di","Mi","Do","Fr","Sa"][now.getDay()];

  useEffect(() => {
    const ym = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,"0")}`;
    Promise.all([apiGet(`/events/?date=${ym}`), apiGet("/todos/")])
      .then(([evts, tds]) => { setEvents(evts); setTodos(tds); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const toggleTodo = async (id) => {
    const u = await apiPut(`/todos/${id}/done`);
    if (u) setTodos(ts => ts.map(t => t.id===id ? u : t));
  };

  // Shared styles
  const cardBase = {
    borderRadius: 20, padding: 20,
    boxShadow: "0 2px 12px rgba(0,0,0,0.06)",
    fontFamily: ff,
  };

  const Tag = ({ children, bg="#fdf0e8", color="#7a3f20", border="#e8c4a0" }) => (
    <span style={{ background:bg, color, border:`1px solid ${border}`, borderRadius:20,
                   padding:"2px 10px", fontSize:11, fontWeight:700, fontFamily:ff }}>
      {children}
    </span>
  );

  // ── HEUTE ──────────────────────────────────────────────────────────────────
  const HeutePage = () => {
    const todayEvts = events.filter(e => isToday(e.start_datetime))
                            .sort((a,b) => a.start_datetime.localeCompare(b.start_datetime));
    const openTodos = todos.filter(t => !t.done);
    const acc = T.accent || "#c2855a";
    const accLight = acc + "22";
    const accBorder = acc + "55";

    // Tageszeit-Gruß
    const h = now.getHours();
    const gruss = h < 12 ? "Guten Morgen" : h < 17 ? "Guten Tag" : "Guten Abend";

    return (
      <div style={{ display:"flex", flexDirection:"column", gap:16, height:"100%" }}>

        {/* ── BANNER ── */}
        <div style={{ ...cardBase, padding:"22px 28px",
                      background:`linear-gradient(120deg, ${acc}, ${acc}cc)`,
                      border:"none", display:"flex", justifyContent:"space-between", alignItems:"center",
                      boxShadow:`0 4px 24px ${acc}44` }}>
          <div>
            <div style={{ fontSize: chalk?13:10, fontWeight:700, color:"rgba(255,255,255,0.65)",
                          letterSpacing:"0.12em", textTransform:"uppercase", fontFamily:ff, marginBottom:4 }}>
              {dateStr}
            </div>
            <div style={{ fontSize: chalk?44:34, fontWeight:700, color:"#fff", fontFamily:hf, lineHeight:1.1 }}>
              {gruss}! 🤙
            </div>
            <div style={{ marginTop:10, display:"flex", gap:8 }}>
              <span style={{ background:"rgba(255,255,255,0.2)", color:"#fff", borderRadius:20,
                              padding:"4px 12px", fontSize: chalk?14:11, fontWeight:600, fontFamily:ff }}>
                📅 {loading?"…":todayEvts.length} Termine
              </span>
              <span style={{ background:"rgba(255,255,255,0.2)", color:"#fff", borderRadius:20,
                              padding:"4px 12px", fontSize: chalk?14:11, fontWeight:600, fontFamily:ff }}>
                ✅ {loading?"…":openTodos.length} offen
              </span>
              <span style={{ background:"rgba(255,255,255,0.2)", color:"#fff", borderRadius:20,
                              padding:"4px 12px", fontSize: chalk?14:11, fontWeight:600, fontFamily:ff }}>
                ⛅ 18°
              </span>
            </div>
          </div>
          <div style={{ display:"flex", gap:10 }}>
            {[["👩","#7c3aed"],["👨","#0ea5e9"],["👶","#c2855a"]].map(([e,c])=>(
              <div key={e} style={{ width:44, height:44, borderRadius:"50%",
                                     background:"rgba(255,255,255,0.25)",
                                     display:"flex", alignItems:"center", justifyContent:"center",
                                     fontSize:22, border:"2px solid rgba(255,255,255,0.4)" }}>{e}</div>
            ))}
          </div>
        </div>

        {/* ── HAUPTINHALT: 2 SPALTEN ── */}
        <div style={{ display:"grid", gridTemplateColumns:"1.1fr 0.9fr", gap:16, alignItems:"stretch",
                      flex:1, overflow:"hidden" }}>

          {/* LINKE SPALTE – Tagesplan */}
          <div style={{ display:"flex", flexDirection:"column", gap:16, minHeight:0, overflow:"hidden" }}>

            {/* TERMINE */}
            <div style={{ ...cardBase, background:T.card, border:`1.5px solid ${T.border}` }}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:16 }}>
                <div style={{ fontSize: chalk?20:13, fontWeight:700, color:T.textSub,
                              textTransform:"uppercase", letterSpacing:"0.1em", fontFamily:ff }}>
                  Heute · Tagesplan
                </div>
                <span style={{ background:accLight, color:acc, border:`1px solid ${accBorder}`,
                                borderRadius:20, padding:"3px 10px", fontSize: chalk?14:11, fontWeight:700, fontFamily:ff }}>
                  {todayEvts.length} Termine
                </span>
              </div>
              {loading
                ? <div style={{ color:T.textSub, fontFamily:ff }}>Laden…</div>
                : todayEvts.length === 0
                ? <div style={{ color:T.textSub, fontSize: chalk?16:14, fontFamily:ff, padding:"12px 0" }}>
                    Freier Tag – genieß ihn! 🌿
                  </div>
                : todayEvts.map((e,i) => {
                  const col = CAL_COLORS[i % CAL_COLORS.length];
                  return (
                    <div key={e.id} style={{ display:"flex", alignItems:"center", gap:12, marginBottom:8,
                                              borderRadius:14, padding:"12px 14px",
                                              background:col+"18", borderLeft:`4px solid ${col}` }}>
                      <span style={{ color:col, fontWeight:800, fontSize: chalk?16:12,
                                      minWidth:40, fontFamily:ff }}>{fmtTime(e.start_datetime)}</span>
                      <div style={{ flex:1 }}>
                        <div style={{ color:T.text, fontSize: chalk?18:14, fontWeight:600, fontFamily:hf }}>{e.title}</div>
                        {e.description && <div style={{ color:T.textSub, fontSize: chalk?14:11, fontFamily:ff, marginTop:2 }}>{e.description}</div>}
                      </div>
                      <div style={{ width:8, height:8, borderRadius:"50%", background:col }}/>
                    </div>
                  );
                })
              }
            </div>

            {/* WETTER */}
            <div style={{ ...cardBase, background:T.card, border:`1.5px solid ${T.border}` }}>
              <div style={{ fontSize: chalk?14:11, fontWeight:700, color:T.textSub, opacity:.7,
                            textTransform:"uppercase", letterSpacing:"0.1em", marginBottom:12, fontFamily:ff }}>Wetter</div>
              <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between" }}>
                <div style={{ display:"flex", alignItems:"center", gap:12 }}>
                  <span style={{ fontSize:48 }}>⛅</span>
                  <div>
                    <div style={{ fontSize: chalk?42:32, fontWeight:900, color:T.text, lineHeight:1, fontFamily:hf }}>18°</div>
                    <div style={{ color:T.textSub, fontSize: chalk?14:11, fontFamily:ff }}>Teilweise bewölkt</div>
                  </div>
                </div>
                <div style={{ display:"flex", gap:16 }}>
                  {[["Fr","🌧","14°"],["Sa","☀️","22°"],["So","☀️","21°"]].map(([d,ic,t])=>(
                    <div key={d} style={{ textAlign:"center" }}>
                      <div style={{ color:T.textSub, fontSize: chalk?13:10, fontFamily:ff }}>{d}</div>
                      <div style={{ fontSize:20, margin:"4px 0" }}>{ic}</div>
                      <div style={{ color:T.text, fontSize: chalk?15:12, fontWeight:700, fontFamily:ff }}>{t}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* FOTO SLIDER */}
            <PhotoSlider cardBase={cardBase} T={T} ff={ff} hf={hf} chalk={chalk} />

          </div>{/* Ende linke Spalte */}

          {/* RECHTE SPALTE – Todos + Essen + Buttons */}
          <div style={{ display:"flex", flexDirection:"column", gap:16, overflow:"hidden" }}>

            {/* OFFENE TODOS */}
            <div style={{ ...cardBase, background:T.card, border:`1.5px solid ${T.border}` }}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:14 }}>
                <div style={{ fontSize: chalk?20:13, fontWeight:700, color:T.textSub,
                              textTransform:"uppercase", letterSpacing:"0.1em", fontFamily:ff }}>
                  Offene Aufgaben
                </div>
                <span style={{ background:accLight, color:acc, border:`1px solid ${accBorder}`,
                                borderRadius:20, padding:"3px 10px", fontSize: chalk?14:11, fontWeight:700, fontFamily:ff }}>
                  {openTodos.length}
                </span>
              </div>
              {openTodos.length === 0
                ? <div style={{ color:T.textSub, fontSize: chalk?16:13, fontFamily:ff }}>Alles erledigt! 🎉</div>
                : openTodos.slice(0,5).map(t => (
                  <div key={t.id} style={{ display:"flex", alignItems:"center", gap:10, marginBottom:8,
                                            padding:"8px 0", borderBottom:`1px solid ${T.border}` }}>
                    <div onClick={()=>toggleTodo(t.id)} style={{
                      width:20, height:20, borderRadius:6, border:`2px solid ${acc}`,
                      background: t.done ? acc : "transparent",
                      display:"flex", alignItems:"center", justifyContent:"center",
                      cursor:"pointer", flexShrink:0,
                    }}>
                      {t.done && <span style={{ color:"#fff", fontSize:11, fontWeight:900 }}>✓</span>}
                    </div>
                    <span style={{ flex:1, color: t.done ? T.textSub : T.text,
                                    fontSize: chalk?16:13, fontFamily:ff,
                                    textDecoration: t.done ? "line-through" : "none" }}>{t.text}</span>
                    <span style={{ fontSize: chalk?12:10, color:T.textSub, fontFamily:ff, opacity:.6 }}>{t.list_name}</span>
                  </div>
                ))
              }
            </div>

            {/* ESSEN */}
            <div style={{ ...cardBase, background:T.card, border:`1.5px solid ${T.border}` }}>
              <div style={{ fontSize: chalk?14:11, fontWeight:700, color:T.textSub, opacity:.7,
                            textTransform:"uppercase", letterSpacing:"0.1em", marginBottom:12, fontFamily:ff }}>Essen heute</div>
              {[["🌅 Früh","Açaí Bowl"],["☀️ Mittag","Fish Tacos"],["🌙 Abend","Poke Bowl"]].map(([label,meal])=>(
                <div key={meal} style={{ display:"flex", justifyContent:"space-between", alignItems:"center",
                                          padding:"8px 0", borderBottom:`1px solid ${T.border}` }}>
                  <span style={{ color:T.textSub, fontSize: chalk?14:11, fontFamily:ff }}>{label}</span>
                  <span style={{ color:T.text, fontSize: chalk?16:13, fontWeight:600, fontFamily:ff }}>{meal}</span>
                </div>
              ))}
            </div>

            {/* SCHNELL-BUTTONS */}
            <div style={{ ...cardBase, background:T.card, border:`1.5px solid ${T.border}` }}>
              <div style={{ fontSize: chalk?14:11, fontWeight:700, color:T.textSub, opacity:.7,
                            textTransform:"uppercase", letterSpacing:"0.1em", marginBottom:12, fontFamily:ff }}>Schnell-Buttons</div>
              <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:8 }}>
                {[["🛒 Einkauf","einkauf"],["🍕 Pizza","pizza"],
                  ["🏥 Arzt","arzt"],["🚗 Fahrt","fahrt"],
                  ["📦 Paket","paket"],["🏄 Strand","strand"]].map(([l,key])=>{
                  const img = window.BTN_IMGS?.[key];
                  return (
                    <button key={l} style={{ background:T.card, border:`1.5px solid ${accBorder}`,
                                              borderRadius:12, padding: chalk?"14px 6px":"11px 6px",
                                              color:acc, fontSize: chalk?16:12, fontWeight:700,
                                              cursor:"pointer", fontFamily:ff,
                                              display:"flex", flexDirection:"column", alignItems:"center", gap:4 }}
                      onMouseEnter={e=>{ e.currentTarget.style.background=acc; e.currentTarget.style.color="#fff"; }}
                      onMouseLeave={e=>{ e.currentTarget.style.background=T.card; e.currentTarget.style.color=acc; }}>
                      {img
                        ? <img src={img} style={{ width:28, height:28, objectFit:"contain" }} />
                        : <span style={{ fontSize:20 }}>{l.split(" ")[0]}</span>}
                      <span style={{ fontSize: chalk?12:10 }}>{l.split(" ").slice(1).join(" ")}</span>
                    </button>
                  );
                })}
              </div>
            </div>

          </div>
        </div>
      </div>
    );
  };

  // ── TODOS ──────────────────────────────────────────────────────────────────
  const TodosPage = () => {
    const [newText,  setNewText]  = useState({});
    const [addingTo, setAddingTo] = useState(null);

    const addTodo = async (list) => {
      const txt = (newText[list]||"").trim();
      if (!txt) return;
      const c = await apiPost("/todos/", {text:txt, list_name:list, person:"family"});
      if (c) setTodos(ts => [c,...ts]);
      setNewText(n=>({...n,[list]:""}));
      setAddingTo(null);
    };
    const delTodo = async (id) => { await apiDel(`/todos/${id}`); setTodos(ts=>ts.filter(t=>t.id!==id)); };

    return (
      <div style={{ display:"flex", flexDirection:"column", gap:16 }}>
        {TODO_LISTS.map(lst => {
          const items = todos.filter(t=>t.list_name===lst.name);
          const open  = items.filter(t=>!t.done);
          const done  = items.filter(t=>t.done);
          return (
            <div key={lst.name} style={{ ...cardBase, background:lst.color, border:`2px solid ${lst.border}` }}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:14 }}>
                <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                  <span style={{ fontSize:20 }}>{lst.icon}</span>
                  <span style={{ fontSize: chalk?22:15, fontWeight:700, color:T.text, fontFamily:ff }}>{lst.name}</span>
                  {open.length>0 && <Tag bg={lst.color} color={T.text} border={lst.border}>{open.length}</Tag>}
                </div>
                <button onClick={()=>setAddingTo(addingTo===lst.name?null:lst.name)}
                  style={{ background:lst.check+"22", border:`1.5px solid ${lst.check}55`, color:lst.check,
                            borderRadius:10, padding:"5px 14px", cursor:"pointer",
                            fontSize: chalk?16:13, fontWeight:700, fontFamily:ff }}>
                  + Hinzufügen
                </button>
              </div>

              {addingTo===lst.name && (
                <div style={{ display:"flex", gap:8, marginBottom:12 }}>
                  <input autoFocus value={newText[lst.name]||""}
                    onChange={e=>setNewText(n=>({...n,[lst.name]:e.target.value}))}
                    onKeyDown={e=>{if(e.key==="Enter")addTodo(lst.name);if(e.key==="Escape")setAddingTo(null);}}
                    placeholder="Neues Todo…"
                    style={{ flex:1, background:"rgba(255,255,255,0.6)", border:`1.5px solid ${lst.border}`,
                              borderRadius:12, padding:"10px 14px", color:T.text,
                              fontSize: chalk?18:14, fontFamily:ff, outline:"none" }}/>
                  <button onClick={()=>addTodo(lst.name)}
                    style={{ background:lst.check, border:"none", borderRadius:12, padding:"10px 18px",
                              color:"#fff", cursor:"pointer", fontWeight:700, fontSize: chalk?18:14, fontFamily:ff }}>OK</button>
                </div>
              )}

              {open.map(t=>(
                <div key={t.id} style={{ display:"flex", alignItems:"center", gap:12, marginBottom:8,
                                          background:"rgba(255,255,255,0.4)", borderRadius:12, padding:"8px 12px" }}>
                  <div className="check-box" onClick={()=>toggleTodo(t.id)}
                    style={{ borderColor:lst.check, background:"transparent" }}/>
                  <span style={{ flex:1, color:T.text, fontSize: chalk?18:14, fontFamily:ff }}>{t.text}</span>
                  <button onClick={()=>delTodo(t.id)}
                    style={{ background:"transparent", border:"none", cursor:"pointer",
                              color:T.textSub, fontSize:20, fontFamily:ff, lineHeight:1 }}
                    onMouseEnter={e=>e.currentTarget.style.color="#ef4444"}
                    onMouseLeave={e=>e.currentTarget.style.color=T.textSub}>×</button>
                </div>
              ))}

              {done.length>0 && (
                <details style={{ marginTop:6 }}>
                  <summary style={{ color:T.textSub, fontSize: chalk?16:12, cursor:"pointer",
                                    fontFamily:ff, padding:"4px 0" }}>
                    ✓ Erledigt ({done.length})
                  </summary>
                  {done.map(t=>(
                    <div key={t.id} style={{ display:"flex", alignItems:"center", gap:12, marginTop:6,
                                              background:"rgba(255,255,255,0.25)", borderRadius:12, padding:"8px 12px" }}>
                      <div className="check-box" onClick={()=>toggleTodo(t.id)}
                        style={{ borderColor:lst.check, background:lst.check }}>
                        <span style={{ color:"#fff", fontSize:13, fontWeight:800 }}>✓</span>
                      </div>
                      <span style={{ flex:1, color:T.textSub, fontSize: chalk?17:13,
                                      textDecoration:"line-through", fontFamily:ff }}>{t.text}</span>
                    </div>
                  ))}
                </details>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  // ── KALENDER ──────────────────────────────────────────────────────────────
  const KalenderPage = () => {
    const [month, setMonth] = useState(now.getMonth()+1);
    const [year,  setYear]  = useState(now.getFullYear());
    const [calEvts, setCalEvts] = useState(events);

    const MONTHS_LONG = ["Januar","Februar","März","April","Mai","Juni",
                         "Juli","August","September","Oktober","November","Dezember"];

    // Monat wechseln → neue Events laden
    const goMonth = (dir) => {
      let m = month + dir, y = year;
      if (m < 1)  { m = 12; y -= 1; }
      if (m > 12) { m = 1;  y += 1; }
      setMonth(m); setYear(y);
      const ym = `${y}-${String(m).padStart(2,"0")}`;
      apiGet(`/events/?date=${ym}`).then(ev => setCalEvts(ev));
    };

    const daysInMonth = new Date(year, month, 0).getDate();
    // Montag = 0 … Sonntag = 6
    const startDow = (new Date(year, month-1, 1).getDay() + 6) % 7;
    const evDay = d => calEvts.filter(e => {
      const dt = new Date(e.start_datetime);
      return dt.getFullYear()===year && (dt.getMonth()+1)===month && dt.getDate()===d;
    });
    const isToday = d => year===now.getFullYear() && month===(now.getMonth()+1) && d===now.getDate();
    const accent = T.accent || "#6bbdb5";

    const NavBtn = ({dir, label}) => (
      <button onClick={()=>goMonth(dir)} style={{
        width:44, height:44, borderRadius:14,
        background: T.card, border:`1.5px solid ${T.border}`,
        boxShadow:"0 2px 8px rgba(0,0,0,0.08)",
        fontSize:20, fontWeight:700, cursor:"pointer",
        color: accent, display:"flex", alignItems:"center", justifyContent:"center",
        transition:"all 0.15s",
      }}
        onMouseEnter={e=>e.currentTarget.style.background=accent}
        onMouseLeave={e=>e.currentTarget.style.background=T.card}
      >{label}</button>
    );

    return (
      <div style={{ display:"flex", flexDirection:"column", gap:16 }}>
        <div style={{ ...cardBase, background:T.card, border:`1.5px solid ${T.border}` }}>

          {/* Header: Prev – Monat/Jahr – Next */}
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:24 }}>
            <NavBtn dir={-1} label="‹" />
            <span style={{ fontFamily:hf, fontSize: chalk?30:22, fontWeight:700, color:accent }}>
              {MONTHS_LONG[month-1]} {year}
            </span>
            <NavBtn dir={1} label="›" />
          </div>

          {/* Wochentage */}
          <div style={{ display:"grid", gridTemplateColumns:"repeat(7,1fr)", marginBottom:8 }}>
            {["Mo","Di","Mi","Do","Fr","Sa","So"].map(d=>(
              <div key={d} style={{ textAlign:"center", fontSize: chalk?16:12, fontWeight:700,
                                     color:T.textSub, fontFamily:ff, paddingBottom:8 }}>{d}</div>
            ))}
          </div>

          {/* Tage */}
          <div style={{ display:"grid", gridTemplateColumns:"repeat(7,1fr)", gap:4 }}>
            {Array.from({length:startDow}).map((_,i)=><div key={"e"+i}/>)}
            {Array.from({length:daysInMonth},(_,i)=>i+1).map(d=>{
              const de = evDay(d);
              const isTd = isToday(d);
              return (
                <div key={d} style={{
                  display:"flex", flexDirection:"column", alignItems:"center",
                  padding:"6px 2px", borderRadius:12, cursor:"pointer",
                  background: isTd ? accent : "transparent",
                  transition:"all 0.15s",
                }}
                  onMouseEnter={e=>{ if(!isTd) e.currentTarget.style.background=accent+"22"; }}
                  onMouseLeave={e=>{ if(!isTd) e.currentTarget.style.background="transparent"; }}
                >
                  <span style={{
                    fontSize: chalk?18:15, fontWeight: isTd?800:500,
                    color: isTd?"#fff" : T.text, fontFamily:ff,
                    lineHeight:1, marginBottom:4,
                  }}>{String(d).padStart(2,"0")}</span>
                  {/* Event-Dots */}
                  <div style={{ display:"flex", gap:2, flexWrap:"wrap", justifyContent:"center" }}>
                    {de.slice(0,3).map((e,i)=>(
                      <span key={i} title={e.title} style={{
                        width:6, height:6, borderRadius:"50%",
                        background: isTd?"rgba(255,255,255,0.8)" : (e.color||accent),
                        display:"block",
                      }}/>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Event-Liste des Monats */}
        {calEvts.length > 0 && (
          <div style={{ ...cardBase, background:T.card, border:`1.5px solid ${T.border}` }}>
            <div style={{ fontSize: chalk?18:12, fontWeight:700, color:T.textSub, opacity:.7,
                          textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:12, fontFamily:ff }}>
              Termine {MONTHS_LONG[month-1]}
            </div>
            {calEvts.sort((a,b)=>a.start_datetime.localeCompare(b.start_datetime)).map((e,i)=>{
              const col = e.color || CAL_COLORS[i%CAL_COLORS.length];
              const dt = new Date(e.start_datetime);
              return (
                <div key={e.id} style={{ display:"flex", alignItems:"center", gap:12, marginBottom:8,
                                          background:col+"18", border:`1.5px solid ${col}44`,
                                          borderRadius:12, padding:"10px 14px" }}>
                  <div style={{ background:col, color:"#fff", borderRadius:8, padding:"4px 10px",
                                  fontSize: chalk?15:11, fontWeight:700, fontFamily:ff, minWidth:32, textAlign:"center" }}>
                    {dt.getDate()}
                  </div>
                  <span style={{ flex:1, color:T.text, fontSize: chalk?17:13, fontFamily:ff }}>{e.title}</span>
                  <span style={{ color:T.textSub, fontSize: chalk?14:11, fontFamily:ff }}>{fmtTime(e.start_datetime)}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  };

  // ── SPEISEPLAN ─────────────────────────────────────────────────────────────
  const SpeisePage = () => (
    <div className="card-cream" style={cardBase}>
      <div style={{ fontSize: chalk?22:13, fontWeight:700, color:T.textSub, opacity:.7,
                    textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:16, fontFamily:ff }}>
        Speiseplan diese Woche
      </div>
      {weekMeals.map(m=>(
        <div key={m.d} style={{ display:"flex", alignItems:"center", gap:14, marginBottom:8,
                                  background: m.d===dow?acc+"22":"rgba(255,255,255,0.4)",
                                  border: m.d===dow?`1.5px solid ${acc}`:"1.5px solid transparent",
                                  borderRadius:14, padding:"10px 16px" }}>
          <span style={{ fontFamily:ff, fontWeight:700, fontSize: chalk?18:14,
                          color: m.d===dow?acc:T.textSub, opacity: m.d===dow?1:.6, minWidth:28 }}>{m.d}</span>
          {m.d===dow && <Tag>HEUTE</Tag>}
          <span style={{ fontFamily:ff, fontSize: chalk?20:15, color:T.text }}>{m.meal}</span>
        </div>
      ))}
    </div>
  );

  // ── NAV ITEMS ─────────────────────────────────────────────────────────────
  const navItems = [
    { id:"heute",    icon:"🏠", label:"Heute"    },
    { id:"kalender", icon:"📅", label:"Kalender" },
    { id:"todos",    icon:"✅", label:"Todos"    },
    { id:"speise",   icon:"🍽️", label:"Essen"    },
  ];

  const pages = { heute:<HeutePage/>, kalender:<KalenderPage/>, todos:<TodosPage/>, speise:<SpeisePage/> };

  return (
    <div style={{ minHeight:"100vh", background:T.bg, display:"flex", fontFamily:ff }}>

      {/* ── SIDEBAR ── */}
      <div style={{ width:200, background:T.sidebar, display:"flex", flexDirection:"column",
                    padding:20, position:"fixed", top:0, bottom:0, left:0, zIndex:50,
                    boxShadow:"4px 0 20px rgba(0,0,0,0.15)" }}>

        {/* Logo */}
        <div style={{ marginBottom:32 }}>
          <div style={{ fontSize: chalk?28:22, fontWeight:700, color:T.sidebarText, fontFamily:hf, lineHeight:1.2 }}>
            Familien<br/>Dashboard
          </div>
          <div style={{ fontSize: chalk?14:11, color:T.sidebarText, opacity:.5, marginTop:4, fontFamily:ff }}>
            {now.toLocaleDateString("de-DE",{day:"numeric",month:"short"})}
          </div>
        </div>

        {/* Nav items */}
        <div style={{ display:"flex", flexDirection:"column", gap:4, flex:1 }}>
          {navItems.map(n=>(
            <div key={n.id} className={`sidebar-item ${page===n.id?"active":""}`}
              onClick={()=>setPage(n.id)}
              style={{ color:T.sidebarText, opacity:page===n.id?1:.6,
                        fontSize: chalk?18:14, fontFamily:ff, fontWeight:page===n.id?700:400 }}>
              <span style={{ fontSize:18 }}>{n.icon}</span>
              {n.label}
            </div>
          ))}
        </div>

        {/* Theme + Font switcher */}
        <div style={{ borderTop:`1px solid rgba(255,255,255,0.1)`, paddingTop:16, display:"flex", flexDirection:"column", gap:8 }}>
          <div style={{ color:T.sidebarText, opacity:.4, fontSize: chalk?13:10,
                        fontWeight:700, letterSpacing:"0.08em", textTransform:"uppercase", fontFamily:ff }}>
            Design
          </div>
          {Object.entries(THEMES).map(([k,th])=>(
            <button key={k} onClick={()=>setThemeKey(k)} style={{
              background: themeKey===k ? "rgba(255,255,255,0.15)" : "transparent",
              border: themeKey===k ? "1px solid rgba(255,255,255,0.3)" : "1px solid transparent",
              borderRadius:8, padding:"6px 10px", color:T.sidebarText,
              opacity:themeKey===k?1:.55, cursor:"pointer", textAlign:"left",
              fontSize: chalk?15:12, fontFamily:ff, fontWeight:themeKey===k?700:400,
            }}>
              {th.name}
            </button>
          ))}

          <div style={{ marginTop:8, display:"flex", flexDirection:"column", gap:6 }}>
            <button onClick={()=>setChalk(!chalk)} style={{
              width:"100%", background: chalk?"rgba(255,255,255,0.15)":"transparent",
              border: chalk?"1px solid rgba(255,255,255,0.3)":"1px solid rgba(255,255,255,0.1)",
              borderRadius:8, padding:"6px 10px", color:T.sidebarText,
              cursor:"pointer", fontFamily:"'Caveat', cursive", fontSize:16,
              textAlign:"left", fontWeight:chalk?700:400,
            }}>
              ✏️ {chalk ? "Kreide aktiv" : "Kreide-Schrift"}
            </button>
            <EmojiToggle sidebarText={T.sidebarText} />
          </div>
        </div>

        {/* Person avatars */}
        <div style={{ display:"flex", gap:8, marginTop:16 }}>
          {[["👩","#7c3aed"],["👨","#0ea5e9"],["👶","#c2855a"]].map(([e,c])=>(
            <div key={e} style={{ width:32, height:32, borderRadius:"50%", background:c,
                                    display:"flex", alignItems:"center", justifyContent:"center",
                                    fontSize:16, boxShadow:`0 0 8px ${c}66` }}>{e}</div>
          ))}
        </div>
      </div>

      {/* ── CONTENT ── */}
      <div style={{ flex:1, marginLeft:200, overflow:"hidden", padding:24,
                    height:"100vh", display:"flex", flexDirection:"column" }}>
        {pages[page]}
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);

// Twemoji nach jedem React-Render aktivieren
const observer = new MutationObserver(() => {
  if (window._emojiSet === "twemoji") {
    twemoji.parse(document.body, { folder:"svg", ext:".svg" });
  }
});
observer.observe(document.body, { childList:true, subtree:true });
window._emojiSet = "twemoji"; // Standard: Twemoji an
twemoji.parse(document.body, { folder:"svg", ext:".svg" });
</script>
</body>
</html>
"""

print("Lade Bilder aus assets/...")
btn_imgs   = load_images("buttons")
per_imgs   = load_images("personen")
photos     = load_images("photos", as_path=True)  # Direkte Pfade, kein Base64
print(f"  {len(btn_imgs)} Button-Bilder, {len(per_imgs)} Personen-Bilder, {len(photos)} Fotos")

all_photos = list(photos.values())
print(f"  Gesamt Fotos: {len(all_photos)}")

# Bilder als JS-Variablen vor dem React-Code einschleusen
img_script = f"""<script>
window.BTN_IMGS = {json.dumps(btn_imgs)};
window.PER_IMGS = {json.dumps(per_imgs)};
window.PHOTOS   = {json.dumps(all_photos)};
</script>"""
final_html = HTML.replace("<div id=\"root\"></div>", img_script + "\n<div id=\"root\"></div>")

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "design_preview.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(final_html)

print("Dashboard erstellt:", output_path)
print("Oeffne Browser...")
webbrowser.open(f"file:///{output_path.replace(os.sep, '/')}")
print()
print("Sidebar links: Theme wechseln + Kreide-Schrift an/aus")
