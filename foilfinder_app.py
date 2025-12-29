import streamlit as st
import pandas as pd
from foil_specs import FOIL_SPECS

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Foilfinder", layout="wide")

DATA_FILE = "foilfinder_functional_fixed.csv"
WIND_IRRELEVANT = ["Pronefoil", "Pumpfoil"]

# =========================================================
# SESSION STATE (WICHTIG!)
# =========================================================
if "result_a" not in st.session_state:
    st.session_state.result_a = None

if "result_b" not in st.session_state:
    st.session_state.result_b = None

if "selected_foil" not in st.session_state:
    st.session_state.selected_foil = None

# =========================================================
# LOAD DATA
# =========================================================
df = pd.read_csv(DATA_FILE)

META_COLS = ["Disziplin", "Level", "Gewicht", "Kategorie", "Wind", "Wellen"]
FOIL_NAMES = [c for c in df.columns if c not in META_COLS]

# =========================================================
# HELPERS
# =========================================================
def fmt(v):
    return int(v) if float(v).is_integer() else round(v, 1)

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

        # Wind nur berücksichtigen, wenn relevant
        if user["Disziplin"] not in WIND_IRRELEVANT:
            if r["Wind"] == user["Wind"]:
                for f in FOIL_NAMES:
                    if r[f] == 1:
                        scores[f] += 1

        # Wellen immer berücksichtigen
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
# UI HEADER
# =========================================================
st.title("🪁 Foilfinder")
compare_mode = st.checkbox("🔁 Vergleich Foil A / Foil B")

DISZIPLINEN = df["Disziplin"].unique()
LEVELS = df["Level"].unique()
GEWICHTE = df["Gewicht"].unique()
KATEGORIEN = df["Kategorie"].unique()
WINDE = df["Wind"].unique()
WELLEN = df["Wellen"].unique()

# =========================================================
# INPUT FORM
# =========================================================
with st.form("finder"):

    if compare_mode:
        colA, colB = st.columns(2)
    else:
        colA = st.container()

    # ---------------- FOIL A ----------------
    with colA:
        st.subheader("Foil A")

        disziplin = st.selectbox("Disziplin", DISZIPLINEN)

        if disziplin in WIND_IRRELEVANT:
            st.info("💡 Bei Pronefoil und Pumpfoil spielt der Wind keine Rolle.")

        level = st.selectbox("Level", LEVELS)
        gewicht = st.selectbox("Gewicht", GEWICHTE)
        kategorie = st.selectbox("Kategorie", KATEGORIEN)

        c1, c2 = st.columns(2)

        if disziplin in WIND_IRRELEVANT:
            wind = "nicht relevant"
        else:
            wind = c1.selectbox("Wind", WINDE)

        wellen = c2.selectbox("Wellen", WELLEN)

    # ---------------- FOIL B ----------------
    if compare_mode:
        with colB:
            st.subheader("Foil B")

            disziplin_b = st.selectbox("Disziplin", DISZIPLINEN, key="d_b")

            if disziplin_b in WIND_IRRELEVANT:
                st.info("💡 Bei Pronefoil und Pumpfoil spielt der Wind keine Rolle.")

            level_b = st.selectbox("Level", LEVELS, key="l_b")
            gewicht_b = st.selectbox("Gewicht", GEWICHTE, key="g_b")
            kategorie_b = st.selectbox("Kategorie", KATEGORIEN, key="k_b")

            c1b, c2b = st.columns(2)

            if disziplin_b in WIND_IRRELEVANT:
                wind_b = "nicht relevant"
            else:
                wind_b = c1b.selectbox("Wind", WINDE, key="w_b")

            wellen_b = c2b.selectbox("Wellen", WELLEN, key="we_b")

    submit = st.form_submit_button("🔍 Foil berechnen")

# =========================================================
# CALCULATION (STATEFUL!)
# =========================================================
if submit:
    user_a = {
        "Disziplin": disziplin,
        "Level": level,
        "Gewicht": gewicht,
        "Kategorie": kategorie,
        "Wind": wind,
        "Wellen": wellen,
    }

    st.session_state.result_a = recommend(df, user_a)

    if compare_mode:
        user_b = {
            "Disziplin": disziplin_b,
            "Level": level_b,
            "Gewicht": gewicht_b,
            "Kategorie": kategorie_b,
            "Wind": wind_b,
            "Wellen": wellen_b,
        }
        st.session_state.result_b = recommend(df, user_b)
    else:
        st.session_state.result_b = None

# =========================================================
# RESULTS
# =========================================================
if st.session_state.result_a is not None:

    result_a = st.session_state.result_a
    result_b = st.session_state.result_b

    st.divider()
    medals = ["🥇", "🥈", "🥉"]

    if compare_mode and result_b is not None:
        ca, cb = st.columns(2)

        with ca:
            st.subheader("🏆 Foil A – Top 3")
            for i, r in result_a.head(3).iterrows():
                if st.button(f"{medals[i]} {r['Foil']}", key=f"a_{r['Foil']}"):
                    st.session_state.selected_foil = r["Foil"]

        with cb:
            st.subheader("🏆 Foil B – Top 3")
            for i, r in result_b.head(3).iterrows():
                if st.button(f"{medals[i]} {r['Foil']}", key=f"b_{r['Foil']}"):
                    st.session_state.selected_foil = r["Foil"]

    else:
        st.subheader("🏆 Top-Empfehlungen")
        for i, r in result_a.head(3).iterrows():
            if st.button(f"{medals[i]} {r['Foil']}", key=f"s_{r['Foil']}"):
                st.session_state.selected_foil = r["Foil"]

# =========================================================
# FOIL SPECS (CLICK-STABLE)
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
