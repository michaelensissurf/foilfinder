import streamlit as st
import pandas as pd
import os
from foils import FOILS

# -------------------------------------------------
# Config
# -------------------------------------------------
st.set_page_config(page_title="Foilfinder – Experteneingabe", layout="wide")

FILE = "progress.csv"
FOIL_NAMES = [v for k, v in FOILS.items() if k != 0]  # ohne "nicht relevant"

LEVELS = ["Discovers", "Discovers to Intermediate", "Intermediate to Experts"]
GEWICHTE = ["bis 70 kg", "70–90 kg", "grösser 90 kg"]
DISZIPLINEN = [
    "Freeride", "Downwind-Wave", "Wavesurfing",
    "Jumping", "Lightwindfoil", "Flatwater", "Race"
]
WINDE = ["Schwachwind", "Medium Wind", "Starkwind", "nicht notwendig"]
WELLEN = ["Flachwasser", "Kleine Wellen", "Grosse Wellen", "nicht notwendig"]

# -------------------------------------------------
# Daten laden / erzeugen
# -------------------------------------------------
if not os.path.exists(FILE):
    rows = [
        (l, g, d, w, wa)
        for l in LEVELS
        for g in GEWICHTE
        for d in DISZIPLINEN
        for w in WINDE
        for wa in WELLEN
    ]
    df = pd.DataFrame(rows, columns=["Level", "Gewicht", "Disziplin", "Wind", "Wellen"])
    for f in FOIL_NAMES:
        df[f] = pd.NA
    df.to_csv(FILE, index=False)
else:
    df = pd.read_csv(FILE)

# -------------------------------------------------
# Logik
# -------------------------------------------------
def row_done(row):
    return (row[FOIL_NAMES].fillna(0) == 1).any()

def get_last_4_context(df, current_row):
    mask = (
        (df["Level"] == current_row.Level) &
        (df["Gewicht"] == current_row.Gewicht) &
        (df["Disziplin"] == current_row.Disziplin)
    )

    subset = df[mask].copy()
    subset = subset[subset.apply(row_done, axis=1)]

    last = subset.tail(4)

    result = []
    for _, r in last.iterrows():
        foil = None
        for f in FOIL_NAMES:
            if r[f] == 1:
                foil = f
                break
        result.append({
            "Wind": r["Wind"],
            "Wellen": r["Wellen"],
            "Foil": foil
        })

    return result[::-1]

# -------------------------------------------------
# Fortschritt
# -------------------------------------------------
open_rows = df[~df.apply(row_done, axis=1)]
done = len(df) - len(open_rows)

st.title("Foilfinder – Experteneingabe")
st.progress(done / len(df))
st.caption(f"{done} / {len(df)} Situationen bewertet")

if open_rows.empty:
    st.success("🎉 Alle Situationen bewertet")
    st.stop()

idx = open_rows.index[0]
row = df.loc[idx]

# -------------------------------------------------
# Aktuelle Situation
# -------------------------------------------------
st.subheader("Aktuelle Situation")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Level", row.Level)
c2.metric("Gewicht", row.Gewicht)
c3.metric("Disziplin", row.Disziplin)
c4.metric("Wind", row.Wind)
c5.metric("Wellen", row.Wellen)

# -------------------------------------------------
# Layout
# -------------------------------------------------
left, center, right = st.columns([1.3, 1.6, 1.4])

# -------- Foil-Übersicht --------
with left:
    st.subheader("Foil-Übersicht")
    for k, v in FOILS.items():
        st.markdown(f"**{k:>2}** – {v}")

# -------- Eingabe --------
with center:
    st.subheader("Auswahl per Nummer")

    with st.form("foil_form"):
        foil_input = st.text_input(
            "Foils (z. B. 14 13 9 oder 0 für nicht relevant)",
            placeholder="Top-1 [Top-2 Top-3]"
        )
        use_prev = st.checkbox("Gleich wie vorher")
        submit = st.form_submit_button("✔ Speichern & weiter")

    if submit:
        if use_prev:
            if "last_selection" not in st.session_state:
                st.warning("Noch keine vorherige Auswahl vorhanden.")
                st.stop()
            selection = st.session_state.last_selection
        else:
            selection = [int(x) for x in foil_input.split()]
            if any(n not in FOILS for n in selection):
                st.error("Ungültige Foil-Nummer.")
                st.stop()

        # Reset
        for f in FOIL_NAMES:
            df.at[idx, f] = pd.NA

        # Setzen
        if selection[0] != 0:
            for i, num in enumerate(selection):
                if num != 0:
                    df.at[idx, FOILS[num]] = i + 1

        df.to_csv(FILE, index=False)
        st.session_state.last_selection = selection
        st.rerun()

# -------- Letzte 4 (Kontext) --------
with right:
    st.subheader("Letzte 4 – gleicher Kontext")
    st.caption("Level / Gewicht / Disziplin")

    last4 = get_last_4_context(df, row)

    if not last4:
        st.caption("Noch keine Einträge")
    else:
        for i, r in enumerate(last4, 1):
            foil = r["Foil"] if r["Foil"] else "nicht relevant"
            st.markdown(
                f"**{i}.** {r['Wind']} · {r['Wellen']} → **{foil}**"
            )
