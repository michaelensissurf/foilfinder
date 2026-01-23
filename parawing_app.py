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
WAVES = ["Flat Water", "Small Waves", "Big Waves"]

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

    # Wind
    if wind == "Light":
        offset += 1
    elif wind == "Strong":
        offset -= 1

    # Waves (category dependent)
    if category == "Downwind-Wave":
        # Waves are PRIMARY for Downwind-Wave
        # Small Waves = easier (+1) - more important than wind
        # Big Waves = harder (-1)
        if waves == "Small Waves":
            offset += 1
        elif waves == "Big Waves":
            offset -= 1
    elif category == "Freeride":
        # For Freeride: Flat water/small waves = easier (+1)
        if waves in ["Flat Water", "Small Waves"]:
            offset += 1

    return offset

def get_optimal_flow(level, weight, category, wind, waves):
    offset = calculate_flow_offset(level, weight, category, wind, waves)
    target_index = FLOW_STANDARD_INDEX + offset
    target_index = max(0, min(target_index, len(FLOW_SIZES) - 1))
    return FLOW_SIZES[target_index], offset

def should_recommend_stride_ace(level, weight, category, wind, waves, flow_size):
    """
    Stride Ace only for Discover in gentle conditions:
    - No strong wind (too difficult for beginners)
    - No big waves (too difficult for beginners)
    - Only if Flow >= 1080 (generally larger foil needed)
    """
    if level != "Discover":
        return False

    if flow_size < 1080:
        return False

    # Strong wind or big waves → no Stride (too difficult)
    if wind == "Strong" or waves == "Big Waves":
        return False

    # Stride for light wind or flat water (but not strong/big)
    if wind == "Light" or waves == "Flat Water":
        return True

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
with st.form("finder"):
    col1, col2, col3 = st.columns(3)

    with col1:
        level_slider = st.slider("Level", min_value=0, max_value=100, value=50, step=1)
        # Map to level category
        if level_slider <= 25:
            lvl = "Discover"
            level_info = "Beginner"
        elif level_slider <= 75:
            lvl = "Intermediate"
            level_info = "Intermediate"
        else:
            lvl = "Expert"
            level_info = "Advanced"
        st.caption(f"🎯 {level_info}")

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

    with col3:
        kat = st.selectbox("Category", CATEGORIES)

    col4, col5 = st.columns(2)

    with col4:
        wind = st.selectbox("Wind", WIND)

    with col5:
        # Wave options depending on category
        if kat == "Downwind-Wave":
            wave_options = ["Small Waves", "Big Waves"]
        else:
            wave_options = WAVES
        wl = st.selectbox("Waves", wave_options)

    # Info about category
    if kat == "Freeride":
        st.info("💡 For Freeride, wave size is secondary.")
    else:
        st.info("🌊 For Downwind-Wave, wave size is primary for foil selection.")

    submit = st.form_submit_button("🔍 Calculate Foil", use_container_width=True)

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
with st.expander("ℹ️ How does the recommendation work?"):
    st.markdown("""
    **Baseline:** Flow Ace 1080 (70-90kg, Intermediate, Medium Wind, Small Waves)

    **Adjustments:**
    - Lighter riders (<70kg) → smaller foil
    - Heavier riders (>90kg) → larger foil
    - Discover level → larger foil
    - Expert level → smaller foil
    - Light wind → larger foil
    - Strong wind → smaller foil

    **Categories:**
    - **Freeride:** Wave size is secondary (no impact on recommendation)
    - **Downwind-Wave:** Wave size is primary (big waves → smaller foil)

    **Ranking:**
    - **Rank 1:** Flow Ace (optimal for your conditions)
    - **Rank 2:** Flow Ace neighbor size (safe alternative)
    - **Rank 3:** Infinity Ace (sporty alternative - more agile, slightly larger due to less lift)

    **Stride Ace for Discover:**
    - In gentle conditions (light wind or flat water)
    - Stride Ace 1740 for riders 70-90kg and >90kg
    - Stride Ace 1360 for riders <70kg
    - Flow/Infinity as alternative on Rank 2/3
    """)
