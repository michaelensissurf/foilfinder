import streamlit as st
from foil_specs import FOIL_SPECS

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Parawing Foilfinder", layout="wide")

# =========================================================
# FOIL SIZES
# =========================================================
FLOW_SIZES = [720, 900, 1080, 1260]
STRIDE_ACE_SIZES = [1360, 1740]
INFINITY_SIZES = [540, 690, 840, 990, 1140, 1390]

FLOW_STANDARD = 1080
FLOW_STANDARD_INDEX = FLOW_SIZES.index(FLOW_STANDARD)

# Flow → Infinity Mapping (Infinity etwas größer wegen weniger Lift)
FLOW_TO_INFINITY = {
    720: 840,
    900: 990,
    1080: 1140,
    1260: 1390
}

# =========================================================
# PARAMETERS
# =========================================================
LEVELS = ["Discover", "Intermediate", "Expert"]
GEWICHT = ["<70", "70-90", ">90"]
KATEGORIEN = ["Freeride", "Downwind-Wave"]
WIND = ["Schwach", "Mittel", "Stark"]
WELLEN = ["Flachwasser", "Kleine Wellen", "Grosse Wellen"]

# =========================================================
# SESSION STATE
# =========================================================
for k in ["result", "selected_foil"]:
    if k not in st.session_state:
        st.session_state[k] = None

# =========================================================
# HELPERS
# =========================================================
def fmt(v):
    return int(v) if float(v).is_integer() else round(v, 1)

# =========================================================
# RECOMMENDATION LOGIC
# =========================================================
def calculate_flow_offset(level, gewicht, kategorie, wind, wellen):
    offset = 0

    # Gewicht
    if gewicht == "<70":
        offset -= 1
    elif gewicht == ">90":
        offset += 1

    # Level
    if level == "Discover":
        offset += 1
    elif level == "Expert":
        offset -= 1

    # Wind
    if wind == "Schwach":
        offset += 1
    elif wind == "Stark":
        offset -= 1

    # Wellen (abhängig von Kategorie)
    if kategorie == "Downwind-Wave":
        # Wellen sind PRIMÄR für Downwind-Wave
        if wellen == "Grosse Wellen":
            offset -= 1
    # Bei Freeride: Wellen werden ignoriert (sekundär)

    return offset

def get_optimal_flow(level, gewicht, kategorie, wind, wellen):
    offset = calculate_flow_offset(level, gewicht, kategorie, wind, wellen)
    target_index = FLOW_STANDARD_INDEX + offset
    target_index = max(0, min(target_index, len(FLOW_SIZES) - 1))
    return FLOW_SIZES[target_index], offset

def should_recommend_stride_ace(level, gewicht, kategorie, wind, wellen, flow_size):
    """
    Stride Ace nur für Discover bei sanften Bedingungen:
    - Kein starker Wind (zu schwierig für Beginner)
    - Keine großen Wellen (zu schwierig für Beginner)
    - Nur wenn Flow >= 1080 wäre (also grundsätzlich größerer Foil nötig)
    """
    if level != "Discover":
        return False

    if flow_size < 1080:
        return False

    # Starker Wind oder große Wellen → kein Stride (zu schwierig)
    if wind == "Stark" or wellen == "Grosse Wellen":
        return False

    # Stride bei schwachem Wind oder Flachwasser (aber nicht bei stark/groß)
    if wind == "Schwach" or wellen == "Flachwasser":
        return True

    return False

def recommend_top3(level, gewicht, kategorie, wind, wellen):
    flow_size, offset = get_optimal_flow(level, gewicht, kategorie, wind, wellen)
    flow_index = FLOW_SIZES.index(flow_size)

    top3 = []

    # DISCOVER mit Stride Ace Präferenz
    if should_recommend_stride_ace(level, gewicht, kategorie, wind, wellen, flow_size):

        # Schwere Rider (70-90 oder >90): Stride 1740 möglich
        if gewicht in ["70-90", ">90"]:
            top3.append({"Foil": "Stride Ace 1740", "Rank": 1})
            top3.append({"Foil": "Stride Ace 1360", "Rank": 2})
            top3.append({"Foil": f"Flow Ace {flow_size}", "Rank": 3})

        # Leichte Rider (<70): Stride 1740 fällt weg
        else:
            top3.append({"Foil": "Stride Ace 1360", "Rank": 1})
            top3.append({"Foil": f"Flow Ace {flow_size}", "Rank": 2})
            if flow_index > 0:
                top3.append({"Foil": f"Flow Ace {FLOW_SIZES[flow_index - 1]}", "Rank": 3})
            elif flow_index < len(FLOW_SIZES) - 1:
                top3.append({"Foil": f"Flow Ace {FLOW_SIZES[flow_index + 1]}", "Rank": 3})

    # DISCOVER ohne Stride (bei stärkerem Wind / größeren Wellen)
    elif level == "Discover":
        top3.append({"Foil": f"Flow Ace {flow_size}", "Rank": 1})

        # Rang 2: Flow Nachbargröße (sichere Alternative)
        if flow_index > 0:
            top3.append({"Foil": f"Flow Ace {FLOW_SIZES[flow_index - 1]}", "Rank": 2})
        elif flow_index < len(FLOW_SIZES) - 1:
            top3.append({"Foil": f"Flow Ace {FLOW_SIZES[flow_index + 1]}", "Rank": 2})

        # Rang 3: Infinity Ace (sportliche Alternative)
        infinity_size = FLOW_TO_INFINITY.get(flow_size)
        if infinity_size:
            top3.append({"Foil": f"Infinity Ace {infinity_size}", "Rank": 3})

    # INTERMEDIATE / EXPERT
    else:
        top3.append({"Foil": f"Flow Ace {flow_size}", "Rank": 1})

        # Rang 2: Flow Nachbargröße (sichere Alternative)
        if flow_index > 0:
            top3.append({"Foil": f"Flow Ace {FLOW_SIZES[flow_index - 1]}", "Rank": 2})
        elif flow_index < len(FLOW_SIZES) - 1:
            top3.append({"Foil": f"Flow Ace {FLOW_SIZES[flow_index + 1]}", "Rank": 2})

        # Rang 3: Infinity Ace (sportliche Alternative)
        infinity_size = FLOW_TO_INFINITY.get(flow_size)
        if infinity_size:
            top3.append({"Foil": f"Infinity Ace {infinity_size}", "Rank": 3})

    return top3

# =========================================================
# UI HEADER
# =========================================================
st.title("🪁 Parawing Foilfinder")
st.caption("Spezialisiert für Parawing mit Flow Ace, Infinity Ace & Stride Ace")

# =========================================================
# INPUT FORM
# =========================================================
with st.form("finder"):
    col1, col2, col3 = st.columns(3)

    with col1:
        lvl = st.selectbox("Level", LEVELS)

    with col2:
        gw = st.selectbox("Gewicht", GEWICHT)

    with col3:
        kat = st.selectbox("Kategorie", KATEGORIEN)

    col4, col5 = st.columns(2)

    with col4:
        wind = st.selectbox("Wind", WIND)

    with col5:
        wl = st.selectbox("Wellen", WELLEN)

    # Info zur Kategorie
    if kat == "Freeride":
        st.info("💡 Bei Freeride ist die Wellengröße sekundär.")
    else:
        st.info("🌊 Bei Downwind-Wave ist die Wellengröße primär für die Foil-Wahl.")

    submit = st.form_submit_button("🔍 Foil berechnen", use_container_width=True)

# =========================================================
# CALCULATION
# =========================================================
if submit:
    st.session_state.result = recommend_top3(lvl, gw, kat, wind, wl)

# =========================================================
# RESULTS
# =========================================================
if st.session_state.result:
    st.divider()
    medals = ["🥇", "🥈", "🥉"]

    st.subheader("🏆 Top-Empfehlungen")

    cols = st.columns(3)

    for i, rec in enumerate(st.session_state.result):
        with cols[i]:
            foil_name = rec["Foil"]
            if st.button(
                f"{medals[i]} {foil_name}",
                key=f"rec_{i}",
                use_container_width=True
            ):
                st.session_state.selected_foil = foil_name

# =========================================================
# FOIL SPECS
# =========================================================
if st.session_state.selected_foil:
    foil = st.session_state.selected_foil
    specs = FOIL_SPECS.get(foil)

    st.divider()
    st.subheader(f"🔍 Specs – {foil}")

    if specs:
        cols = st.columns(3)
        for i, (k, v) in enumerate(specs.items()):
            cols[i % 3].metric(k, fmt(v))
    else:
        st.warning(f"Keine Specs für {foil} hinterlegt.")

# =========================================================
# INFO FOOTER
# =========================================================
st.divider()
with st.expander("ℹ️ Wie funktioniert die Empfehlung?"):
    st.markdown("""
    **Basis:** Flow Ace 1080 (70-90kg, Intermediate, Mittel Wind, Kleine Wellen)

    **Anpassungen:**
    - Leichtere Rider (<70kg) → kleinerer Foil
    - Schwerere Rider (>90kg) → größerer Foil
    - Discover Level → größerer Foil
    - Expert Level → kleinerer Foil
    - Schwacher Wind → größerer Foil
    - Starker Wind → kleinerer Foil

    **Kategorien:**
    - **Freeride:** Wellengröße ist sekundär (hat keinen Einfluss auf Empfehlung)
    - **Downwind-Wave:** Wellengröße ist primär (große Wellen → kleinerer Foil)

    **Rangierung:**
    - **Rang 1:** Flow Ace (optimal für deine Bedingungen)
    - **Rang 2:** Flow Ace Nachbargröße (sichere Alternative)
    - **Rang 3:** Infinity Ace (sportliche Alternative - wendiger, etwas größer wegen weniger Lift)

    **Stride Ace für Discover:**
    - Bei schwachen Bedingungen (schwacher Wind oder Flachwasser)
    - Stride Ace 1740 für Rider 70-90kg und >90kg
    - Stride Ace 1360 für Rider <70kg
    - Flow/Infinity als Alternative auf Platz 2/3
    """)
