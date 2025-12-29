# foil_input.py

import pandas as pd
import os
from foils import FOILS

# -----------------------------
# Parameter
# -----------------------------
LEVELS = ["Discovers", "Discovers to Intermediate", "Intermediate to Experts"]
GEWICHTE = ["bis 70 kg", "70–90 kg", "grösser 90 kg"]
DISZIPLINEN = ["Freeride", "Downwind-Wave", "Wavesurfing", "Jumping",
               "Lightwindfoil", "Flatwater", "Race"]
WINDE = ["Schwachwind", "Medium Wind", "Starkwind", "nicht notwendig"]
WELLEN = ["Flachwasser", "Kleine Wellen", "Grosse Wellen", "nicht notwendig"]

FILE = "progress.csv"

FOIL_NAMES = list(FOILS.values())

# -----------------------------
# Alle Kombinationen erzeugen
# -----------------------------
all_rows = [
    (l, g, d, w, wa)
    for l in LEVELS
    for g in GEWICHTE
    for d in DISZIPLINEN
    for w in WINDE
    for wa in WELLEN
]

columns = ["Level", "Gewicht", "Disziplin", "Wind", "Wellen"] + FOIL_NAMES

# -----------------------------
# CSV laden oder erzeugen
# -----------------------------
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(all_rows, columns=columns[:5])
    for f in FOIL_NAMES:
        df[f] = ""
    df.to_csv(FILE, index=False)

# -----------------------------
# Hilfsfunktionen
# -----------------------------
def row_done(row):
    return (row[FOIL_NAMES] == "1").any()

def similar_rows(df, row):
    return df[
        (df.Level == row.Level) &
        (df.Gewicht == row.Gewicht) &
        (df.Disziplin == row.Disziplin)
    ]

def most_common_top1(similar):
    tops = []
    for _, r in similar.iterrows():
        for f in FOIL_NAMES:
            if r[f] == "1":
                tops.append(f)
    if tops:
        return max(set(tops), key=tops.count)
    return None

# -----------------------------
# Haupt-Loop
# -----------------------------
last_selection = None

for idx, row in df.iterrows():
    if not row_done(row):

        print("\n" + "-" * 50)
        print(f"Situation {idx + 1} / {len(df)}")
        print(f"Level     : {row.Level}")
        print(f"Gewicht   : {row.Gewicht}")
        print(f"Disziplin : {row.Disziplin}")
        print(f"Wind      : {row.Wind}")
        print(f"Wellen    : {row.Wellen}")

        print("\nFoils:")
        for k, v in FOILS.items():
            print(f"{k:>2}: {v}")

        inp = input(
            "\nFoils eingeben (z.B. 14 13 9 | Enter = gleich wie vorher): "
        ).strip()

        if inp == "":
            if last_selection is None:
                print("❌ Noch keine vorherige Auswahl vorhanden.")
                continue
            selection = last_selection
        else:
            try:
                selection = [int(x) for x in inp.split()]
            except ValueError:
                print("❌ Ungültige Eingabe.")
                continue

        top1_foil = FOILS[selection[0]]

        # Konsistenz-Warnung
        expected = most_common_top1(similar_rows(df, row))
        if expected and expected != top1_foil:
            print("\n⚠️ Konsistenz-Hinweis:")
            print(f"   Häufige Top-1 bisher: {expected}")
            print(f"   Deine Wahl          : {top1_foil}")
            confirm = input("   Enter = ok | x = ändern: ").strip()
            if confirm.lower() == "x":
                continue

        # Werte setzen
        for f in FOIL_NAMES:
            df.at[idx, f] = ""

        for i, num in enumerate(selection):
            df.at[idx, FOILS[num]] = str(i + 1)

        df.to_csv(FILE, index=False)
        last_selection = selection

        done = sum(df.apply(row_done, axis=1))
        print(f"✔ gespeichert ({done} / {len(df)})")

        break

else:
    print("\n🎉 Alle 1008 Situationen sind bewertet!")
