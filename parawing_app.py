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

# Flow → Infinity Mapping (Infinity slightly larger due to less lift)
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
WEIGHT = ["<70", "70-90", ">90"]
CATEGORIES = ["Freeride", "Downwind-Wave"]
WIND = ["Light", "Medium", "Strong"]
WAVES_DOWNWIND = ["Small Waves (<0.5m)", "Medium Waves (0.5-1m)", "Big Waves (>1m)"]

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
def calculate_flow_offset(level, weight, category, wind, waves):
    offset = 0

    # Weight
    if weight == "<70":
        offset -= 1
    elif weight == ">90":
        offset += 1

    # Level
    if level == "Discover":
        offset += 1
    elif level == "Expert":
        offset -= 1

    # Category-specific conditions
    if category == "Freeride":
        # For Freeride: Only wind matters
        if wind and wind == "Light":
            offset += 1
        elif wind and wind == "Strong":
            offset -= 1
    elif category == "Downwind-Wave":
        # For Downwind-Wave: Only waves matter
        if waves:
            if "Small" in waves:
                offset += 1
            elif "Big" in waves:
                offset -= 1
            # Medium = 0 (neutral)

    return offset

def get_optimal_flow(level, weight, category, wind, waves):
    offset = calculate_flow_offset(level, weight, category, wind, waves)
    target_index = FLOW_STANDARD_INDEX + offset
    target_index = max(0, min(target_index, len(FLOW_SIZES) - 1))
    return FLOW_SIZES[target_index], offset

def should_recommend_stride_ace(level, weight, category, wind, waves, flow_size):
    """
    Stride Ace only for Discover in gentle conditions:
    - Freeride: Light wind only
    - Downwind-Wave: Small waves only
    - Only if Flow >= 1080 (generally larger foil needed)
    """
    if level != "Discover":
        return False

    if flow_size < 1080:
        return False

    # Category-specific gentle conditions check
    if category == "Freeride":
        # Stride only for light wind in Freeride
        return wind == "Light"
    elif category == "Downwind-Wave":
        # Stride only for small waves in Downwind-Wave
        return waves and "Small" in waves

    return False

def recommend_top3(level, weight, category, wind, waves):
    flow_size, offset = get_optimal_flow(level, weight, category, wind, waves)
    flow_index = FLOW_SIZES.index(flow_size)

    top3 = []

    # DISCOVER with Stride Ace preference
    if should_recommend_stride_ace(level, weight, category, wind, waves, flow_size):

        # Heavier riders (70-90 or >90): Stride 1740 possible
        if weight in ["70-90", ">90"]:
            top3.append({"Foil": "Stride Ace 1740", "Rank": 1})
            top3.append({"Foil": "Stride Ace 1360", "Rank": 2})
            top3.append({"Foil": f"Flow Ace {flow_size}", "Rank": 3})

        # Lighter riders (<70): Stride 1740 omitted
        else:
            top3.append({"Foil": "Stride Ace 1360", "Rank": 1})
            top3.append({"Foil": f"Flow Ace {flow_size}", "Rank": 2})
            if flow_index > 0:
                top3.append({"Foil": f"Flow Ace {FLOW_SIZES[flow_index - 1]}", "Rank": 3})
            elif flow_index < len(FLOW_SIZES) - 1:
                top3.append({"Foil": f"Flow Ace {FLOW_SIZES[flow_index + 1]}", "Rank": 3})

    # DISCOVER without Stride (stronger wind / bigger waves)
    elif level == "Discover":
        top3.append({"Foil": f"Flow Ace {flow_size}", "Rank": 1})

        # Rank 2: Flow neighbor size (safe alternative)
        if flow_index > 0:
            top3.append({"Foil": f"Flow Ace {FLOW_SIZES[flow_index - 1]}", "Rank": 2})
        elif flow_index < len(FLOW_SIZES) - 1:
            top3.append({"Foil": f"Flow Ace {FLOW_SIZES[flow_index + 1]}", "Rank": 2})

        # Rank 3: Infinity Ace (sporty alternative)
        infinity_size = FLOW_TO_INFINITY.get(flow_size)
        if infinity_size:
            top3.append({"Foil": f"Infinity Ace {infinity_size}", "Rank": 3})

    # INTERMEDIATE / EXPERT
    else:
        top3.append({"Foil": f"Flow Ace {flow_size}", "Rank": 1})

        # Rank 2: Flow neighbor size (safe alternative)
        if flow_index > 0:
            top3.append({"Foil": f"Flow Ace {FLOW_SIZES[flow_index - 1]}", "Rank": 2})
        elif flow_index < len(FLOW_SIZES) - 1:
            top3.append({"Foil": f"Flow Ace {FLOW_SIZES[flow_index + 1]}", "Rank": 2})

        # Rank 3: Infinity Ace (sporty alternative)
        infinity_size = FLOW_TO_INFINITY.get(flow_size)
        if infinity_size:
            top3.append({"Foil": f"Infinity Ace {infinity_size}", "Rank": 3})

    return top3

# =========================================================
# UI HEADER
# =========================================================
st.title("🪁 Parawing Foilfinder")
st.caption("Specialized for Parawing with Flow Ace, Infinity Ace & Stride Ace")

# =========================================================
# INPUT FORM
# =========================================================
# Row 1: Category
kat = st.selectbox("Category", CATEGORIES)

# Row 2: Level & Weight
col1, col2 = st.columns(2)
with col1:
    lvl = st.select_slider("Level", options=LEVELS, value="Intermediate")
with col2:
    weight_kg = st.slider("Weight (kg)", min_value=40, max_value=150, value=80, step=1)
    # Map to weight category
    if weight_kg < 70:
        gw = "<70"
        weight_info = "Light rider"
    elif weight_kg <= 90:
        gw = "70-90"
        weight_info = "Medium rider"
    else:
        gw = ">90"
        weight_info = "Heavy rider"
    st.caption(f"📊 {weight_info} ({gw}kg)")

# Row 3 & 4: Category-specific inputs
if kat == "Freeride":
    # For Freeride: Only wind matters
    wind = st.selectbox("Wind", WIND)
    wl = None  # Waves not relevant
    st.info("💡 For Freeride, wind is primary for getting on the foil.")
else:  # Downwind-Wave
    # For Downwind-Wave: Only waves matter
    wl = st.selectbox("Waves", WAVES_DOWNWIND)
    wind = None  # Wind not relevant
    st.info("🌊 For Downwind-Wave, wave size is primary for foil selection.")

# =========================================================
# CALCULATION
# =========================================================
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
with st.expander("ℹ️ How does the recommendation work?"):
    st.markdown("""
    **Baseline:** Flow Ace 1080 (70-90kg, Intermediate)

    **Adjustments (always applied):**
    - Lighter riders (<70kg) → smaller foil
    - Heavier riders (>90kg) → larger foil
    - Discover level → larger foil
    - Expert level → smaller foil

    **Categories:**
    - **Freeride:** Wind is primary for getting on foil
      - Light wind → larger foil
      - Strong wind → smaller foil
    - **Downwind-Wave:** Wave size is primary for foil selection
      - Small waves (<0.5m) → larger foil
      - Medium waves (0.5-1m) → neutral
      - Big waves (>1m) → smaller foil

    **Ranking:**
    - **Rank 1:** Flow Ace (optimal for your conditions)
    - **Rank 2:** Flow Ace neighbor size (safe alternative)
    - **Rank 3:** Infinity Ace (sporty alternative - more agile, slightly larger due to less lift)

    **Stride Ace for Discover:**
    - Only in gentle conditions:
      - Freeride: Light wind
      - Downwind-Wave: Small waves (<0.5m)
    - Stride Ace 1740 for riders 70-90kg and >90kg
    - Stride Ace 1360 for riders <70kg
    - Flow/Infinity as alternative on Rank 2/3
    """)
