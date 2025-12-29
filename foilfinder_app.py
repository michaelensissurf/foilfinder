import streamlit as st
import pandas as pd
from foil_specs import FOIL_SPECS

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="Foilfinder", layout="centered")

# =========================================================
# DATA
# =========================================================
DATA_FILE = "foilfinder_functional_fixed.csv"
df = pd.read_csv(DATA_FILE)

META_COLS = ["Disziplin", "Level", "Gewicht", "Kategorie", "Wind", "Wellen"]
FOIL_NAMES = [c for c in df.columns if c not in META_COLS]

# =========================================================
# OPTIONS (CSV-KONSISTENT)
# =========================================================
DISZIPLINEN = ["Wingfoil", "Parawing", "Pumpfoil", "Downwind", "Pronefoil"]
KATEGORIEN = ["Freeride", "Downwind-Wave", "Wavesurfing", "Jumping", "Lightwindfoil", "Race"]

LEVELS = df["Level"].unique()
GEWICHTE = ["bis 70 kg", "70-90 kg", "groesser 90 kg"]
WINDE = df["Wind"].unique()
WELLEN = df["Wellen"].unique()

# =========================================================
# HELPERS
# =========================================================
def fmt(v):
    return round(float(v), 1)

# =========================================================
# RECOMMENDATION LOGIC
# =========================================================
def recommend(df, user):
    base = df[
        (df["Disziplin"] == user["Disziplin"]) &
        (df["Level"] == user["Level"]) &
        (df["Gewicht"] == user["Gewicht"]) &
        (df["Kategorie"] == user["Kategorie"])
    ]

    if base.empty:
        return None

    scores = {f: 0 for f in FOIL_NAMES}

    for _, r in base.iterrows():
        for f in FOIL_NAMES:
            if r[f] == 1:
                scores[f] += 3
            elif r[f] == 2:
                scores[f] += 2
            elif r[f] == 3:
                scores[f] += 1

        if user["Wind"] != "__ANY__" and r["Wind"] == user["Wind"]:
            for f in FOIL_NAMES:
                if r[f] == 1:
                    scores[f] += 1

        if r["Wellen"] == user["Wellen"]:
            for f in FOIL_NAMES:
                if r[f] == 1:
                    scores[f] += 1

    return (
        pd.DataFrame(scores.items(), columns=["Foil", "Score"])
        .sort_values("Score", ascending=False)
        .reset_index(drop=True)
    )

# =========================================================
# HEADER
# =========================================================
st.title("🪁 Foilfinder")
compare_mode = st.checkbox("Vergleich zweier Setups")

# =========================================================
# SETUP UI
# =========================================================
if compare_mode:
    col_a, col_b = st.columns(2)
else:
    col_a = st.container()
    col_b = None

# -------------------------
# SETUP A
# -------------------------
with col_a:
    st.subheader("Setup A")

    disziplin = st.selectbox("Disziplin", DISZIPLINEN, key="disziplin_a")
    level = st.selectbox("Level", LEVELS, key="level_a")
    gewicht = st.selectbox("Gewicht", GEWICHTE, key="gewicht_a")
    kategorie = st.selectbox("Kategorie", KATEGORIEN, key="kategorie_a")

    if disziplin != "Pronefoil":
        wind = st.selectbox("Wind", WINDE, key="wind_a")
    else:
        wind = "__ANY__"
        st.caption("Wind ist bei Pronefoil nicht relevant.")

    wellen = st.selectbox("Wellen", WELLEN, key="wellen_a")

# -------------------------
# SETUP B
# -------------------------
if compare_mode and col_b:
    with col_b:
        st.subheader("Setup B")

        disziplin_b = st.selectbox("Disziplin B", DISZIPLINEN, key="disziplin_b")
        level_b = st.selectbox("Level B", LEVELS, key="level_b")
        gewicht_b = st.selectbox("Gewicht B", GEWICHTE, key="gewicht_b")
        kategorie_b = st.selectbox("Kategorie B", KATEGORIEN, key="kategorie_b")

        if disziplin_b != "Pronefoil":
            wind_b = st.selectbox("Wind B", WINDE, key="wind_b")
        else:
            wind_b = "__ANY__"
            st.caption("Wind ist bei Pronefoil nicht relevant.")

        wellen_b = st.selectbox("Wellen B", WELLEN, key="wellen_b")

# =========================================================
# CALCULATE BUTTON
# =========================================================
calculate = st.button("Foil berechnen")

# =========================================================
# CALCULATION
# =========================================================
if calculate:
    st.session_state.pop("selected_foil_a", None)
    st.session_state.pop("selected_foil_b", None)

    user_a = {
        "Disziplin": disziplin,
        "Level": level,
        "Gewicht": gewicht,
        "Kategorie": kategorie,
        "Wind": wind,
        "Wellen": wellen,
    }

    result_a = recommend(df, user_a)
    if result_a is None:
        st.warning("Keine passenden Daten für Setup A.")
        st.stop()

    st.session_state.result_a = result_a

    if compare_mode:
        user_b = {
            "Disziplin": disziplin_b,
            "Level": level_b,
            "Gewicht": gewicht_b,
            "Kategorie": kategorie_b,
            "Wind": wind_b,
            "Wellen": wellen_b,
        }

        result_b = recommend(df, user_b)
        if result_b is None:
            st.warning("Keine passenden Daten für Setup B.")
            st.stop()

        st.session_state.result_b = result_b

# =========================================================
# RESULTS
# =========================================================
if "result_a" in st.session_state:
    medals = ["🥇", "🥈", "🥉"]

    if not compare_mode:
        st.divider()
        st.subheader("Top-Empfehlungen")

        for i, r in st.session_state.result_a.head(3).iterrows():
            if st.button(f"{medals[i]} {r['Foil']}", key=f"a_{r['Foil']}"):
                st.session_state.selected_foil_a = r["Foil"]

    else:
        st.divider()
        col_l, col_r = st.columns(2)

        with col_l:
            st.subheader("Setup A – Top 3")
            for i, r in st.session_state.result_a.head(3).iterrows():
                if st.button(f"{medals[i]} {r['Foil']}", key=f"a_{r['Foil']}"):
                    st.session_state.selected_foil_a = r["Foil"]

        with col_r:
            st.subheader("Setup B – Top 3")
            for i, r in st.session_state.result_b.head(3).iterrows():
                if st.button(f"{medals[i]} {r['Foil']}", key=f"b_{r['Foil']}"):
                    st.session_state.selected_foil_b = r["Foil"]

# =========================================================
# SPECS (ONLY AFTER CLICK)
# =========================================================
if "selected_foil_a" in st.session_state:
    foil = st.session_state.selected_foil_a
    specs = FOIL_SPECS.get(foil)

    if specs:
        st.divider()
        st.subheader(f"Specs – {foil}")
        st.dataframe(
            pd.DataFrame({
                "Eigenschaft": specs.keys(),
                "Wert": [fmt(v) for v in specs.values()],
            }),
            hide_index=True,
            use_container_width=True,
        )

if compare_mode and "selected_foil_b" in st.session_state:
    foil = st.session_state.selected_foil_b
    specs = FOIL_SPECS.get(foil)

    if specs:
        st.divider()
        st.subheader(f"Specs – {foil}")
        st.dataframe(
            pd.DataFrame({
                "Eigenschaft": specs.keys(),
                "Wert": [fmt(v) for v in specs.values()],
            }),
            hide_index=True,
            use_container_width=True,
        )
