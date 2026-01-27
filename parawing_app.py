import streamlit as st
from foil_specs import FOIL_SPECS

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Foilfinder", layout="wide")

# =========================================================
# FOIL SIZES
# =========================================================
# Parawing foils
FLOW_SIZES = [720, 900, 1080, 1260]
STRIDE_ACE_SIZES = [1360, 1740]
INFINITY_PARAWING_SIZES = [540, 690, 840, 990, 1140, 1390]

# Wingfoil foils
PACER_SIZES = [950, 1250, 1550, 1850, 2200]
INFINITY_WINGFOIL_SIZES = [540, 690, 840, 990, 1140, 1390]
FLOW_WINGFOIL_SIZES = [720, 900, 1080, 1260]

# Baselines
FLOW_STANDARD = 1080
FLOW_STANDARD_INDEX = FLOW_SIZES.index(FLOW_STANDARD)
INFINITY_WINGFOIL_STANDARD = 990
INFINITY_WINGFOIL_STANDARD_INDEX = INFINITY_WINGFOIL_SIZES.index(INFINITY_WINGFOIL_STANDARD)

# Flow → Infinity Mapping (for Parawing)
FLOW_TO_INFINITY = {
    720: 840,
    900: 990,
    1080: 1140,
    1260: 1390
}

# =========================================================
# PARAMETERS
# =========================================================
DISCIPLINES = ["Parawing", "Wingfoil"]
LEVELS = ["Discover", "Discover to Intermediate", "Intermediate to Expert", "Expert"]
WEIGHT = ["<70", "70-90", ">90"]
CATEGORIES_PARAWING = ["Freeride", "Downwind-Wave"]
CATEGORIES_WINGFOIL = ["Freeride"]
WIND = ["Light", "Medium", "Strong"]
WAVES_DOWNWIND = ["Small Waves (<0.5m)", "Medium Waves (0.5-1m)", "Big Waves (>1m)"]

# =========================================================
# FOIL PROPERTIES (for scoring)
# =========================================================
PERFORMANCE_PARAMS = ["Speed", "Lift", "Glide", "Maneuverability", "Pump", "Ease of use"]

FOIL_PROPERTIES = {
    "Flow Ace": {
        "Speed": 4.0,
        "Lift": 4.0,
        "Glide": 5.0,
        "Maneuverability": 4.0,
        "Pump": 4.0,
        "Ease of use": 3.5,
    },
    "Infinity Ace": {
        "Speed": 4.5,
        "Lift": 3.5,
        "Glide": 3.5,
        "Maneuverability": 5.0,
        "Pump": 3.5,
        "Ease of use": 4.5,
    },
    "Stride Ace": {
        "Speed": 3.0,
        "Lift": 4.5,
        "Glide": 4.0,
        "Maneuverability": 3.5,
        "Pump": 5.0,
        "Ease of use": 4.0,
    },
    "Stride": {  # For Stride 2050
        "Speed": 3.0,
        "Lift": 5.0,
        "Glide": 4.0,
        "Maneuverability": 3.5,
        "Pump": 5.0,
        "Ease of use": 4.0,
    },
    "Pacer": {
        "Speed": 3.5,
        "Lift": 4.5,
        "Glide": 3.5,
        "Maneuverability": 4.5,
        "Pump": 3.0,
        "Ease of use": 5.0,
    },
}

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

def get_foil_type(foil_name):
    """Extract foil type from full foil name (e.g., 'Flow Ace 1080' -> 'Flow Ace')"""
    for foil_type in FOIL_PROPERTIES.keys():
        if foil_type in foil_name:
            return foil_type
    return None

def calculate_foil_score(foil_name, user_weights):
    """Calculate score for a foil based on user preferences"""
    foil_type = get_foil_type(foil_name)
    if not foil_type or foil_type not in FOIL_PROPERTIES:
        return 0

    properties = FOIL_PROPERTIES[foil_type]
    score = sum(user_weights[param] * properties[param] for param in PERFORMANCE_PARAMS)
    return score

def rerank_by_score(foils, user_weights):
    """Re-rank foils based on user preference scores"""
    # Check if user has customized preferences (any slider != 0)
    default_weight = 0.0
    has_custom_prefs = any(user_weights[param] != default_weight for param in PERFORMANCE_PARAMS)

    if not has_custom_prefs:
        # No custom preferences, return original ranking
        return foils

    # Calculate scores for all foils
    scored_foils = []
    for foil_dict in foils:
        foil_name = foil_dict["Foil"]
        score = calculate_foil_score(foil_name, user_weights)
        scored_foils.append({
            "Foil": foil_name,
            "Score": score,
            "Rank": foil_dict["Rank"]  # Keep original rank for reference
        })

    # Sort by score descending
    scored_foils.sort(key=lambda x: x["Score"], reverse=True)

    # Re-assign ranks
    for i, foil in enumerate(scored_foils):
        foil["Rank"] = i + 1

    return scored_foils

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
        offset += 2
    elif level == "Discover to Intermediate":
        offset += 1
    elif level == "Intermediate to Expert":
        offset += 0
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
    Stride Ace only for Discover/Discover to Intermediate in gentle conditions:
    - Freeride: Light wind only
    - Downwind-Wave: Small waves only
    - Only if Flow >= 1080 (generally larger foil needed)
    """
    if level not in ["Discover", "Discover to Intermediate"]:
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

    # DISCOVER / DISCOVER TO INTERMEDIATE with Stride Ace preference
    if should_recommend_stride_ace(level, weight, category, wind, waves, flow_size):

        if level == "Discover":
            # Discover: Heavier riders (70-90 or >90): Stride 1740 possible
            if weight in ["70-90", ">90"]:
                top3.append({"Foil": "Stride Ace 1740", "Rank": 1})
                top3.append({"Foil": "Stride Ace 1360", "Rank": 2})
                top3.append({"Foil": f"Flow Ace {flow_size}", "Rank": 3})
            # Discover: Lighter riders (<70): Stride 1740 omitted
            else:
                top3.append({"Foil": "Stride Ace 1360", "Rank": 1})
                top3.append({"Foil": f"Flow Ace {flow_size}", "Rank": 2})
                if flow_index > 0:
                    top3.append({"Foil": f"Flow Ace {FLOW_SIZES[flow_index - 1]}", "Rank": 3})
                elif flow_index < len(FLOW_SIZES) - 1:
                    top3.append({"Foil": f"Flow Ace {FLOW_SIZES[flow_index + 1]}", "Rank": 3})
        else:
            # Discover to Intermediate: Stride 1360 as base
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
# WINGFOIL RECOMMENDATION LOGIC
# =========================================================
def calculate_wingfoil_offset(level, weight, wind):
    """Calculate size offset for Wingfoil based on level, weight, and wind."""
    offset = 0

    # Weight
    if weight == "<70":
        offset -= 1
    elif weight == ">90":
        offset += 1

    # Level
    if level == "Discover":
        offset += 2
    elif level == "Discover to Intermediate":
        offset += 1
    elif level == "Intermediate to Expert":
        offset += 0
    elif level == "Expert":
        offset -= 1

    # Wind
    if wind == "Light":
        offset += 1
    elif wind == "Strong":
        offset -= 1

    return offset

def get_optimal_wingfoil_size(level, weight, wind, foil_type):
    """Get optimal size for Wingfoil based on foil type (Pacer, Flow, or Infinity)."""
    offset = calculate_wingfoil_offset(level, weight, wind)

    if foil_type == "Pacer":
        # Pacer baseline: 1250 (index 1) - allows 2200 for heavy riders in light wind
        base_index = 1
        sizes = PACER_SIZES
    elif foil_type == "Flow":
        # Flow baseline: 900 (index 1) - analog to Infinity 990
        base_index = 1
        sizes = FLOW_WINGFOIL_SIZES
    else:  # Infinity
        # Infinity baseline: 990 (index 3) - analog to Flow 900
        base_index = INFINITY_WINGFOIL_STANDARD_INDEX
        sizes = INFINITY_WINGFOIL_SIZES

    target_index = base_index + offset
    target_index = max(0, min(target_index, len(sizes) - 1))
    return sizes[target_index]

def recommend_top3_wingfoil(level, weight, wind):
    """Recommend top 3 foils for Wingfoil Freeride."""
    top3 = []

    # Discover: Only Pacer foils
    if level == "Discover":
        pacer_size = get_optimal_wingfoil_size(level, weight, wind, "Pacer")
        pacer_index = PACER_SIZES.index(pacer_size)

        top3.append({"Foil": f"Pacer {pacer_size}", "Rank": 1})

        # Rank 2: Neighbor Pacer size
        if pacer_index < len(PACER_SIZES) - 1:
            top3.append({"Foil": f"Pacer {PACER_SIZES[pacer_index + 1]}", "Rank": 2})
        elif pacer_index > 0:
            top3.append({"Foil": f"Pacer {PACER_SIZES[pacer_index - 1]}", "Rank": 2})

        # Rank 3: Another Pacer alternative
        if pacer_index > 0 and pacer_index < len(PACER_SIZES) - 1:
            # If in middle, offer smaller or larger based on previous choice
            if len(top3) > 1 and str(PACER_SIZES[pacer_index + 1]) in top3[1]["Foil"]:
                top3.append({"Foil": f"Pacer {PACER_SIZES[pacer_index - 1]}", "Rank": 3})
            else:
                top3.append({"Foil": f"Pacer {PACER_SIZES[pacer_index + 1]}", "Rank": 3})
        elif pacer_index == 0 and len(PACER_SIZES) > 2:
            top3.append({"Foil": f"Pacer {PACER_SIZES[2]}", "Rank": 3})
        elif pacer_index == len(PACER_SIZES) - 1 and len(PACER_SIZES) > 2:
            top3.append({"Foil": f"Pacer {PACER_SIZES[pacer_index - 2]}", "Rank": 3})

    # Discover to Intermediate: Pacer Rank 1, Infinity Rank 2, Flow Rank 3
    elif level == "Discover to Intermediate":
        pacer_size = get_optimal_wingfoil_size(level, weight, wind, "Pacer")
        flow_size = get_optimal_wingfoil_size(level, weight, wind, "Flow")
        infinity_size = get_optimal_wingfoil_size(level, weight, wind, "Infinity")

        top3.append({"Foil": f"Pacer {pacer_size}", "Rank": 1})
        top3.append({"Foil": f"Infinity Ace {infinity_size}", "Rank": 2})
        top3.append({"Foil": f"Flow Ace {flow_size}", "Rank": 3})

    # Intermediate to Expert: Infinity Rank 1, Flow Rank 2, Pacer Rank 3
    elif level == "Intermediate to Expert":
        pacer_size = get_optimal_wingfoil_size(level, weight, wind, "Pacer")
        flow_size = get_optimal_wingfoil_size(level, weight, wind, "Flow")
        infinity_size = get_optimal_wingfoil_size(level, weight, wind, "Infinity")

        top3.append({"Foil": f"Infinity Ace {infinity_size}", "Rank": 1})
        top3.append({"Foil": f"Flow Ace {flow_size}", "Rank": 2})
        top3.append({"Foil": f"Pacer {pacer_size}", "Rank": 3})

    # Expert: Infinity Rank 1, Flow Rank 2, smaller alternative Rank 3 (NO Pacer)
    else:  # Expert
        flow_size = get_optimal_wingfoil_size(level, weight, wind, "Flow")
        infinity_size = get_optimal_wingfoil_size(level, weight, wind, "Infinity")

        # Special case: Light riders + Strong wind = prefer smaller Infinity progression
        if weight == "<70" and wind == "Strong":
            top3.append({"Foil": "Infinity Ace 540", "Rank": 1})
            top3.append({"Foil": "Infinity Ace 690", "Rank": 2})
            top3.append({"Foil": f"Flow Ace {flow_size}", "Rank": 3})
        else:
            top3.append({"Foil": f"Infinity Ace {infinity_size}", "Rank": 1})
            top3.append({"Foil": f"Flow Ace {flow_size}", "Rank": 2})
            # Rank 3: smaller alternative (prefer Infinity)
            infinity_index = INFINITY_WINGFOIL_SIZES.index(infinity_size)
            if infinity_index > 0:
                top3.append({"Foil": f"Infinity Ace {INFINITY_WINGFOIL_SIZES[infinity_index - 1]}", "Rank": 3})
            else:
                flow_index = FLOW_WINGFOIL_SIZES.index(flow_size)
                if flow_index > 0:
                    top3.append({"Foil": f"Flow Ace {FLOW_WINGFOIL_SIZES[flow_index - 1]}", "Rank": 3})

    return top3

# =========================================================
# UI HEADER
# =========================================================
st.title("🪁 Foilfinder")
st.caption("Find your optimal foil for Parawing or Wingfoil")

# =========================================================
# INPUT FORM
# =========================================================
# Row 1: Discipline
discipline = st.selectbox("Discipline", DISCIPLINES)

# Row 2: Category (discipline-specific)
if discipline == "Parawing":
    kat = st.selectbox("Category", CATEGORIES_PARAWING)
else:  # Wingfoil
    kat = st.selectbox("Category", CATEGORIES_WINGFOIL)

# Row 3: Level & Weight
col1, col2 = st.columns(2)
with col1:
    lvl = st.radio("Level", options=LEVELS, index=1, horizontal=False)
with col2:
    weight_kg = st.slider("Weight (kg)", min_value=32, max_value=125, value=80, step=1)
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

# Row 4 & 5: Discipline + Category-specific inputs
if discipline == "Parawing":
    if kat == "Freeride":
        # Parawing Freeride: Only wind matters
        wind = st.selectbox("Wind", WIND, help="Based on your usual riding conditions")
        wl = None
        style_preference = None
        st.info("💡 For Parawing Freeride, wind is primary for getting on the foil.")
    else:  # Downwind-Wave
        # Parawing Downwind-Wave: Only waves matter
        wl = st.selectbox("Waves", WAVES_DOWNWIND)
        wind = None
        style_preference = None
        st.info("🌊 For Parawing Downwind-Wave, wave size is primary for foil selection.")
else:  # Wingfoil
    # Wingfoil Freeride: Wind only
    wind = st.selectbox("Wind", WIND, help="Based on your usual riding conditions")
    wl = None
    style_preference = None
    st.info("🪶 For Wingfoil Freeride, wind conditions determine the optimal foil. Use the preference sliders below to fine-tune.")

# =========================================================
# PERFORMANCE PREFERENCES (Optional Fine-Tuning)
# =========================================================
with st.expander("🎯 Fine-tune your preferences (optional)"):
    st.caption("Adjust sliders to prioritize specific foil characteristics.")

    user_weights = {}
    cols = st.columns(2)

    for i, param in enumerate(PERFORMANCE_PARAMS):
        with cols[i % 2]:
            user_weights[param] = st.slider(
                param,
                min_value=0.0,
                max_value=5.0,
                value=0.0,
                step=0.5,
                key=f"weight_{param}"
            )

# =========================================================
# CALCULATION
# =========================================================
# Get base recommendations
if discipline == "Parawing":
    base_result = recommend_top3(lvl, gw, kat, wind, wl)
else:  # Wingfoil
    base_result = recommend_top3_wingfoil(lvl, gw, wind)

# Apply user preference scoring to re-rank
st.session_state.result = rerank_by_score(base_result, user_weights)

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
    if discipline == "Parawing":
        st.markdown("""
        ### Parawing

        **Baseline:** Flow Ace 1080 (70-90kg, Intermediate)

        **Adjustments (always applied):**
        - Lighter riders (<70kg) → smaller foil
        - Heavier riders (>90kg) → larger foil
        - Discover level → much larger foil (+2)
        - Discover to Intermediate → larger foil (+1)
        - Intermediate to Expert → neutral (0)
        - Expert level → smaller foil (-1)

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
        - **Rank 3:** Infinity Ace (sporty alternative - more agile)

        **Stride Ace for Discover/Discover to Intermediate (gentle conditions only):**
        - Freeride: Light wind only
        - Downwind-Wave: Small waves (<0.5m) only

        | Level | Heavy riders (70-90kg, >90kg) | Light riders (<70kg) |
        |-------|------------------------------|---------------------|
        | Discover | Stride 1740 → 1360 → Flow | Stride 1360 → Flow |
        | Discover to Intermediate | Stride 1360 → Flow | Stride 1360 → Flow |
        """)
    else:  # Wingfoil
        st.markdown("""
        ### Wingfoil Freeride

        **Baselines:**
        - Pacer 1250 (80kg, Intermediate, Medium Wind)
        - Flow Ace 900 (80kg, Intermediate, Medium Wind)
        - Infinity Ace 990 (80kg, Intermediate, Medium Wind)

        **Adjustments (always applied):**
        - Lighter riders (<70kg) → smaller foil
        - Heavier riders (>90kg) → larger foil
        - Discover level → much larger foil (+2)
        - Discover to Intermediate → larger foil (+1)
        - Intermediate to Expert → neutral (0)
        - Expert level → smaller foil (-1)
        - Light wind → larger foil
        - Strong wind → smaller foil

        **Fine-Tuning with Performance Sliders:**
        - Use the optional sliders to prioritize specific characteristics
        - Higher values (3-5) = more important to you
        - Default (0) = use standard ranking based on level
        - Examples: High Glide/Pump favors Flow Ace, High Speed/Maneuverability favors Infinity Ace

        **Foil Properties:**

        | Foil | Speed | Lift | Glide | Maneuverability | Pump | Ease of use |
        |------|-------|------|-------|-----------------|------|-------------|
        | Flow Ace | 4.0 | 4.0 | **5.0** | 4.0 | 4.0 | 3.5 |
        | Infinity Ace | 4.5 | 3.5 | 3.5 | **5.0** | 3.5 | 4.5 |
        | Pacer | 3.5 | 4.5 | 3.5 | 4.5 | 3.0 | **5.0** |

        **Default Ranking by Level:**

        | Level | Rank 1 | Rank 2 | Rank 3 |
        |-------|--------|--------|--------|
        | Discover | Pacer | Pacer | Pacer |
        | Discover to Intermediate | Pacer | Infinity Ace | Flow Ace |
        | Intermediate to Expert | Infinity Ace | Flow Ace | Pacer |
        | Expert | Infinity Ace | Flow Ace | smaller alternative |

        **Why this order?**
        - **Discover:** Pacer only - easiest to use (5.0)
        - **Discover to Intermediate:** Infinity before Flow - better ease of use (4.5 vs 3.5)
        - **Intermediate to Expert & Expert:** Infinity first - better speed & maneuverability
        - Want more **Glide/Pump**? → Increase sliders to move Flow Ace up
        """)
