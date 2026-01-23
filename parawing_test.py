# Testskript für Parawing Foil-Empfehlungen
# Nur Flow, direkte Größenberechnung

import pandas as pd
import itertools

# ============================================
# FLOW GRÖSSEN
# ============================================
FLOW_SIZES = [720, 900, 1080, 1260]
STANDARD_SIZE = 1080  # Basis für 70-90kg, Intermediate, Mittel, Kleine Wellen
STANDARD_INDEX = FLOW_SIZES.index(STANDARD_SIZE)  # Index 2

# ============================================
# PARAMETER
# ============================================
LEVELS = ["Discover", "Intermediate", "Expert"]
GEWICHT = ["<70", "70-90", ">90"]
WIND = ["Schwach", "Mittel", "Stark"]
WELLEN = ["Flachwasser", "Kleine Wellen", "Grosse Wellen"]

# ============================================
# OFFSET-LOGIK
# ============================================
def calculate_offset(level, gewicht, wind, wellen):
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

    # Wellen
    if wellen == "Grosse Wellen":
        offset -= 1
    # Flachwasser und Kleine Wellen = 0

    return offset

# ============================================
# EMPFEHLUNG
# ============================================
def recommend_flow(level, gewicht, wind, wellen):
    offset = calculate_offset(level, gewicht, wind, wellen)
    target_index = STANDARD_INDEX + offset

    # Grenzen einhalten
    target_index = max(0, min(target_index, len(FLOW_SIZES) - 1))

    return FLOW_SIZES[target_index], offset

# ============================================
# TEST ALLE KOMBINATIONEN
# ============================================
rows = []

for level, gewicht, wind, wellen in itertools.product(LEVELS, GEWICHT, WIND, WELLEN):
    size, offset = recommend_flow(level, gewicht, wind, wellen)

    rows.append({
        "Level": level,
        "Gewicht": gewicht,
        "Wind": wind,
        "Wellen": wellen,
        "Offset": offset,
        "Empfehlung": f"Flow {size}"
    })

# ============================================
# AUSGABE
# ============================================
df = pd.DataFrame(rows)

# Speichern als CSV
df.to_csv("parawing_test_results.csv", index=False)

# Ausgabe in Konsole
print("=" * 80)
print("PARAWING FLOW EMPFEHLUNGEN - TESTAUSGABE")
print("=" * 80)
print(f"\nBasis: Flow {STANDARD_SIZE} für 70-90kg, Intermediate, Mittel Wind, Kleine Wellen\n")

# Gruppiert nach Offset
for offset_val in sorted(df["Offset"].unique()):
    subset = df[df["Offset"] == offset_val]
    print(f"\n--- OFFSET {offset_val:+d} ---")
    print(subset.to_string(index=False))
    print()

print(f"\nGesamt: {len(df)} Kombinationen getestet")
print(f"Ergebnisse gespeichert in: parawing_test_results.csv")
print("=" * 80)
