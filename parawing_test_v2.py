# Testskript für Parawing Foil-Empfehlungen V2
# Flow + Stride Ace, mit Top 3 Rangierung

import pandas as pd
import itertools

# ============================================
# FOIL GRÖSSEN
# ============================================
FLOW_SIZES = [720, 900, 1080, 1260]
STRIDE_ACE_SIZES = [1360, 1740]

# Standard für Intermediate: Flow 1080
FLOW_STANDARD = 1080
FLOW_STANDARD_INDEX = FLOW_SIZES.index(FLOW_STANDARD)

# ============================================
# PARAMETER
# ============================================
LEVELS = ["Discover", "Intermediate", "Expert"]
GEWICHT = ["<70", "70-90", ">90"]
WIND = ["Schwach", "Mittel", "Stark"]
WELLEN = ["Flachwasser", "Kleine Wellen", "Grosse Wellen"]

# ============================================
# OFFSET-LOGIK (für Flow)
# ============================================
def calculate_flow_offset(level, gewicht, wind, wellen):
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

    return offset

# ============================================
# FLOW EMPFEHLUNG
# ============================================
def get_optimal_flow(level, gewicht, wind, wellen):
    offset = calculate_flow_offset(level, gewicht, wind, wellen)
    target_index = FLOW_STANDARD_INDEX + offset
    target_index = max(0, min(target_index, len(FLOW_SIZES) - 1))
    return FLOW_SIZES[target_index], offset

# ============================================
# STRIDE ACE CHECK (nur für Discover)
# ============================================
def should_recommend_stride_ace(level, gewicht, wind, wellen, flow_size):
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

# ============================================
# TOP 3 RANGIERUNG
# ============================================
def recommend_top3(level, gewicht, wind, wellen):
    flow_size, offset = get_optimal_flow(level, gewicht, wind, wellen)
    flow_index = FLOW_SIZES.index(flow_size)

    top3 = []

    # DISCOVER mit Stride Ace Präferenz
    if should_recommend_stride_ace(level, gewicht, wind, wellen, flow_size):

        # Schwere Rider (70-90 oder >90): Stride 1740 möglich
        if gewicht in ["70-90", ">90"]:
            top3.append(("Stride Ace", 1740, 1))
            top3.append(("Stride Ace", 1360, 2))
            top3.append(("Flow", flow_size, 3))

        # Leichte Rider (<70): Stride 1740 fällt weg
        else:
            top3.append(("Stride Ace", 1360, 1))
            top3.append(("Flow", flow_size, 2))
            # Flow Nachbargröße als Platz 3
            if flow_index > 0:
                top3.append(("Flow", FLOW_SIZES[flow_index - 1], 3))
            elif flow_index < len(FLOW_SIZES) - 1:
                top3.append(("Flow", FLOW_SIZES[flow_index + 1], 3))

    # DISCOVER ohne Stride (bei stärkerem Wind / größeren Wellen)
    elif level == "Discover":
        top3.append(("Flow", flow_size, 1))

        # Nachbargrößen
        if flow_index > 0:
            top3.append(("Flow", FLOW_SIZES[flow_index - 1], 2))
        if flow_index < len(FLOW_SIZES) - 1:
            rank = 3 if len(top3) == 2 else 2
            top3.append(("Flow", FLOW_SIZES[flow_index + 1], rank))

    # INTERMEDIATE / EXPERT (Flow only)
    else:
        top3.append(("Flow", flow_size, 1))

        # Nachbargrößen
        if flow_index > 0:
            top3.append(("Flow", FLOW_SIZES[flow_index - 1], 2))
        if flow_index < len(FLOW_SIZES) - 1:
            rank = 3 if len(top3) == 2 else 2
            top3.append(("Flow", FLOW_SIZES[flow_index + 1], rank))

    return top3

# ============================================
# TEST ALLE KOMBINATIONEN
# ============================================
rows = []

for level, gewicht, wind, wellen in itertools.product(LEVELS, GEWICHT, WIND, WELLEN):
    top3 = recommend_top3(level, gewicht, wind, wellen)

    row = {
        "Level": level,
        "Gewicht": gewicht,
        "Wind": wind,
        "Wellen": wellen,
    }

    for i, (foil, size, rank) in enumerate(top3):
        row[f"Platz_{rank}"] = f"{foil} {size}"

    rows.append(row)

# ============================================
# AUSGABE
# ============================================
df = pd.DataFrame(rows)

# Spalten sortieren
col_order = ["Level", "Gewicht", "Wind", "Wellen", "Platz_1", "Platz_2", "Platz_3"]
df = df[col_order]

# Speichern
df.to_csv("parawing_test_results_v2.csv", index=False)

# Konsolen-Ausgabe
print("=" * 100)
print("PARAWING TOP 3 EMPFEHLUNGEN - TESTAUSGABE V2")
print("=" * 100)

# Discover Beispiele
print("\n--- DISCOVER BEISPIELE ---\n")
discover_examples = df[df["Level"] == "Discover"].head(10)
print(discover_examples.to_string(index=False))

# Intermediate Beispiele
print("\n--- INTERMEDIATE BEISPIELE ---\n")
intermediate_examples = df[df["Level"] == "Intermediate"].head(10)
print(intermediate_examples.to_string(index=False))

# Expert Beispiele
print("\n--- EXPERT BEISPIELE ---\n")
expert_examples = df[df["Level"] == "Expert"].head(10)
print(expert_examples.to_string(index=False))

# Stride Ace Empfehlungen zählen
stride_count = df[df["Platz_1"].str.contains("Stride", na=False)].shape[0]
print(f"\n\nStride Ace auf Platz 1: {stride_count} von {len(df)} Kombinationen")
print(f"Gesamt: {len(df)} Kombinationen getestet")
print(f"Ergebnisse gespeichert in: parawing_test_results_v2.csv")
print("=" * 100)
