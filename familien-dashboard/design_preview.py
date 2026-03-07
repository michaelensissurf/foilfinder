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
            # HTTP-URL über Backend (funktioniert via http://localhost:8000)
            url = "http://localhost:8000/assets/" + folder + "/" + fname
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
  <script src="/assets/sbbUhr.js"></script>

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
    body { background:#e2dbd0; overflow:hidden; }
    #root {
      transform: scale(1.18);
      transform-origin: 0 0;
      width: calc(100% / 1.18);
      height: calc(100vh / 1.18);
    }

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

// ── DEMO EVENTS (werden genutzt wenn Backend keine Daten liefert) ─────────────
const makeDT = (dayOffset, h, m=0) => {
  const d = new Date(); d.setDate(d.getDate()+dayOffset);
  d.setHours(h,m,0,0); return d.toISOString();
};
const DEMO_EVENTS = [
  // ── Montag (heute -1 / morgen je nach Wochentag)
  { id:101, title:"Schule Abgabe",    person:"kind1", color:"#f15bb5", start_datetime:makeDT(-1,8,0),  end_datetime:makeDT(-1,9,0)  },
  { id:102, title:"Yoga",             person:"mama",  color:"#9b5de5", start_datetime:makeDT(-1,9,0),  end_datetime:makeDT(-1,10,0) },
  { id:103, title:"Work Meeting",     person:"papa",  color:"#00b4d8", start_datetime:makeDT(-1,10,0), end_datetime:makeDT(-1,11,30)},
  // ── Heute
  { id:201, title:"Kita Abholen",     person:"mama",  color:"#9b5de5", start_datetime:makeDT(0,8,30),  end_datetime:makeDT(0,9,0)   },
  { id:202, title:"Zahnarzt",         person:"papa",  color:"#00b4d8", start_datetime:makeDT(0,11,0),  end_datetime:makeDT(0,12,0)  },
  { id:203, title:"Fußball Training", person:"kind1", color:"#f15bb5", start_datetime:makeDT(0,14,0),  end_datetime:makeDT(0,15,30) },
  { id:204, title:"Klavierstunde",    person:"kind2", color:"#fb923c", start_datetime:makeDT(0,16,0),  end_datetime:makeDT(0,17,0)  },
  { id:205, title:"Familien-Pizza",   person:"family",color:"#10b981", start_datetime:makeDT(0,18,30), end_datetime:makeDT(0,20,0)  },
  // ── Morgen
  { id:301, title:"Supermarkt",       person:"mama",  color:"#9b5de5", start_datetime:makeDT(1,9,0),   end_datetime:makeDT(1,10,0)  },
  { id:302, title:"Homeoffice",       person:"papa",  color:"#00b4d8", start_datetime:makeDT(1,9,0),   end_datetime:makeDT(1,17,0)  },
  { id:303, title:"Schwimmen",        person:"kind2", color:"#fb923c", start_datetime:makeDT(1,15,0),  end_datetime:makeDT(1,16,30) },
  // ── Übermorgen
  { id:401, title:"Arzttermin",       person:"kind1", color:"#f15bb5", start_datetime:makeDT(2,10,0),  end_datetime:makeDT(2,11,0)  },
  { id:402, title:"Sport",            person:"papa",  color:"#00b4d8", start_datetime:makeDT(2,7,0),   end_datetime:makeDT(2,8,0)   },
  { id:403, title:"Elternabend",      person:"mama",  color:"#9b5de5", start_datetime:makeDT(2,19,0),  end_datetime:makeDT(2,20,30) },
  // ── In 3 Tagen
  { id:501, title:"Geburtstag Oma",   person:"family",color:"#f59e0b", start_datetime:makeDT(3,0,0)   },  // all-day
  { id:502, title:"Musik AG",         person:"kind2", color:"#fb923c", start_datetime:makeDT(3,13,0),  end_datetime:makeDT(3,14,0)  },
  { id:503, title:"Einkaufen",        person:"papa",  color:"#00b4d8", start_datetime:makeDT(3,17,0),  end_datetime:makeDT(3,18,0)  },
  // ── In 4 Tagen
  { id:601, title:"Yoga",             person:"mama",  color:"#9b5de5", start_datetime:makeDT(4,8,0),   end_datetime:makeDT(4,9,0)   },
  { id:602, title:"Schulausflug",     person:"kind1", color:"#f15bb5", start_datetime:makeDT(4,0,0)   },  // all-day
  { id:603, title:"Teammeeting",      person:"papa",  color:"#00b4d8", start_datetime:makeDT(4,14,0),  end_datetime:makeDT(4,15,0)  },
  // ── In 5 Tagen (Wochenende)
  { id:701, title:"Fahrradtour",      person:"family",color:"#10b981", start_datetime:makeDT(5,10,0),  end_datetime:makeDT(5,12,0)  },
  { id:702, title:"Nachhilfe",        person:"kind2", color:"#fb923c", start_datetime:makeDT(5,14,0),  end_datetime:makeDT(5,15,0)  },
  // ── In 6 Tagen (Wochenende)
  { id:801, title:"Großeltern Besuch",person:"family",color:"#f59e0b", start_datetime:makeDT(6,13,0),  end_datetime:makeDT(6,17,0)  },
  { id:802, title:"Joggen",           person:"papa",  color:"#00b4d8", start_datetime:makeDT(6,8,0),   end_datetime:makeDT(6,9,0)   },
];

const DEMO_TODOS = [
  // 🛒 Einkauf
  { id:1001, text:"Milch & Joghurt",      list_name:"Einkauf",    person:"mama",  done:false },
  { id:1002, text:"Brot vom Bäcker",      list_name:"Einkauf",    person:"papa",  done:false },
  { id:1003, text:"Obst & Gemüse",        list_name:"Einkauf",    person:"mama",  done:false },
  { id:1004, text:"Nudeln nachkaufen",    list_name:"Einkauf",    person:"family",done:true  },
  { id:1005, text:"Waschmittel",          list_name:"Einkauf",    person:"family",done:true  },
  // 🏡 Haushalt
  { id:2001, text:"Küche putzen",         list_name:"Haushalt",   person:"mama",  done:false },
  { id:2002, text:"Wäsche aufhängen",     list_name:"Haushalt",   person:"papa",  done:false },
  { id:2003, text:"Kinderzimmer aufräumen",list_name:"Haushalt",  person:"kind1", done:false },
  { id:2004, text:"Geschirrspüler ausräumen",list_name:"Haushalt",person:"kind2", done:true  },
  { id:2005, text:"Müll rausbringen",     list_name:"Haushalt",   person:"papa",  done:true  },
  // ✅ Erledigung
  { id:3001, text:"Arzttermin buchen",    list_name:"Erledigung", person:"mama",  done:false },
  { id:3002, text:"Schule anrufen",       list_name:"Erledigung", person:"papa",  done:false },
  { id:3003, text:"Paket abholen",        list_name:"Erledigung", person:"papa",  done:false },
  { id:3004, text:"Versicherung kündigen",list_name:"Erledigung", person:"mama",  done:true  },
];

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
  const [cur,  setCur]  = useState(0);
  const [next, setNext] = useState(null);
  const [loaded, setLoaded] = useState({});
  const acc = T.accent || "#c2855a";
  const FADE_MS = 800;

  // Nächste 2 Fotos vorausladen
  useEffect(() => {
    [1, 2].forEach(offset => {
      const i = (cur + offset) % photos.length;
      if (!loaded[i]) {
        const img = new Image();
        img.src = photos[i];
        img.onload = () => setLoaded(l => ({ ...l, [i]: true }));
      }
    });
  }, [cur, photos.length]);

  useEffect(() => {
    if (photos.length < 2) return;
    const t = setInterval(() => go(1), 5000);
    return () => clearInterval(t);
  }, [cur, photos.length]);

  const go = (dir) => {
    const n = (cur + dir + photos.length) % photos.length;
    setNext(n);
    setTimeout(() => { setCur(n); setNext(null); }, FADE_MS);
  };
  const goTo = (i) => { if (i === cur) return; setNext(i); setTimeout(() => { setCur(i); setNext(null); }, FADE_MS); };

  return (
    <div style={{ ...cardBase, padding:0, background:T.card, border:`1.5px solid ${T.border}`,
                  flex:1, minHeight:0, display:"flex", flexDirection:"column", overflow:"hidden" }}>

      {photos.length === 0 ? (
        <div style={{ flex:1, minHeight:200, display:"flex", flexDirection:"column", alignItems:"center",
                      justifyContent:"center", gap:10, background:T.border+"44", borderRadius:14 }}>
          <div style={{ fontSize:40 }}>📷</div>
          <div style={{ color:T.textSub, fontSize: chalk?15:12, fontFamily:ff, textAlign:"center" }}>
            Fotos in <strong>assets/photos/</strong> ablegen
          </div>
        </div>
      ) : (
        <div style={{ position:"relative", flex:1, minHeight:0, overflow:"hidden", borderRadius:14 }}>
          {/* Aktuelles Foto (unten) */}
          <img src={photos[cur]} alt="" style={{
            position:"absolute", inset:0, width:"100%", height:"100%", objectFit:"cover",
          }}/>
          {/* Nächstes Foto blendet ein (oben) */}
          {next !== null && (
            <img src={photos[next]} alt="" style={{
              position:"absolute", inset:0, width:"100%", height:"100%", objectFit:"cover",
              opacity: 0, animation:`xfade ${FADE_MS}ms ease-in-out forwards`,
            }}/>
          )}
          <style>{`@keyframes xfade { from { opacity:0 } to { opacity:1 } }`}</style>

          {photos.length > 1 && (<>
            <button onClick={()=>go(-1)} style={{
              position:"absolute", left:8, top:"50%", transform:"translateY(-50%)",
              width:34, height:34, borderRadius:10, border:"none",
              background:"rgba(0,0,0,0.38)", color:"#fff", fontSize:20,
              cursor:"pointer", display:"flex", alignItems:"center", justifyContent:"center", zIndex:2,
            }}>‹</button>
            <button onClick={()=>go(1)} style={{
              position:"absolute", right:8, top:"50%", transform:"translateY(-50%)",
              width:34, height:34, borderRadius:10, border:"none",
              background:"rgba(0,0,0,0.38)", color:"#fff", fontSize:20,
              cursor:"pointer", display:"flex", alignItems:"center", justifyContent:"center", zIndex:2,
            }}>›</button>
            <div style={{ position:"absolute", bottom:10, left:0, right:0,
                          display:"flex", justifyContent:"center", gap:6, zIndex:2 }}>
              {photos.map((_,i) => (
                <div key={i} onClick={()=>goTo(i)}
                  style={{ width:i===cur?20:7, height:7, borderRadius:4, cursor:"pointer",
                            background:i===cur?"#fff":"rgba(255,255,255,0.5)", transition:"all 0.3s" }}/>
              ))}
            </div>
          </>)}
        </div>
      )}
    </div>
  );
}

// ── JAALEE SENSOR CARD ────────────────────────────────────────────────────────
function JaaleeSensors({ cardBase, T, ff, hf, chalk }) {
  const [sensors, setSensors] = useState([]);
  useEffect(() => {
    const load = () => apiGet("/jaalee/sensors").then(d => { if (Array.isArray(d) && d.length > 0) setSensors(d); });
    load();
    const t = setInterval(load, 60000); // jede Minute aktualisieren
    return () => clearInterval(t);
  }, []);
  const humIcon  = (h) => h < 40 ? "💧" : h < 60 ? "🌡️" : "💦";
  const tempColor = (t) => t < 16 ? "#60a5fa" : t < 20 ? "#34d399" : t < 24 ? T.accent : "#f87171";
  return (
    <div style={{ ...cardBase, background:T.card, border:`1.5px solid ${T.border}` }}>
      <div style={{ fontSize: chalk?14:11, fontWeight:700, color:T.textSub, opacity:.7,
                    textTransform:"uppercase", letterSpacing:"0.1em", marginBottom:12, fontFamily:ff }}>
        🌡️ Sensoren – Jaalee
      </div>
      {sensors.length === 0
        ? <div style={{ color:T.textSub, fontSize: chalk?14:12, fontFamily:ff, opacity:.6 }}>
            Verbinde mit Backend…
          </div>
        : <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
            {sensors.map(s => (
              <div key={s.mac} style={{ display:"flex", alignItems:"center", gap:10,
                                         padding:"8px 12px", borderRadius:12,
                                         background:T.border+"33", border:`1px solid ${T.border}` }}>
                <span style={{ fontSize:16, minWidth:20 }}>📍</span>
                <span style={{ flex:1, fontSize: chalk?15:12, fontWeight:600, color:T.text, fontFamily:ff }}>{s.name}</span>
                <span style={{ fontSize: chalk?18:14, fontWeight:800, color:tempColor(s.temperature), fontFamily:hf }}>
                  {s.temperature}°
                </span>
                <span style={{ fontSize: chalk?13:11, color:T.textSub, fontFamily:ff }}>
                  {humIcon(s.humidity)} {s.humidity}%
                </span>
                <span style={{ fontSize:10, color:s.power>20?"#10b981":"#f87171", fontFamily:ff, opacity:.7 }}>🔋{s.power}%</span>
              </div>
            ))}
          </div>
      }
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
      .then(([evts, tds]) => {
        setEvents(evts.length > 0 ? evts : DEMO_EVENTS);
        setTodos(tds.length  > 0 ? tds  : DEMO_TODOS);
        setLoading(false);
      })
      .catch(() => { setEvents(DEMO_EVENTS); setTodos(DEMO_TODOS); setLoading(false); });
  }, []);

  const toggleTodo = async (id) => {
    // Sofort lokal umschalten, dann Backend (optional)
    setTodos(ts => ts.map(t => t.id===id ? {...t, done:!t.done} : t));
    apiPut(`/todos/${id}/done`).then(u => { if (u) setTodos(ts => ts.map(t => t.id===id ? u : t)); });
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

  // ── SBB Uhr (lokale sbbUhr.js, setTimeout entfernt → reines rAF) ──
  const SbbClock = React.memo(({ isDark }) => {
    const containerRef = React.useRef(null);
    const clockRef     = React.useRef(null);
    useEffect(() => {
      if (!containerRef.current) return;
      if (typeof sbbUhr === "undefined") return;
      const id = "sbb-clock-" + Math.random().toString(36).slice(2);
      containerRef.current.id = id;
      clockRef.current = new sbbUhr(id, isDark, false);
      clockRef.current.start();
      return () => { try { clockRef.current?.stop(); } catch(e){} };
    }, []);
    return <div ref={containerRef} style={{ width:"100%", height:"100%" }} />;
  });

  // ── HEUTE ──────────────────────────────────────────────────────────────────
  const HeutePage = () => {
    const todayEvts = events.filter(e => isToday(e.start_datetime))
                            .sort((a,b) => a.start_datetime.localeCompare(b.start_datetime));
    const openTodos = todos.filter(t => !t.done);
    const acc = T.accent || "#c2855a";
    const accLight = acc + "22";
    const accBorder = acc + "55";

    const isDark = T.bg === "#1a1a2e" || T.bg === "#0f172a" || T.bg?.startsWith("#0") || T.bg?.startsWith("#1");

    // ── Mini-Kalender ──
    const MiniCalendar = () => {
      const [offset, setOffset] = useState(0);
      const d = new Date(now.getFullYear(), now.getMonth()+offset, 1);
      const year = d.getFullYear(), month = d.getMonth();
      const monthName = d.toLocaleDateString("de-DE",{month:"long",year:"numeric"});
      const firstDow = (d.getDay()+6)%7; // Mo=0
      const daysInMonth = new Date(year, month+1, 0).getDate();
      const cells = [...Array(firstDow).fill(null),
                     ...Array.from({length:daysInMonth},(_,i)=>i+1)];
      const isToday2 = day => offset===0 && day===now.getDate();
      const DOW = ["Mo","Di","Mi","Do","Fr","Sa","So"];
      return (
        <div style={{ display:"flex", flexDirection:"column", height:"100%" }}>
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:8 }}>
            <button onClick={()=>setOffset(o=>o-1)} style={{ background:"none", border:"none", cursor:"pointer",
              color:T.textSub, fontSize:18, padding:"0 4px" }}>‹</button>
            <span style={{ fontSize:chalk?15:13, fontWeight:700, color:T.text, fontFamily:ff }}>{monthName}</span>
            <button onClick={()=>setOffset(o=>o+1)} style={{ background:"none", border:"none", cursor:"pointer",
              color:T.textSub, fontSize:18, padding:"0 4px" }}>›</button>
          </div>
          <div style={{ display:"grid", gridTemplateColumns:"repeat(7,1fr)", gap:2, flex:1 }}>
            {DOW.map(d => <div key={d} style={{ textAlign:"center", fontSize:chalk?12:11,
              fontWeight:700, color:T.textSub, fontFamily:ff, paddingBottom:4 }}>{d}</div>)}
            {cells.map((day,i) => (
              <div key={i} style={{ textAlign:"center", fontSize:chalk?14:12, fontFamily:ff,
                aspectRatio:"1", display:"flex", alignItems:"center", justifyContent:"center",
                borderRadius:"50%",
                background: isToday2(day) ? acc : "transparent",
                color: isToday2(day) ? "#fff" : day ? T.text : "transparent",
                fontWeight: isToday2(day) ? 700 : 400,
              }}>{day||""}</div>
            ))}
          </div>
        </div>
      );
    };

    // ── Wetter Widget (aktuell + 3-Tage Forecast) ──
    const WeatherWidget = () => {
      const h2 = now.getHours();
      const [icon, desc, temp] = h2 < 7  ? ["🌙","Klar & kühl","8°"]
                                : h2 < 10 ? ["🌤️","Morgen","12°"]
                                : h2 < 17 ? ["☀️","Sonnig","18°"]
                                : h2 < 20 ? ["🌅","Abend","15°"]
                                :           ["🌙","Nacht","10°"];
      const forecast = [
        { day:"Mo", icon:"🌤️", hi:"19°", lo:"9°" },
        { day:"Di", icon:"🌧️", hi:"14°", lo:"8°" },
        { day:"Mi", icon:"☀️",  hi:"22°", lo:"11°" },
      ];
      return (
        <div style={{ display:"flex", flexDirection:"column", height:"100%", gap:6 }}>
          {/* Aktuell */}
          <div style={{ display:"flex", flexDirection:"column", alignItems:"center",
                        justifyContent:"center", flex:1 }}>
            <div style={{ fontSize:chalk?56:44 }}>{icon}</div>
            <div style={{ fontSize:chalk?46:36, fontWeight:900, color:T.text, fontFamily:hf, lineHeight:1 }}>{temp}</div>
            <div style={{ fontSize:chalk?15:13, color:T.textSub, fontFamily:ff, marginTop:4 }}>{desc}</div>
          </div>
          {/* 3-Tage */}
          <div style={{ borderTop:`1px solid ${T.border}`, paddingTop:8,
                        display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:4 }}>
            {forecast.map(f => (
              <div key={f.day} style={{ display:"flex", flexDirection:"column", alignItems:"center", gap:2 }}>
                <div style={{ fontSize:chalk?13:12, fontWeight:700, color:T.textSub, fontFamily:ff }}>{f.day}</div>
                <div style={{ fontSize:chalk?26:22 }}>{f.icon}</div>
                <div style={{ fontSize:chalk?14:13, fontWeight:700, color:T.text, fontFamily:ff }}>{f.hi}</div>
                <div style={{ fontSize:chalk?12:11, color:T.textSub, fontFamily:ff }}>{f.lo}</div>
              </div>
            ))}
          </div>
        </div>
      );
    };

    // ── Geburtstage ──
    const BIRTHDAYS = [
      { name:"Mama",  date:"08-03", emoji:"👩" },
      { name:"Papa",  date:"05-21", emoji:"👨" },
      { name:"Kind",  date:"12-03", emoji:"👶" },
    ];
    const BirthdayWidget = () => {
      const today = `${String(now.getMonth()+1).padStart(2,"0")}-${String(now.getDate()).padStart(2,"0")}`;
      const upcoming = BIRTHDAYS.map(b => {
        const [m,d] = b.date.split("-").map(Number);
        const next = new Date(now.getFullYear(), m-1, d);
        if (next < now) next.setFullYear(now.getFullYear()+1);
        const days = Math.ceil((next - now) / 86400000);
        return { ...b, days };
      }).sort((a,b)=>a.days-b.days);
      return (
        <div style={{ display:"flex", flexDirection:"column", gap:8, height:"100%" }}>
          {upcoming.map(b => (
            <div key={b.name} style={{ display:"flex", alignItems:"center", gap:10,
              padding:"8px 10px", borderRadius:12,
              background: b.days<=7 ? acc+"22" : T.border+"33",
              border: b.days<=7 ? `1.5px solid ${acc}55` : `1.5px solid transparent` }}>
              <span style={{ fontSize:20 }}>{b.emoji}</span>
              <div style={{ flex:1 }}>
                <div style={{ fontSize:chalk?17:14, fontWeight:700, color:T.text, fontFamily:ff }}>{b.name}</div>
                <div style={{ fontSize:chalk?13:11, color:T.textSub, fontFamily:ff }}>{b.date.replace("-",".")}</div>
              </div>
              <span style={{ fontSize:chalk?14:12, fontWeight:700, fontFamily:ff,
                             color: b.days===0 ? acc : b.days<=7 ? acc : T.textSub }}>
                {b.days===0 ? "🎂 Heute!" : `in ${b.days}d`}
              </span>
            </div>
          ))}
        </div>
      );
    };

    // ── Auto-Scroll Helper ──
    const useAutoScroll = (ref, len, max) => {
      useEffect(() => {
        if (len <= max) return;
        const el = ref.current; if (!el) return;
        let dir = 1;
        const iv = setInterval(() => {
          el.scrollTop += dir;
          if (el.scrollTop + el.clientHeight >= el.scrollHeight - 2) setTimeout(()=>{ dir=-1; },1200);
          if (el.scrollTop <= 0 && dir===-1) setTimeout(()=>{ dir=1; },1200);
        }, 30);
        return () => clearInterval(iv);
      }, [len]);
    };

    const evtRef = React.useRef(null);  useAutoScroll(evtRef, todayEvts.length, 3);
    const todoRef = React.useRef(null); useAutoScroll(todoRef, openTodos.length, 3);

    const CARD = { ...cardBase, background:T.card, border:`1.5px solid ${T.border}` };
    const SectionLabel = ({children}) => (
      <div style={{ fontSize:chalk?14:12, fontWeight:700, color:T.textSub, textTransform:"uppercase",
                    letterSpacing:"0.1em", fontFamily:ff, marginBottom:8 }}>{children}</div>
    );

    // Portrait: simple stacked layout
    if (portrait) return (
      <div style={{ display:"flex", flexDirection:"column", height:"100%", gap:10 }}>
        <div style={{ ...CARD, padding:"14px 20px",
                      background:`linear-gradient(120deg,${acc},${acc}bb)`, border:"none",
                      display:"flex", justifyContent:"space-between", alignItems:"center" }}>
          <div>
            <div style={{ fontSize:12, color:"rgba(255,255,255,0.7)", fontFamily:ff,
                          textTransform:"uppercase", letterSpacing:"0.1em" }}>{dateStr}</div>
            <div style={{ fontSize:22, fontWeight:800, color:"#fff", fontFamily:hf, lineHeight:1.1 }}>
              {now.getHours()<12?"Guten Morgen":now.getHours()<17?"Guten Tag":"Guten Abend"}! 🤙
            </div>
          </div>
          <div style={{ display:"flex", gap:10 }}>
            {["👩","👨","👶"].map(e=>(
              <div key={e} style={{ width:36, height:36, borderRadius:"50%",
                background:"rgba(255,255,255,0.25)", display:"flex", alignItems:"center",
                justifyContent:"center", fontSize:18, border:"2px solid rgba(255,255,255,0.4)" }}>{e}</div>
            ))}
          </div>
        </div>
        <div style={{ flex:1, minHeight:0 }}>
          <PhotoSlider cardBase={cardBase} T={T} ff={ff} hf={hf} chalk={chalk} />
        </div>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10 }}>
          <div style={{ ...CARD, padding:12 }}>
            <SectionLabel>✅ Aufgaben ({openTodos.length})</SectionLabel>
            <div ref={todoRef} style={{ overflowY:"auto", maxHeight:120, scrollbarWidth:"none" }}>
              {openTodos.map(t => (
                <div key={t.id} style={{ display:"flex", alignItems:"center", gap:6, marginBottom:4,
                  padding:"3px 0", borderBottom:`1px solid ${T.border}` }}>
                  <div onClick={()=>toggleTodo(t.id)} style={{
                    width:16, height:16, borderRadius:4, border:`2px solid ${acc}`,
                    background:t.done?acc:"transparent", cursor:"pointer", flexShrink:0 }}/>
                  <span style={{ flex:1, color:T.text, fontSize:11, fontFamily:ff,
                    overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{t.text}</span>
                </div>
              ))}
            </div>
          </div>
          <div style={{ ...CARD, padding:12 }}>
            <SectionLabel>🎂 Geburtstage</SectionLabel>
            <BirthdayWidget />
          </div>
        </div>
      </div>
    );

    // Landscape: 3-column proportional layout
    return (
      <div style={{ display:"grid", height:"100%", gap:10,
                    gridTemplateColumns:"1fr 3fr 1fr" }}>

        {/* ── LINKE SPALTE: Uhr 2/5 · Kalender 2/5 · TagesPlan 1/5 ── */}
        <div style={{ display:"flex", flexDirection:"column", gap:10, minHeight:0 }}>

          {/* SBB Uhr */}
          <div style={{ ...CARD, flex:2, padding:8, minHeight:0 }}>
            <SbbClock isDark={isDark} />
          </div>

          {/* Mini-Kalender */}
          <div style={{ ...CARD, flex:2, padding:14, minHeight:0 }}>
            <MiniCalendar />
          </div>

          {/* Tagesplan */}
          <div style={{ ...CARD, flex:1, padding:14, minHeight:0, overflow:"hidden" }}>
            <SectionLabel>📅 Tagesplan</SectionLabel>
            <div ref={evtRef} style={{ overflowY:"auto", height:"calc(100% - 26px)", scrollbarWidth:"none" }}>
              {loading ? <div style={{ color:T.textSub, fontFamily:ff, fontSize:chalk?16:13 }}>…</div>
               : todayEvts.length===0
               ? <div style={{ color:T.textSub, fontSize:chalk?15:13, fontFamily:ff }}>Freier Tag 🌿</div>
               : todayEvts.map((e,i) => {
                  const col = CAL_COLORS[i%CAL_COLORS.length];
                  return (
                    <div key={e.id} style={{ display:"flex", gap:6, alignItems:"center", marginBottom:5,
                      padding:"5px 8px", borderRadius:8, background:col+"18", borderLeft:`3px solid ${col}` }}>
                      <span style={{ color:col, fontWeight:700, fontSize:chalk?14:12, fontFamily:ff, minWidth:36 }}>
                        {fmtTime(e.start_datetime)}</span>
                      <span style={{ color:T.text, fontSize:chalk?15:13, fontFamily:hf,
                        flex:1, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{e.title}</span>
                    </div>
                  );
                })
              }
            </div>
          </div>
        </div>

        {/* ── MITTLERE SPALTE: Header 1/5 · Foto 3/5 · Aufgaben+Geburtstage 1/5 ── */}
        <div style={{ display:"flex", flexDirection:"column", gap:10, minHeight:0 }}>

          {/* Header */}
          <div style={{ ...CARD, flex:1, padding:"12px 20px",
                        background:`linear-gradient(120deg,${acc},${acc}bb)`, border:"none",
                        display:"flex", justifyContent:"space-between", alignItems:"center", minHeight:0 }}>
            <div>
              <div style={{ fontSize:chalk?15:12, color:"rgba(255,255,255,0.7)", fontFamily:ff,
                            textTransform:"uppercase", letterSpacing:"0.1em" }}>{dateStr}</div>
              <div style={{ fontSize:chalk?34:26, fontWeight:800, color:"#fff", fontFamily:hf, lineHeight:1.1 }}>
                {now.getHours()<12?"Guten Morgen":now.getHours()<17?"Guten Tag":"Guten Abend"}! 🤙
              </div>
            </div>
            <div style={{ display:"flex", gap:12, alignItems:"center" }}>
              {[["👩","#7c3aed"],["👨","#0ea5e9"],["👶","#c2855a"]].map(([e,c])=>(
                <div key={e} style={{ width:chalk?48:36, height:chalk?48:36, borderRadius:"50%",
                  background:"rgba(255,255,255,0.25)", display:"flex", alignItems:"center",
                  justifyContent:"center", fontSize:chalk?24:18, border:"2px solid rgba(255,255,255,0.4)" }}>{e}</div>
              ))}
            </div>
          </div>

          {/* Foto */}
          <div style={{ flex:3, minHeight:0, display:"flex", flexDirection:"column" }}>
            <PhotoSlider cardBase={cardBase} T={T} ff={ff} hf={hf} chalk={chalk} />
          </div>

          {/* Offene Aufgaben + Geburtstage nebeneinander */}
          <div style={{ flex:1, display:"grid", gridTemplateColumns:"1fr 1fr", gap:10, minHeight:0 }}>
            <div style={{ ...CARD, padding:12, minHeight:0, overflow:"hidden" }}>
              <SectionLabel>✅ Aufgaben <span style={{ color:acc }}>({openTodos.length})</span></SectionLabel>
              <div ref={todoRef} style={{ overflowY:"auto", height:"calc(100% - 24px)", scrollbarWidth:"none" }}>
                {openTodos.length===0
                  ? <div style={{ color:T.textSub, fontSize:chalk?15:13, fontFamily:ff }}>Alles erledigt! 🎉</div>
                  : openTodos.map(t => (
                    <div key={t.id} style={{ display:"flex", alignItems:"center", gap:7, marginBottom:5,
                      padding:"3px 0", borderBottom:`1px solid ${T.border}` }}>
                      <div onClick={()=>toggleTodo(t.id)} style={{
                        width:18, height:18, borderRadius:5, border:`2px solid ${acc}`,
                        background:t.done?acc:"transparent", cursor:"pointer", flexShrink:0,
                        display:"flex", alignItems:"center", justifyContent:"center" }}>
                        {t.done && <span style={{ color:"#fff", fontSize:11, fontWeight:900 }}>✓</span>}
                      </div>
                      <span style={{ flex:1, color:T.text, fontSize:chalk?15:13, fontFamily:ff,
                        overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{t.text}</span>
                    </div>
                  ))
                }
              </div>
            </div>
            <div style={{ ...CARD, padding:12, minHeight:0, overflow:"hidden" }}>
              <SectionLabel>🎂 Geburtstage</SectionLabel>
              <div style={{ overflowY:"auto", height:"calc(100% - 24px)", scrollbarWidth:"none" }}>
                <BirthdayWidget />
              </div>
            </div>
          </div>
        </div>

        {/* ── RECHTE SPALTE: Wetter 2/5 · Sensoren 2/5 · Buttons 1/5 ── */}
        <div style={{ display:"flex", flexDirection:"column", gap:10, minHeight:0 }}>

          {/* Wetter aktuell + 3-Tage Forecast */}
          <div style={{ ...CARD, flex:2, padding:14, minHeight:0, overflow:"hidden" }}>
            <WeatherWidget />
          </div>

          {/* Sensoren */}
          <div style={{ flex:2, minHeight:0, overflow:"hidden" }}>
            <JaaleeSensors cardBase={cardBase} T={T} ff={ff} hf={hf} chalk={chalk} />
          </div>

          {/* Schnell-Buttons */}
          <div style={{ ...CARD, flex:1, padding:12, minHeight:0, overflow:"hidden" }}>
            <SectionLabel>⚡ Schnell-Buttons</SectionLabel>
            <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:5 }}>
              {[["🛒","Einkauf","einkauf"],["🍕","Pizza","pizza"],
                ["🏥","Arzt","arzt"],["🚗","Fahrt","fahrt"],
                ["📦","Paket","paket"],["🏄","Strand","strand"]].map(([em,l,key])=>{
                const img = window.BTN_IMGS?.[key];
                return (
                  <button key={l} style={{ background:T.card, border:`1.5px solid ${accBorder}`,
                    borderRadius:8, padding:"6px 3px", color:acc, cursor:"pointer", fontFamily:ff,
                    display:"flex", flexDirection:"column", alignItems:"center", gap:2 }}
                    onMouseEnter={e=>{ e.currentTarget.style.background=acc; e.currentTarget.style.color="#fff"; }}
                    onMouseLeave={e=>{ e.currentTarget.style.background=T.card; e.currentTarget.style.color=acc; }}>
                    {img ? <img src={img} style={{ width:20, height:20, objectFit:"contain" }}/> : <span style={{ fontSize:16 }}>{em}</span>}
                    <span style={{ fontSize:chalk?12:11, fontWeight:700 }}>{l}</span>
                  </button>
                );
              })}
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
      // Sofort lokal hinzufügen
      const local = { id: Date.now(), text:txt, list_name:list, person:"family", done:false };
      setTodos(ts => [local, ...ts]);
      setNewText(n=>({...n,[list]:""}));
      setAddingTo(null);
      // Backend optional
      apiPost("/todos/", {text:txt, list_name:list, person:"family"})
        .then(c => { if (c) setTodos(ts => ts.map(t => t.id===local.id ? c : t)); });
    };
    const delTodo = async (id) => {
      setTodos(ts => ts.filter(t => t.id!==id));
      apiDel(`/todos/${id}`);
    };

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

  // ── KALENDER DAY ──────────────────────────────────────────────────────────
  const KalenderDayPage = () => {
    const [view,       setView]       = useState("W");
    const [weekOffset, setWeekOffset] = useState(0);
    const [weekEvts,   setWeekEvts]   = useState(events.length > 0 ? events : DEMO_EVENTS);

    const PERSONS = [
      { key:"mama",  name:"Mama",  color:"#9b5de5", emoji:"👩" },
      { key:"papa",  name:"Papa",  color:"#00b4d8", emoji:"👨" },
      { key:"kind1", name:"Kind 1",color:"#f15bb5", emoji:"👦" },
      { key:"kind2", name:"Kind 2",color:"#fb923c", emoji:"👧" },
    ];

    const HOUR_H  = 56;
    const START_H = 7;
    const END_H   = 20;
    const HOURS   = Array.from({length: END_H - START_H + 1}, (_, i) => START_H + i);
    const DAY_S   = ["So","Mo","Di","Mi","Do","Fr","Sa"];

    const getWeekDays = (offset) => {
      const base = new Date();
      const dow  = base.getDay();
      const diff = (dow === 0 ? -6 : 1 - dow) + offset * 7;
      const mon  = new Date(base);
      mon.setDate(base.getDate() + diff);
      mon.setHours(0,0,0,0);
      return Array.from({length:7}, (_, i) => { const d = new Date(mon); d.setDate(mon.getDate()+i); return d; });
    };

    const weekDays  = getWeekDays(weekOffset);
    const weekStart = weekDays[0];
    const weekEnd   = weekDays[6];

    const goWeek = (dir) => {
      const next = weekOffset + dir;
      setWeekOffset(next);
      const d  = getWeekDays(next)[0];
      const ym = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}`;
      apiGet(`/events/?date=${ym}`).then(ev => setWeekEvts(ev));
    };

    const sameDay   = (a,b) => a.getFullYear()===b.getFullYear() && a.getMonth()===b.getMonth() && a.getDate()===b.getDate();
    const isAllDay  = (e) => { const d=new Date(e.start_datetime); return d.getHours()===0 && d.getMinutes()===0 && !e.end_datetime; };
    const evDay     = (date, allDay) => weekEvts.filter(e => { const d=new Date(e.start_datetime); return sameDay(d,date) && isAllDay(e)===allDay; });
    const personCol = (e) => { if(e.color) return e.color; const p=PERSONS.find(p=>p.key===(e.person||"").toLowerCase()); return p?p.color:CAL_COLORS[0]; };
    const evStyle   = (e) => {
      const s   = new Date(e.start_datetime);
      const en  = e.end_datetime ? new Date(e.end_datetime) : new Date(s.getTime()+3600000);
      const top = ((s.getHours()-START_H)*60 + s.getMinutes())/60*HOUR_H;
      return { top, height: Math.max((en-s)/3600000*HOUR_H, 24) };
    };
    const isTd  = (d) => sameDay(d, now);
    const fmtWk = () => {
      const o = {day:"numeric",month:"short"};
      return `${weekStart.toLocaleDateString("de-DE",o)} – ${weekEnd.toLocaleDateString("de-DE",o)} ${weekEnd.getFullYear()}`;
    };

    return (
      <div style={{ display:"flex", flexDirection:"column", height:"100%", gap:12 }}>

        {/* ── PERSON STRIP ── */}
        <div style={{ ...cardBase, background:T.card, border:`1.5px solid ${T.border}`,
                      display:"flex", gap:20, alignItems:"center", padding:"14px 24px", flexWrap:"wrap" }}>
          {PERSONS.map(p => {
            const img    = window.PER_IMGS?.[p.key];
            const pTodos = todos.filter(t => !t.done && (t.person||"").toLowerCase()===p.key);
            return (
              <div key={p.key} style={{ display:"flex", flexDirection:"column", alignItems:"center", gap:5 }}>
                <div style={{ width:58, height:58, borderRadius:"50%", overflow:"hidden",
                              border:`3px solid ${p.color}`, background:p.color+"22",
                              display:"flex", alignItems:"center", justifyContent:"center" }}>
                  {img
                    ? <img src={img} style={{width:"100%",height:"100%",objectFit:"cover"}}/>
                    : <span style={{fontSize:28}}>{p.emoji}</span>}
                </div>
                <span style={{ fontSize: chalk?15:12, fontWeight:700, color:T.text, fontFamily:ff }}>{p.name}</span>
                <span style={{ fontSize: chalk?12:10, color:p.color, fontWeight:600, fontFamily:ff }}>
                  ✓ {pTodos.length} to-dos
                </span>
              </div>
            );
          })}
        </div>

        {/* ── CALENDAR CARD ── */}
        <div style={{ ...cardBase, background:T.card, border:`1.5px solid ${T.border}`,
                      flex:1, minHeight:0, display:"flex", flexDirection:"column",
                      overflow:"hidden", padding:0 }}>

          {/* Header */}
          <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between",
                        padding:"12px 20px", borderBottom:`1px solid ${T.border}` }}>
            <div style={{ display:"flex", gap:2, background:T.border+"66", borderRadius:10, padding:2 }}>
              {["D","W","M"].map(v=>(
                <button key={v} onClick={()=>setView(v)} style={{
                  padding:"4px 14px", borderRadius:8, border:"none", cursor:"pointer",
                  background: view===v ? T.accent : "transparent",
                  color: view===v ? "#fff" : T.textSub,
                  fontSize:12, fontWeight:700, fontFamily:ff,
                }}>{v}</button>
              ))}
            </div>
            <span style={{ fontSize: chalk?18:14, fontWeight:700, color:T.text, fontFamily:ff }}>{fmtWk()}</span>
            <div style={{ display:"flex", gap:6 }}>
              {[[-1,"‹"],[1,"›"]].map(([d,l])=>(
                <button key={l} onClick={()=>goWeek(d)} style={{
                  background:T.card, border:`1.5px solid ${T.border}`,
                  borderRadius:10, width:32, height:32, cursor:"pointer", fontSize:16,
                  color:T.accent, display:"flex", alignItems:"center", justifyContent:"center",
                }}>{l}</button>
              ))}
            </div>
          </div>

          {/* Day name headers */}
          <div style={{ display:"grid", gridTemplateColumns:`52px repeat(7,1fr)`,
                        borderBottom:`1px solid ${T.border}` }}>
            <div/>
            {weekDays.map((d,i)=>(
              <div key={i} style={{ textAlign:"center", padding:"8px 4px",
                                     borderLeft:`1px solid ${T.border}88` }}>
                <div style={{ fontSize: chalk?13:10, color:T.textSub, fontFamily:ff,
                               textTransform:"uppercase", letterSpacing:"0.05em" }}>{DAY_S[d.getDay()]}</div>
                <div style={{
                  width:28, height:28, borderRadius:"50%", margin:"3px auto 0",
                  background: isTd(d) ? T.accent : "transparent",
                  display:"flex", alignItems:"center", justifyContent:"center",
                  fontSize: chalk?16:13, fontWeight: isTd(d)?800:500,
                  color: isTd(d)?"#fff":T.text, fontFamily:ff,
                }}>{d.getDate()}</div>
              </div>
            ))}
          </div>

          {/* ALL-DAY strip */}
          <div style={{ display:"grid", gridTemplateColumns:`52px repeat(7,1fr)`,
                        borderBottom:`1px solid ${T.border}`, minHeight:28 }}>
            <div style={{ display:"flex", alignItems:"center", justifyContent:"flex-end",
                          paddingRight:8, fontSize: chalk?12:9, color:T.textSub,
                          fontFamily:ff, opacity:.6, letterSpacing:"0.03em" }}>ALL-DAY</div>
            {weekDays.map((d,i)=>{
              const ade = evDay(d, true);
              return (
                <div key={i} style={{ borderLeft:`1px solid ${T.border}88`, padding:"2px 3px" }}>
                  {ade.map(e=>(
                    <div key={e.id} title={e.title} style={{
                      background:personCol(e), color:"#fff", borderRadius:4,
                      fontSize: chalk?11:9, padding:"1px 5px", marginBottom:1,
                      fontFamily:ff, fontWeight:600,
                      whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis",
                    }}>{e.title}</div>
                  ))}
                </div>
              );
            })}
          </div>

          {/* Time grid */}
          <div style={{ flex:1, overflowY:"auto" }}>
            <div style={{ display:"grid", gridTemplateColumns:`52px repeat(7,1fr)`,
                          position:"relative", minHeight: HOURS.length * HOUR_H }}>
              {/* Hour labels */}
              <div style={{ position:"relative" }}>
                {HOURS.map(h=>(
                  <div key={h} style={{
                    position:"absolute", top:(h-START_H)*HOUR_H-8, right:8,
                    width:44, textAlign:"right",
                    fontSize: chalk?13:10, color:T.textSub, fontFamily:ff, opacity:.7,
                  }}>{h}:00</div>
                ))}
              </div>

              {/* Day columns */}
              {weekDays.map((d,di)=>{
                const de = evDay(d, false);
                return (
                  <div key={di} style={{ position:"relative", borderLeft:`1px solid ${T.border}88` }}>
                    {HOURS.map(h=>(
                      <div key={h} style={{
                        position:"absolute", top:(h-START_H)*HOUR_H, left:0, right:0,
                        borderTop:`1px solid ${T.border}55`, height:HOUR_H,
                      }}/>
                    ))}
                    {de.map(e=>{
                      const {top,height} = evStyle(e);
                      const col = personCol(e);
                      return (
                        <div key={e.id} title={e.title} style={{
                          position:"absolute", top, left:2, right:2, height,
                          background:col, borderRadius:6, padding:"3px 6px",
                          overflow:"hidden", zIndex:2,
                          boxShadow:`0 2px 6px ${col}55`, cursor:"pointer",
                        }}>
                          <div style={{ fontSize: chalk?12:10, color:"#fff", fontWeight:700, fontFamily:ff, lineHeight:1.3 }}>
                            {fmtTime(e.start_datetime)}
                          </div>
                          <div style={{ fontSize: chalk?13:11, color:"#fff", fontFamily:ff, fontWeight:600, lineHeight:1.2 }}>
                            {e.title}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // ── KLIMA ──────────────────────────────────────────────────────────────────
  const KlimaPage = () => {
    const [sensors,    setSensors]    = useState([]);
    const [selMac,     setSelMac]     = useState("overview");
    const [history,    setHistory]    = useState([]);
    const [loading,    setLoading]    = useState(false);
    const [statsMap,   setStatsMap]   = useState({});   // mac → {maxT,minT,maxH,minH}

    useEffect(() => {
      apiGet("/jaalee/sensors").then(d => {
        if (Array.isArray(d) && d.length > 0) setSensors(d);
      });
    }, []);

    // Tages-Stats für Übersicht laden (1 Tag History pro Sensor)
    useEffect(() => {
      if (selMac !== "overview" || sensors.length === 0) return;
      const todayStart = new Date(); todayStart.setHours(0,0,0,0);
      const cutMs = todayStart.getTime();
      sensors.forEach(s => {
        apiGet(`/jaalee/history?mac=${s.mac}&days=1`).then(rows => {
          if (!Array.isArray(rows)) return;
          const today = rows.filter(r => r.t >= cutMs);
          const temps = today.map(r => r.temp);
          const hums  = today.map(r => r.hum);
          setStatsMap(prev => ({ ...prev, [s.mac]: {
            maxT: temps.length ? Math.max(...temps) : null,
            minT: temps.length ? Math.min(...temps) : null,
            maxH: hums.length  ? Math.max(...hums)  : null,
            minH: hums.length  ? Math.min(...hums)  : null,
          }}));
        });
      });
    }, [selMac, sensors]);

    useEffect(() => {
      if (!selMac || selMac === "overview") return;
      setLoading(true); setHistory([]);
      apiGet(`/jaalee/history?mac=${selMac}`).then(d => {
        if (Array.isArray(d)) setHistory(d);
        setLoading(false);
      });
    }, [selMac]);

    const accent = T.accent || "#6bbdb5";
    const DAY_S  = ["So","Mo","Di","Mi","Do","Fr","Sa"];

    // ── SVG Linien-Chart ──────────────────────────────────────────────────────
    const DualChart = ({ data }) => {
      if (!data.length) return <div style={{ color:T.textSub, fontFamily:ff, padding:20 }}>Keine Daten</div>;

      // Downsample: max 200 Punkte
      const step = Math.max(1, Math.floor(data.length / 200));
      const pts  = data.filter((_, i) => i % step === 0);

      const W = 800, H = 240;
      const pad = { t:20, b:62, l:52, r:52 };
      const cW  = W - pad.l - pad.r;
      const cH  = H - pad.t - pad.b;
      const tStart = pts[0].t, tEnd = pts[pts.length-1].t;
      const tRange = (tEnd - tStart) || 1;
      const xT  = t => pad.l + ((t - tStart) / tRange) * cW;

      // Temperatur (linke Achse)
      const temps = pts.map(d => d.temp);
      const minT = Math.min(...temps), maxT = Math.max(...temps);
      const rangeT = (maxT - minT) || 1;
      const yT   = v => pad.t + (1 - (v - minT) / rangeT) * cH;
      const lineT = pts.map(d => `${xT(d.t).toFixed(1)},${yT(d.temp).toFixed(1)}`).join(" ");

      // Feuchte (rechte Achse)
      const hums  = pts.map(d => d.hum);
      const minH  = Math.min(...hums), maxH = Math.max(...hums);
      const rangeH = (maxH - minH) || 1;
      const yH   = v => pad.t + (1 - (v - minH) / rangeH) * cH;
      const lineH = pts.map(d => `${xT(d.t).toFixed(1)},${yH(d.hum).toFixed(1)}`).join(" ");

      // 3h-Ticks
      const h3ms = 3 * 3600 * 1000;
      const firstTick = Math.ceil(tStart / h3ms) * h3ms;
      const hourTicks = [];
      for (let t = firstTick; t <= tEnd + 1000; t += h3ms) {
        const dt = new Date(t);
        const h  = dt.getHours();
        hourTicks.push({ t, xp: xT(t), h, isMidnight: h === 0,
                         label: String(h).padStart(2,'0') + ':00' });
      }

      // Tag-Labels
      const dayMarks = [];
      let lastDay = -1;
      pts.forEach(d => {
        const dt = new Date(d.t);
        if (dt.getDay() !== lastDay) {
          lastDay = dt.getDay();
          dayMarks.push({ t: d.t, xPos: xT(d.t), label: DAY_S[dt.getDay()] });
        }
      });
      const dayLabels = dayMarks.map((m, mi) => {
        const nextX = mi+1 < dayMarks.length ? dayMarks[mi+1].xPos : pad.l + cW;
        return { ...m, xMid: (m.xPos + nextX) / 2 };
      });

      // Y-Achsen Ticks
      const yTicksT = [0,0.2,0.4,0.6,0.8,1].map(f => ({ y: pad.t + f*cH, val: (maxT - f*rangeT).toFixed(1) }));
      const yTicksH = [0,0.2,0.4,0.6,0.8,1].map(f => ({ y: pad.t + f*cH, val: (maxH - f*rangeH).toFixed(0) }));

      const areaT = `${pad.l},${pad.t+cH} ${lineT} ${xT(tEnd)},${pad.t+cH}`;
      const areaH = `${pad.l},${pad.t+cH} ${lineH} ${xT(tEnd)},${pad.t+cH}`;
      const lastT = temps[temps.length-1], lastH = hums[hums.length-1];
      const avgT  = (temps.reduce((a,b)=>a+b,0)/temps.length).toFixed(1);
      const avgH  = (hums.reduce((a,b)=>a+b,0)/hums.length).toFixed(1);

      return (
        <div style={{ height:"100%", display:"flex", flexDirection:"column" }}>
          {/* Legende */}
          <div style={{ display:"flex", gap:24, marginBottom:8, flexWrap:"wrap", flexShrink:0 }}>
            <div style={{ display:"flex", alignItems:"center", gap:8 }}>
              <span style={{ width:20, height:3, background:"#f87171", display:"inline-block", borderRadius:2 }}/>
              <span style={{ fontSize:chalk?15:12, color:"#f87171", fontWeight:700, fontFamily:ff }}>
                Temperatur: {lastT.toFixed(1)}°C &nbsp;↑{maxT.toFixed(1)} ↓{minT.toFixed(1)} ⌀{avgT}
              </span>
            </div>
            <div style={{ display:"flex", alignItems:"center", gap:8 }}>
              <span style={{ width:20, height:3, background:"#60a5fa", borderTop:"2px dashed #60a5fa",
                             display:"inline-block", borderRadius:2 }}/>
              <span style={{ fontSize:chalk?15:12, color:"#60a5fa", fontWeight:700, fontFamily:ff }}>
                Luftfeuchte: {lastH.toFixed(1)}% &nbsp;↑{maxH.toFixed(1)} ↓{minH.toFixed(1)} ⌀{avgH}
              </span>
            </div>
          </div>
          <svg viewBox={`0 0 ${W} ${H}`} style={{ width:"100%", flex:1, display:"block", overflow:"visible" }}>
            {/* Gitter + linke Y-Achse (Temp) */}
            {yTicksT.map((t, i) => (
              <g key={i}>
                <line x1={pad.l} y1={t.y} x2={W-pad.r} y2={t.y}
                      stroke={T.border} strokeWidth={0.8} strokeDasharray="4,3"/>
                <text x={pad.l-6} y={t.y+4} textAnchor="end" fontSize={11} fill="#f87171"
                      fontFamily="Inter,sans-serif">{t.val}°</text>
              </g>
            ))}
            {/* Rechte Y-Achse (Feuchte) */}
            {yTicksH.map((t, i) => (
              <text key={i} x={W-pad.r+6} y={t.y+4} textAnchor="start" fontSize={11} fill="#60a5fa"
                    fontFamily="Inter,sans-serif">{t.val}%</text>
            ))}
            {/* 3h-Ticks + Mitternacht-Linien */}
            {hourTicks.map((tk, i) => (
              <g key={i}>
                {tk.isMidnight
                  ? <line x1={tk.xp} y1={pad.t} x2={tk.xp} y2={pad.t+cH}
                          stroke={T.border} strokeWidth={1.2} strokeDasharray="3,4"/>
                  : <line x1={tk.xp} y1={pad.t+cH} x2={tk.xp} y2={pad.t+cH+5}
                          stroke={T.border} strokeWidth={1}/>
                }
                <text x={tk.xp} y={pad.t+cH+17} textAnchor="middle" fontSize={11}
                      fill={T.text} fontFamily="Inter,sans-serif"
                      opacity={tk.isMidnight ? 0 : 1}>{tk.label}</text>
              </g>
            ))}
            {/* Tag-Labels */}
            {dayLabels.map((m, i) => (
              <g key={i}>
                <rect x={m.xMid-16} y={pad.t+cH+24} width={32} height={16}
                      rx={4} fill={T.border+"44"}/>
                <text x={m.xMid} y={pad.t+cH+36} textAnchor="middle" fontSize={11}
                      fill={T.text} fontWeight="700" fontFamily="Inter,sans-serif">{m.label}</text>
              </g>
            ))}
            {/* Feuchte-Fläche + gestrichelte Linie */}
            <polygon points={areaH} fill="#60a5fa" opacity={0.08}/>
            <polyline points={lineH} fill="none" stroke="#60a5fa" strokeWidth={2}
                      strokeLinejoin="round" strokeLinecap="round" strokeDasharray="6,3"/>
            {/* Temp-Fläche + Linie */}
            <polygon points={areaT} fill="#f87171" opacity={0.12}/>
            <polyline points={lineT} fill="none" stroke="#f87171" strokeWidth={2.5}
                      strokeLinejoin="round" strokeLinecap="round"/>
            {/* Endpunkt-Dots */}
            <circle cx={xT(tEnd)} cy={yT(lastT)} r={4} fill="#f87171"/>
            <circle cx={xT(tEnd)} cy={yH(lastH)} r={4} fill="#60a5fa"/>
          </svg>
        </div>
      );
    };

    const selSensor = sensors.find(s => s.mac === selMac);

    return (
      <div style={{ display:"flex", flexDirection:"column", gap:12, height:"100%" }}>

        {/* SENSOR TABS */}
        <div style={{ ...cardBase, background:T.card, border:`1.5px solid ${T.border}`,
                      display:"flex", alignItems:"center", gap:8, padding:"12px 20px", flexWrap:"wrap", flexShrink:0 }}>
          <button onClick={() => setSelMac("overview")} style={{
            padding:"5px 14px", borderRadius:10, border:"none", cursor:"pointer",
            background: selMac==="overview" ? accent : T.border+"55",
            color: selMac==="overview" ? "#fff" : T.text,
            fontSize: chalk?15:12, fontWeight:700, fontFamily:ff,
          }}>📋 Übersicht</button>
          <span style={{ width:1, height:20, background:T.border, margin:"0 4px" }}/>
          {sensors.map(s => (
            <button key={s.mac} onClick={() => setSelMac(s.mac)} style={{
              padding:"5px 14px", borderRadius:10, border:"none", cursor:"pointer",
              background: selMac===s.mac ? accent : T.border+"55",
              color: selMac===s.mac ? "#fff" : T.text,
              fontSize: chalk?15:12, fontWeight:700, fontFamily:ff,
            }}>{s.name}</button>
          ))}
        </div>

        {selMac === "overview" ? (
          /* ── ÜBERSICHT ALLE SENSOREN ── */
          <div style={{ flex:1, minHeight:0, overflow:"auto",
                        display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(260px,1fr))", gap:14 }}>
            {sensors.map(s => {
              const st = statsMap[s.mac] || {};
              return (
                <div key={s.mac} onClick={() => setSelMac(s.mac)} style={{
                  ...cardBase, background:T.card, border:`1.5px solid ${T.border}`,
                  cursor:"pointer", display:"flex", flexDirection:"column", gap:12,
                }}>
                  {/* Sensor-Name */}
                  <div style={{ fontSize:chalk?16:13, fontWeight:700, color:T.textSub,
                                textTransform:"uppercase", letterSpacing:"0.08em", fontFamily:ff }}>
                    {s.name}
                    <span style={{ float:"right", fontSize:chalk?12:10, fontWeight:400,
                                   color:T.textSub, opacity:.6 }}>🔋{s.power}%</span>
                  </div>
                  {/* Aktuelle Werte */}
                  <div style={{ display:"flex", gap:16, alignItems:"flex-end" }}>
                    <div>
                      <div style={{ fontSize:chalk?13:10, color:"#f87171", fontWeight:600,
                                    fontFamily:ff, textTransform:"uppercase" }}>Temperatur</div>
                      <div style={{ fontSize:chalk?42:32, fontWeight:900, color:"#f87171",
                                    fontFamily:hf, lineHeight:1 }}>{s.temperature}°</div>
                    </div>
                    <div style={{ width:1, height:40, background:T.border }}/>
                    <div>
                      <div style={{ fontSize:chalk?13:10, color:"#60a5fa", fontWeight:600,
                                    fontFamily:ff, textTransform:"uppercase" }}>Feuchte</div>
                      <div style={{ fontSize:chalk?34:26, fontWeight:800, color:"#60a5fa",
                                    fontFamily:hf, lineHeight:1 }}>{s.humidity}%</div>
                    </div>
                  </div>
                  {/* Tages-Max / Min */}
                  <div style={{ display:"flex", gap:8, borderTop:`1px solid ${T.border}`, paddingTop:10 }}>
                    <div style={{ flex:1, textAlign:"center" }}>
                      <div style={{ fontSize:chalk?11:9, color:T.textSub, fontFamily:ff,
                                    textTransform:"uppercase", letterSpacing:"0.06em" }}>Tages-Max</div>
                      <div style={{ fontSize:chalk?18:14, fontWeight:700, fontFamily:hf, color:"#f87171" }}>
                        {st.maxT != null ? st.maxT.toFixed(1)+"°" : "—"}
                        <span style={{ fontSize:chalk?14:11, color:"#60a5fa", marginLeft:6 }}>
                          {st.maxH != null ? st.maxH.toFixed(0)+"%" : ""}
                        </span>
                      </div>
                    </div>
                    <div style={{ width:1, background:T.border }}/>
                    <div style={{ flex:1, textAlign:"center" }}>
                      <div style={{ fontSize:chalk?11:9, color:T.textSub, fontFamily:ff,
                                    textTransform:"uppercase", letterSpacing:"0.06em" }}>Tages-Min</div>
                      <div style={{ fontSize:chalk?18:14, fontWeight:700, fontFamily:hf, color:"#f87171" }}>
                        {st.minT != null ? st.minT.toFixed(1)+"°" : "—"}
                        <span style={{ fontSize:chalk?14:11, color:"#60a5fa", marginLeft:6 }}>
                          {st.minH != null ? st.minH.toFixed(0)+"%" : ""}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <>
            {/* AKTUELLER WERT */}
            {selSensor && (
              <div style={{ ...cardBase, background:`linear-gradient(120deg,${accent},${accent}bb)`,
                            border:"none", padding:"14px 20px", flexShrink:0,
                            display:"flex", gap:32, alignItems:"center" }}>
                <div>
                  <div style={{ fontSize: chalk?13:10, color:"rgba(255,255,255,0.7)", fontFamily:ff,
                                 textTransform:"uppercase", letterSpacing:"0.1em" }}>{selSensor.name} – aktuell</div>
                  <div style={{ fontSize: chalk?38:28, fontWeight:900, color:"#fff", fontFamily:hf, lineHeight:1.1 }}>
                    {selSensor.temperature}°C
                  </div>
                </div>
                <div style={{ width:1, height:40, background:"rgba(255,255,255,0.3)" }}/>
                <div>
                  <div style={{ fontSize: chalk?13:10, color:"rgba(255,255,255,0.7)", fontFamily:ff,
                                 textTransform:"uppercase", letterSpacing:"0.1em" }}>Luftfeuchte</div>
                  <div style={{ fontSize: chalk?28:20, fontWeight:800, color:"#fff", fontFamily:hf }}>
                    {selSensor.humidity}%
                  </div>
                </div>
                <div style={{ marginLeft:"auto", fontSize: chalk?13:10, color:"rgba(255,255,255,0.6)", fontFamily:ff }}>
                  🔋 {selSensor.power}% · {history.length} Messwerte (7 Tage)
                </div>
              </div>
            )}
            {/* CHART */}
            <div style={{ ...cardBase, background:T.card, border:`1.5px solid ${T.border}`,
                          flex:1, minHeight:0, display:"flex", flexDirection:"column" }}>
              {loading
                ? <div style={{ color:T.textSub, fontFamily:ff, padding:20 }}>Lade Verlauf…</div>
                : history.length === 0
                ? <div style={{ color:T.textSub, fontFamily:ff, padding:20, opacity:.6 }}>
                    Keine Verlaufsdaten verfügbar
                  </div>
                : <DualChart data={history} />
              }
            </div>
          </>
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
    { id:"heute",       icon:"🏠", label:"Heute"        },
    { id:"kalenderday", icon:"📆", label:"Kalender Day" },
    { id:"kalender",    icon:"📅", label:"Kalender"     },
    { id:"todos",       icon:"✅", label:"Todos"        },
    { id:"speise",      icon:"🍽️", label:"Essen"        },
    { id:"klima",       icon:"🌡️", label:"Klima"        },
  ];

  const pages = { heute:<HeutePage/>, kalenderday:<KalenderDayPage/>, kalender:<KalenderPage/>, todos:<TodosPage/>, speise:<SpeisePage/>, klima:<KlimaPage/> };

  const [portrait, setPortrait] = useState(window.innerHeight > window.innerWidth);
  useEffect(() => {
    const onResize = () => setPortrait(window.innerHeight > window.innerWidth);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  const [isFullscreen, setIsFullscreen] = useState(!!document.fullscreenElement);
  useEffect(() => {
    const onFsChange = () => setIsFullscreen(!!document.fullscreenElement);
    document.addEventListener("fullscreenchange", onFsChange);
    return () => document.removeEventListener("fullscreenchange", onFsChange);
  }, []);
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) document.documentElement.requestFullscreen();
    else document.exitFullscreen();
  };

  const BOTTOM_NAV_H = 80;

  if (portrait) return (
    <div style={{ height:"100%", background:T.bg, display:"flex", flexDirection:"column", fontFamily:ff }}>

      {/* ── CONTENT ── */}
      <div style={{ flex:1, minHeight:0, overflow:"hidden", padding:16,
                    display:"flex", flexDirection:"column" }}>
        {pages[page]}
      </div>

      {/* ── BOTTOM NAV ── */}
      <div style={{ height:BOTTOM_NAV_H, background:T.sidebar, display:"flex", alignItems:"stretch",
                    boxShadow:"0 -4px 20px rgba(0,0,0,0.15)", flexShrink:0, zIndex:50 }}>
        {navItems.map(n=>(
          <div key={n.id} onClick={()=>setPage(n.id)} style={{
            flex:1, display:"flex", flexDirection:"column", alignItems:"center",
            justifyContent:"center", gap:4, cursor:"pointer",
            borderTop: page===n.id ? `3px solid ${T.accent||"#6bbdb5"}` : "3px solid transparent",
            background: page===n.id ? "rgba(255,255,255,0.08)" : "transparent",
          }}>
            <span style={{ fontSize:22 }}>{n.icon}</span>
            <span style={{ fontSize:chalk?13:10, fontWeight:page===n.id?700:400,
                           color:T.sidebarText, opacity:page===n.id?1:.55,
                           fontFamily:ff }}>{n.label}</span>
          </div>
        ))}
        {/* Theme-Knopf */}
        <div style={{ width:54, display:"flex", flexDirection:"column", alignItems:"center",
                      justifyContent:"center", gap:4, cursor:"pointer",
                      borderLeft:`1px solid rgba(255,255,255,0.1)` }}
             onClick={()=>{ const keys=Object.keys(THEMES); setThemeKey(keys[(keys.indexOf(themeKey)+1)%keys.length]); }}>
          <span style={{ fontSize:20 }}>🎨</span>
          <span style={{ fontSize:chalk?11:9, color:T.sidebarText, opacity:.5, fontFamily:ff }}>Theme</span>
        </div>
        {/* Fullscreen */}
        <div style={{ width:54, display:"flex", flexDirection:"column", alignItems:"center",
                      justifyContent:"center", gap:4, cursor:"pointer",
                      borderLeft:`1px solid rgba(255,255,255,0.1)` }}
             onClick={toggleFullscreen}>
          <span style={{ fontSize:20 }}>{isFullscreen ? "🗗" : "⛶"}</span>
          <span style={{ fontSize:chalk?11:9, color:T.sidebarText, opacity:.5, fontFamily:ff }}>
            {isFullscreen ? "Fenster" : "Fullscr"}
          </span>
        </div>
      </div>
    </div>
  );

  return (
    <div style={{ height:"100%", background:T.bg, display:"flex", fontFamily:ff }}>

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

        {/* Fullscreen */}
        <button onClick={toggleFullscreen} style={{
          marginTop:12, width:"100%", background:"rgba(255,255,255,0.08)",
          border:"1px solid rgba(255,255,255,0.15)", borderRadius:10,
          color:T.sidebarText, cursor:"pointer", padding:"8px 0",
          fontSize:chalk?16:13, fontFamily:ff, fontWeight:600,
          display:"flex", alignItems:"center", justifyContent:"center", gap:8,
        }}>
          {isFullscreen ? "⛶ Fenster" : "⛶ Fullscreen"}
        </button>
      </div>

      {/* ── CONTENT ── */}
      <div style={{ flex:1, marginLeft:200, overflow:"hidden", padding:24,
                    height:"100%", display:"flex", flexDirection:"column" }}>
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

try:
    from PIL import Image as PILImage
    landscape_photos = []
    for fname, url in photos.items():
        fpath = os.path.join(ASSETS, "photos", next(
            f for f in os.listdir(os.path.join(ASSETS, "photos"))
            if os.path.splitext(f)[0].lower() == fname
        ))
        try:
            with PILImage.open(fpath) as im:
                w, h = im.size
                if w >= h:
                    landscape_photos.append(url)
        except Exception:
            landscape_photos.append(url)
    all_photos = landscape_photos
    print(f"  Querformat-Fotos: {len(all_photos)} (von {len(photos)} gesamt)")
except ImportError:
    all_photos = list(photos.values())
    print(f"  Gesamt Fotos: {len(all_photos)} (Pillow nicht installiert, kein Filter)")

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
webbrowser.open("http://localhost:8000/dashboard")
print()
print("Sidebar links: Theme wechseln + Kreide-Schrift an/aus")
