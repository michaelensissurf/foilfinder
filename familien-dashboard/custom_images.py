"""
Familien-Dashboard – Eigene Bilder als Emojis/Icons

ANLEITUNG:
  1. Eigene Fotos in diese Ordner legen:
       assets/personen/mama.jpg   (oder .png, .webp)
       assets/personen/papa.jpg
       assets/personen/kind.jpg
       assets/buttons/pizza.jpg   (eigenes Button-Bild)
       assets/buttons/einkauf.jpg
       ... beliebig viele

  2. python custom_images.py ausführen
  3. Dashboard öffnet sich mit deinen Bildern!

Unterstützte Formate: JPG, PNG, GIF, WEBP, SVG
"""

import webbrowser, os, base64, json, mimetypes

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ── Bilder einlesen & Base64 kodieren ────────────────────────────────────────
def load_images(folder):
    result = {}
    folder_path = os.path.join(ASSETS, folder)
    if not os.path.exists(folder_path):
        return result
    for fname in sorted(os.listdir(folder_path)):
        ext = os.path.splitext(fname)[1].lower()
        if ext not in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}:
            continue
        fpath = os.path.join(folder_path, fname)
        mime  = mimetypes.guess_type(fpath)[0] or "image/png"
        with open(fpath, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        name = os.path.splitext(fname)[0]  # z.B. "mama" aus "mama.jpg"
        result[name] = f"data:{mime};base64,{b64}"
        print(f"  Geladen: {folder}/{fname} ({len(b64)//1024} KB)")
    return result

print("Lade Bilder...")
personen = load_images("personen")
buttons  = load_images("buttons")
print(f"  {len(personen)} Personen-Bilder, {len(buttons)} Button-Bilder\n")

# Standard-Fallbacks wenn kein Bild vorhanden
PERSONEN_DEFAULT = {"mama": "👩", "papa": "👨", "kind": "👶", "family": "🏡"}
BUTTONS_DEFAULT  = [
    {"key":"einkauf",  "label":"Einkaufen", "emoji":"🛒", "color":"#6366f1"},
    {"key":"pizza",    "label":"Pizza",     "emoji":"🍕", "color":"#ef4444"},
    {"key":"arzt",     "label":"Arzt",      "emoji":"🏥", "color":"#10b981"},
    {"key":"taxi",     "label":"Taxi",      "emoji":"🚗", "color":"#f59e0b"},
    {"key":"paket",    "label":"Paket",     "emoji":"📦", "color":"#8b5cf6"},
    {"key":"strand",   "label":"Strand",    "emoji":"🏄", "color":"#06b6d4"},
]

# JSON für den Browser aufbereiten
personen_js = json.dumps(personen)
buttons_js  = json.dumps(buttons)
defaults_js = json.dumps(BUTTONS_DEFAULT)

HTML = f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Family Dashboard – Eigene Bilder</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family:'Inter',sans-serif; background:#f5f0e8; }}
    .card {{ background:#fff; border-radius:20px; padding:20px;
             box-shadow:0 2px 16px rgba(0,0,0,0.07); border:1.5px solid #ede8e0; }}
    .avatar {{ border-radius:50%; object-fit:cover; }}
    .btn-img {{ border-radius:16px; overflow:hidden; object-fit:cover; }}
    ::-webkit-scrollbar {{ width:4px; }}
    ::-webkit-scrollbar-thumb {{ background:#d1c4b0; border-radius:2px; }}
  </style>
</head>
<body>
<div id="root"></div>
<script>
  // Eigene Bilder (Base64 aus Python eingelesen)
  const PERSONEN_IMGS = {personen_js};
  const BUTTONS_IMGS  = {buttons_js};
  const BUTTONS_DEF   = {defaults_js};
</script>
<script type="text/babel">
const {{ useState, useRef }} = React;

// ── BILD-KOMPONENTEN ──────────────────────────────────────────────────────────
function PersonAvatar({{ name, size=44 }}) {{
  const src = PERSONEN_IMGS[name];
  const fallback = {{ mama:"👩", papa:"👨", kind:"👶", family:"🏡" }};
  if (src) return (
    <img src={{src}} className="avatar" style={{{{ width:size, height:size, border:"2.5px solid #e8d5c0" }}}} alt={{name}}/>
  );
  return (
    <div style={{{{ width:size, height:size, borderRadius:"50%", fontSize:size*0.55,
                   display:"flex", alignItems:"center", justifyContent:"center",
                   background:"#f0e8dc", border:"2px solid #e0d0c0" }}}}>
      {{fallback[name] || "👤"}}
    </div>
  );
}}

function ButtonIcon({{ btnKey, size=40 }}) {{
  const src = BUTTONS_IMGS[btnKey];
  if (src) return (
    <img src={{src}} className="btn-img" style={{{{ width:size, height:size, objectFit:"cover" }}}} alt={{btnKey}}/>
  );
  return null;
}}

// ── UPLOAD BEREICH ────────────────────────────────────────────────────────────
function UploadHint() {{
  const assetsPath = String.raw`{ASSETS.replace(os.sep, os.sep+os.sep)}`;
  return (
    <div className="card" style={{{{ background:"#fef9f0", border:"2px dashed #f59e0b" }}}}>
      <div style={{{{ fontSize:22, fontWeight:800, marginBottom:8 }}}}>📁 Eigene Bilder hinzufügen</div>
      <p style={{{{ color:"#6b5a40", fontSize:14, marginBottom:12 }}}}>
        Lege deine Fotos in diese Ordner und starte das Script neu:
      </p>
      <div style={{{{ background:"#1a1a1a", borderRadius:12, padding:"12px 16px", marginBottom:12 }}}}>
        <div style={{{{ color:"#86efac", fontSize:12, fontFamily:"monospace", lineHeight:2 }}}}>
          <div><span style={{{{color:"#94a3b8"}}}}>Personen-Avatare:</span></div>
          <div>  assets/personen/<b style={{{{color:"#fbbf24"}}}}>mama</b>.jpg</div>
          <div>  assets/personen/<b style={{{{color:"#fbbf24"}}}}>papa</b>.jpg</div>
          <div>  assets/personen/<b style={{{{color:"#fbbf24"}}}}>kind</b>.jpg</div>
          <div style={{{{marginTop:8}}}}><span style={{{{color:"#94a3b8"}}}}>Button-Icons:</span></div>
          <div>  assets/buttons/<b style={{{{color:"#fbbf24"}}}}>pizza</b>.jpg</div>
          <div>  assets/buttons/<b style={{{{color:"#fbbf24"}}}}>einkauf</b>.png</div>
          <div>  assets/buttons/<b style={{{{color:"#fbbf24"}}}}>strand</b>.jpg</div>
          <div style={{{{color:"#94a3b8",marginTop:4}}}}>  ... beliebig viele!</div>
        </div>
      </div>
      <div style={{{{ background:"#fff", border:"1.5px solid #fde68a", borderRadius:12, padding:"10px 14px",
                       fontSize:13, color:"#92400e" }}}}>
        💡 Tipp: Dateiname = Schlüssel. "mama.jpg" → Avatar für Mama.<br/>
        "pizza.jpg" → Bild für den Pizza-Button.
      </div>
    </div>
  );
}}

// ── LIVE UPLOAD (Drag & Drop im Browser) ─────────────────────────────────────
function LiveUpload({{ onImageLoaded }}) {{
  const [dragging, setDragging] = useState(false);
  const [uploads,  setUploads]  = useState({{}});
  const inputRef = useRef();

  const handleFiles = (files) => {{
    Array.from(files).forEach(file => {{
      if (!file.type.startsWith("image/")) return;
      const reader = new FileReader();
      reader.onload = (e) => {{
        const name = file.name.replace(/\.[^.]+$/, "").toLowerCase();
        setUploads(u => ({{ ...u, [name]: e.target.result }}));
        onImageLoaded(name, e.target.result);
      }};
      reader.readAsDataURL(file);
    }});
  }};

  return (
    <div className="card">
      <div style={{{{ fontSize:16, fontWeight:800, marginBottom:12 }}}}>🖼 Direkt hier hochladen (temporär)</div>
      <p style={{{{ color:"#6b5a40", fontSize:13, marginBottom:12 }}}}>
        Bilder hier reinziehen – werden sofort als Avatare / Button-Icons verwendet.<br/>
        <span style={{{{opacity:.6}}}}>Dateiname bestimmt Verwendung: mama.jpg → Mama-Avatar</span>
      </p>
      <div
        onDragOver={{e => {{ e.preventDefault(); setDragging(true); }}}}
        onDragLeave={{() => setDragging(false)}}
        onDrop={{e => {{ e.preventDefault(); setDragging(false); handleFiles(e.dataTransfer.files); }}}}
        onClick={{() => inputRef.current.click()}}
        style={{{{
          border: `2px dashed ${{dragging?"#7c3aed":"#c4b5a0"}}`,
          background: dragging ? "#f3f0ff" : "#faf7f2",
          borderRadius:16, padding:"28px 20px", textAlign:"center", cursor:"pointer",
          transition:"all 0.15s",
        }}}}>
        <div style={{{{ fontSize:40, marginBottom:8 }}}}>📸</div>
        <div style={{{{ fontWeight:700, color:"#5a4030" }}}}>Bilder reinziehen</div>
        <div style={{{{ color:"#a08060", fontSize:13, marginTop:4 }}}}>oder klicken zum Auswählen</div>
        <input ref={{inputRef}} type="file" multiple accept="image/*"
          style={{{{display:"none"}}}} onChange={{e => handleFiles(e.target.files)}}/>
      </div>

      {{Object.keys(uploads).length > 0 && (
        <div style={{{{ marginTop:14 }}}}>
          <div style={{{{ fontSize:12, fontWeight:700, color:"#6b5a40", marginBottom:8 }}}}>GELADEN:</div>
          <div style={{{{ display:"flex", flexWrap:"wrap", gap:10 }}}}>
            {{Object.entries(uploads).map(([name, src]) => (
              <div key={{name}} style={{{{ textAlign:"center" }}}}>
                <img src={{src}} style={{{{ width:56, height:56, borderRadius:12, objectFit:"cover",
                                        border:"2px solid #e0d0c0" }}}} alt={{name}}/>
                <div style={{{{ fontSize:11, color:"#6b5a40", marginTop:3, fontWeight:600 }}}}>{{name}}</div>
              </div>
            ))}}
          </div>
        </div>
      )}}
    </div>
  );
}}

// ── HAUPT-DEMO ────────────────────────────────────────────────────────────────
function App() {{
  const [extraImgs, setExtraImgs] = useState({{}});

  // Live-Upload Bilder mergen
  const allPersonen = {{ ...PERSONEN_IMGS, ...extraImgs }};
  const allButtons  = {{ ...BUTTONS_IMGS,  ...extraImgs }};

  const PersonAvatarLive = ({{ name, size=44 }}) => {{
    const src = allPersonen[name];
    const fallback = {{ mama:"👩", papa:"👨", kind:"👶", family:"🏡" }};
    if (src) return <img src={{src}} className="avatar" style={{{{width:size,height:size,border:"2.5px solid #e8d5c0"}}}} alt={{name}}/>;
    return (
      <div style={{{{width:size,height:size,borderRadius:"50%",fontSize:size*0.55,
                     display:"flex",alignItems:"center",justifyContent:"center",
                     background:"#f0e8dc",border:"2px solid #e0d0c0"}}}}>
        {{fallback[name] || "👤"}}
      </div>
    );
  }};

  return (
    <div style={{{{ minHeight:"100vh", display:"flex" }}}}>

      {{/* SIDEBAR */}}
      <div style={{{{ width:200, background:"#2d2d2d", padding:20, position:"fixed",
                      top:0, bottom:0, display:"flex", flexDirection:"column", gap:8 }}}}>
        <div style={{{{ color:"#f5f0e8", fontWeight:800, fontSize:18, marginBottom:16, lineHeight:1.2 }}}}>
          Family<br/>Dashboard
        </div>

        {{/* Personen-Avatare in Sidebar */}}
        <div style={{{{ fontSize:11, color:"rgba(255,255,255,0.4)", fontWeight:700,
                        textTransform:"uppercase", letterSpacing:"0.1em", marginTop:8 }}}}>Personen</div>
        {{["mama","papa","kind"].map(p => (
          <div key={{p}} style={{{{ display:"flex", alignItems:"center", gap:10 }}}}>
            <PersonAvatarLive name={{p}} size={{36}}/>
            <span style={{{{ color:"#f5f0e8", fontSize:13, textTransform:"capitalize", fontWeight:500 }}}}>{{p}}</span>
          </div>
        ))}}

        <div style={{{{ flex:1 }}}}/>
        <div style={{{{ color:"rgba(255,255,255,0.3)", fontSize:11 }}}}>
          Eigene Fotos → assets/personen/
        </div>
      </div>

      {{/* CONTENT */}}
      <div style={{{{ flex:1, marginLeft:200, padding:24, display:"flex", flexDirection:"column", gap:16, maxWidth:720 }}}}>

        {{/* HEADER */}}
        <div style={{{{ display:"flex", justifyContent:"space-between", alignItems:"center" }}}}>
          <div>
            <div style={{{{ fontSize:26, fontWeight:900, color:"#2d2015" }}}}>Guten Morgen! 🤙</div>
            <div style={{{{ color:"#6b5a40", fontSize:14 }}}}>Mittwoch, 4. März 2026</div>
          </div>
          <div style={{{{ display:"flex", gap:10, alignItems:"center" }}}}>
            {{["mama","papa","kind"].map(p => (
              <PersonAvatarLive key={{p}} name={{p}} size={{46}}/>
            ))}}
          </div>
        </div>

        {{/* UPLOAD BEREICH */}}
        <LiveUpload onImageLoaded={{(name, src) => setExtraImgs(e => ({{...e, [name]:src}}))}}/>

        {{/* QUICK BUTTONS mit eigenen Bildern */}}
        <div className="card">
          <div style={{{{ fontSize:12, fontWeight:700, color:"#8a7060", textTransform:"uppercase",
                          letterSpacing:"0.1em", marginBottom:14 }}}}>Schnell-Buttons (mit eigenen Icons)</div>
          <div style={{{{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:12 }}}}>
            {{BUTTONS_DEF.map(btn => {{
              const imgSrc = allButtons[btn.key];
              return (
                <button key={{btn.key}} style={{{{
                  background: imgSrc ? "none" : btn.color+"18",
                  border:`2px solid ${{btn.color}}33`, borderRadius:16,
                  padding:"14px 10px", cursor:"pointer",
                  display:"flex", flexDirection:"column", alignItems:"center", gap:8,
                  overflow:"hidden", position:"relative",
                }}}}>
                  {{imgSrc ? (
                    <img src={{imgSrc}} style={{{{
                      width:48, height:48, borderRadius:12, objectFit:"cover",
                      border:`2px solid ${{btn.color}}44`,
                    }}}} alt={{btn.key}}/>
                  ) : (
                    <span style={{{{fontSize:28}}}}>{{btn.emoji}}</span>
                  )}}
                  <span style={{{{ color:btn.color, fontSize:12, fontWeight:700 }}}}>{{btn.label}}</span>
                </button>
              );
            }})}}
          </div>
          <div style={{{{ marginTop:12, padding:"10px 14px", background:"#fef9f0",
                          border:"1.5px solid #fde68a", borderRadius:12, fontSize:13, color:"#92400e" }}}}>
            💡 Eigene Button-Bilder: <code>assets/buttons/pizza.jpg</code> hochladen
            oder oben reinziehen (Dateiname = <code>pizza</code>)
          </div>
        </div>

        {{/* HEUTE KARTE */}}
        <div className="card">
          <div style={{{{ fontSize:12, fontWeight:700, color:"#8a7060", textTransform:"uppercase",
                          letterSpacing:"0.1em", marginBottom:14 }}}}>Termine heute</div>
          {{[
            {{time:"08:30", title:"Kindergarten bringen", person:"mama", color:"#7c3aed"}},
            {{time:"10:00", title:"Zahnarzt Papa",         person:"papa", color:"#0ea5e9"}},
            {{time:"14:00", title:"Spielgruppe",           person:"kind", color:"#f59e0b"}},
          ].map((e,i) => (
            <div key={{i}} style={{{{ display:"flex", alignItems:"center", gap:12, marginBottom:10,
                                      background:e.color+"0f", border:`1.5px solid ${{e.color}}22`,
                                      borderRadius:14, padding:"10px 14px" }}}}>
              <PersonAvatarLive name={{e.person}} size={{32}}/>
              <div style={{{{ background:e.color, color:"#fff", borderRadius:8, padding:"3px 10px",
                              fontSize:12, fontWeight:700, minWidth:44, textAlign:"center" }}}}>
                {{e.time}}
              </div>
              <span style={{{{ flex:1, fontSize:14, fontWeight:500, color:"#2d2015" }}}}>{{e.title}}</span>
            </div>
          ))}}
        </div>

        {{/* ANLEITUNG */}}
        <UploadHint/>

      </div>
    </div>
  );
}}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
</script>
</body>
</html>
"""

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "custom_images.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(HTML)

print("Fertig! Oeffne Browser...")
webbrowser.open(f"file:///{output_path.replace(os.sep, '/')}")
print()
print("ANLEITUNG:")
print("  Personen-Fotos:  assets/personen/mama.jpg")
print("                   assets/personen/papa.jpg")
print("                   assets/personen/kind.jpg")
print()
print("  Button-Bilder:   assets/buttons/pizza.jpg")
print("                   assets/buttons/einkauf.jpg")
print("                   assets/buttons/strand.jpg")
print()
print("Dann: python custom_images.py  (neu starten)")
print("ODER: Bilder direkt in den Browser ziehen!")
