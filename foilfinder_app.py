import streamlit as st
import pandas as pd
from foil_specs import FOIL_SPECS

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Foilfinder", layout="wide")
DATA_FILE = "foilfinder_functional_fixed.csv"

# =========================================================
# LOAD DATA
# =========================================================
df = pd.read_csv(DATA_FILE)

META_COLS = ["Disziplin", "Level", "Gewicht", "Kategorie", "Wind", "Wellen"]
FOIL_NAMES = [c for c in df.columns if c not in META_COLS]

# =========================================================
# REGELN
# =========================================================
# Disziplinen ohne Wind
WIND_IRRELEVANT = ["Pronefoil", "Pumpfoil", "Downwind"]  # Downwind = SUP-Foiling

# Kategorien
ALL_KATS = list(df["Kategorie"].unique())

KATEGORIEN_PRO_DISZIPLIN = {
    "Downwind": [k for k in ALL_KATS if k not in ["Jumping", "Lightwindfoil"]],
    "Pumpfoil": [],
    "Pronefoil": [],               # Kategorie ignoriert
    "Wingfoil": ALL_KATS,
    "Parawing": ALL_KATS,
}

# Wellen-Regeln
ALL_WELLEN = list(df["Wellen"].unique())
WELLEN_PRO_DISZIPLIN = {
    "Pronefoil": [w for w in ALL_WELLEN if w != "Flachwasser"]
}

# =========================================================
# UI LABEL MAPPINGS
# =========================================================
DISZIPLIN_LABELS = {"Downwind": "SUP-Foiling"}
KATEGORIE_LABELS = {"Downwind": "SUP-Foiling"}

def display_disziplin(d):
    return DISZIPLIN_LABELS.get(d, d)

def internal_disziplin(label):
    return {v: k for k, v in DISZIPLIN_LABELS.items()}.get(label, label)

def display_kategorie(k):
    return KATEGORIE_LABELS.get(k, k)

def internal_kategorie(label):
    return {v: k for k, v in KATEGORIE_LABELS.items()}.get(label, label)

# =========================================================
# SESSION STATE
# =========================================================
for k in ["result_a", "result_b", "selected_foil"]:
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
def recommend(df, user):
    # --- Basisfilter ---
    base = df[
        (df["Disziplin"] == user["Disziplin"]) &
        (df["Level"] == user["Level"]) &
        (df["Gewicht"] == user["Gewicht"])
    ]

    # Kategorie nur filtern, wenn relevant
    if user["Disziplin"] not in ["Pronefoil", "Pumpfoil"]:
        base = base[base["Kategorie"] == user["Kategorie"]]

    if base.empty:
        return None

    scores = {f: 0 for f in FOIL_NAMES}

    for _, r in base.iterrows():
        for f in FOIL_NAMES:
            scores[f] += {1: 3, 2: 2, 3: 1}.get(r[f], 0)

        if user["Disziplin"] not in WIND_IRRELEVANT and r["Wind"] == user["Wind"]:
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
# UI HEADER
# =========================================================
st.title("🪁 Foilfinder")
compare_mode = st.checkbox("🔁 Vergleich Foil A / Foil B")

DISZIPLINEN_UI = [display_disziplin(d) for d in df["Disziplin"].unique()]
LEVELS = df["Level"].unique()
GEWICHTE = df["Gewicht"].unique()
WINDE = df["Wind"].unique()
WELLEN = df["Wellen"].unique()

# =========================================================
# INPUT FORM
# =========================================================
with st.form("finder"):
    cols = st.columns(2) if compare_mode else [st.container()]
    users = []

    for i, col in enumerate(cols):
        with col:
            tag = "A" if i == 0 else "B"
            st.subheader(f"Foil {tag}")

            disz_ui = st.selectbox("Disziplin", DISZIPLINEN_UI, key=f"disz_{tag}")
            disz = internal_disziplin(disz_ui)

            if disz in WIND_IRRELEVANT:
                st.info("💡 Für diese Disziplin ist kein Wind nötig.")

            lvl = st.selectbox("Level", LEVELS, key=f"lvl_{tag}")
            gw = st.selectbox("Gewicht", GEWICHTE, key=f"gw_{tag}")

            allowed_kats = KATEGORIEN_PRO_DISZIPLIN.get(disz, [])

            if not allowed_kats:
                kat = "nicht relevant"
                st.info("💡 Für diese Disziplin ist keine Kategorie nötig.")
            else:
                kat_ui = st.selectbox(
                    "Kategorie",
                    [display_kategorie(k) for k in allowed_kats],
                    key=f"kat_{tag}"
                )
                kat = internal_kategorie(kat_ui)

            if disz in WIND_IRRELEVANT:
                wind = "nicht relevant"
            else:
                wind = st.selectbox("Wind", WINDE, key=f"wind_{tag}")

            allowed_wellen = WELLEN_PRO_DISZIPLIN.get(disz, WELLEN)
            wl = st.selectbox("Wellen", allowed_wellen, key=f"wl_{tag}")

            users.append(
                dict(
                    Disziplin=disz,
                    Level=lvl,
                    Gewicht=gw,
                    Kategorie=kat,
                    Wind=wind,
                    Wellen=wl,
                )
            )

    submit = st.form_submit_button("🔍 Foil berechnen")

# =========================================================
# CALCULATION
# =========================================================
if submit:
    st.session_state.result_a = recommend(df, users[0])
    st.session_state.result_b = recommend(df, users[1]) if compare_mode else None

# =========================================================
# RESULTS
# =========================================================
if st.session_state.result_a is not None:
    st.divider()
    medals = ["🥇", "🥈", "🥉"]

    if compare_mode and st.session_state.result_b is not None:
        ca, cb = st.columns(2)

        with ca:
            st.subheader("🏆 Foil A – Top 3")
            for i, r in st.session_state.result_a.head(3).iterrows():
                if st.button(f"{medals[i]} {r['Foil']}", key=f"a_{r['Foil']}"):
                    st.session_state.selected_foil = r["Foil"]

        with cb:
            st.subheader("🏆 Foil B – Top 3")
            for i, r in st.session_state.result_b.head(3).iterrows():
                if st.button(f"{medals[i]} {r['Foil']}", key=f"b_{r['Foil']}"):
                    st.session_state.selected_foil = r["Foil"]
    else:
        st.subheader("🏆 Top-Empfehlungen")
        for i, r in st.session_state.result_a.head(3).iterrows():
            if st.button(f"{medals[i]} {r['Foil']}", key=f"s_{r['Foil']}"):
                st.session_state.selected_foil = r["Foil"]

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
