# foilfinder_generate_matrix.py
# Generates full foil-size recommendation matrix (0/1/2/3)
# Python = single source of truth
# Downwind-Wave implemented as CATEGORY (Flow-pushing)

import itertools
import pandas as pd

# ------------------------------------------------------------
# INPUT SPACE (UI)
# ------------------------------------------------------------

DISCIPLINES = [
    "Downwind",
    "Wingfoil Freeride",
    "Wavesurfing",
    "Lightwindfoil",
    "Pumpfoil",
    "Parawing",
]

LEVELS = ["Discover", "Intermediate", "Expert"]
GEWICHT = ["<70", "70-90", ">90"]

KATEGORIE = [
    "Freeride",
    "Jumping",
    "Flatwater",
    "Race",
    "Downwind-Wave",
]

WIND = ["Schwach", "Mittel", "Stark"]
WELLEN = ["Flachwasser", "Kleine Wellen", "Grosse Wellen"]

# ------------------------------------------------------------
# FOIL SIZES (MATCH HEADER)
# ------------------------------------------------------------

FOIL_SIZES = {
    "Infinity Ace": [540, 690, 840, 990, 1140, 1390],
    "Stride Ace": [1360, 1740],
    "Stride": [2050],
    "Pacer": [950, 1250, 1550, 1850, 2200],
    "Flow": [720, 900, 1080, 1260],
}

REFERENCE_SIZE = {
    "Infinity Ace": 990,
    "Stride Ace": 1740,
    "Stride": 2050,
    "Pacer": 1550,
    "Flow": 900,
}

# ------------------------------------------------------------
# FOIL CHARACTER SCORES
# ------------------------------------------------------------

FOIL_SCORES = {
    "Pacer":        dict(Lift=80,  Glide=60,  Agil=90,  Ease=100, Speed=75, Pump=70),
    "Stride":       dict(Lift=100, Glide=80,  Agil=50,  Ease=90,  Speed=50, Pump=100),
    "Stride Ace":   dict(Lift=90,  Glide=85,  Agil=70,  Ease=80,  Speed=65, Pump=100),
    "Infinity Ace": dict(Lift=70,  Glide=70,  Agil=100, Ease=80,  Speed=90, Pump=80),
    "Flow":         dict(Lift=75,  Glide=90,  Agil=80,  Ease=70,  Speed=80, Pump=90),
}

# ------------------------------------------------------------
# DISCIPLINE WEIGHTS
# ------------------------------------------------------------

DISCIPLINE_WEIGHTS = {
    "Downwind": {"Glide":0.35,"Pump":0.30,"Agil":0.20,"Lift":0.10,"Speed":0.03,"Ease":0.02},
    "Wingfoil Freeride": {"Ease":0.25,"Speed":0.20,"Agil":0.20,"Glide":0.15,"Lift":0.15,"Pump":0.05},
    "Wavesurfing": {"Agil":0.35,"Pump":0.20,"Glide":0.20,"Lift":0.15,"Speed":0.07,"Ease":0.03},
    "Lightwindfoil": {"Lift":0.30,"Pump":0.25,"Glide":0.25,"Ease":0.10,"Agil":0.05,"Speed":0.05},
    "Pumpfoil": {"Pump":0.45,"Lift":0.20,"Agil":0.15,"Glide":0.10,"Ease":0.05,"Speed":0.05},
    "Parawing": {"Glide":0.30,"Pump":0.25,"Lift":0.15,"Agil":0.15,"Ease":0.10,"Speed":0.05},
}

# ------------------------------------------------------------
# HARD EXCLUSIONS
# ------------------------------------------------------------

def is_valid(level, category, foil):
    if level == "Discover" and foil in ["Flow", "Stride Ace"]:
        return False
    if category == "Race" and foil == "Pacer":
        return False
    return True

# ------------------------------------------------------------
# SIZE LOGIC
# ------------------------------------------------------------

WEIGHT_OFFSET = {"<70": -1, "70-90": 0, ">90": 1}
DISCIPLINE_OFFSET = {"Downwind":1,"Lightwindfoil":1,"Parawing":1,"Pumpfoil":1}
WIND_OFFSET = {"Schwach":1,"Mittel":0,"Stark":0}
WAVE_OFFSET = {"Flachwasser":0,"Kleine Wellen":0,"Grosse Wellen":-1}

def target_index(foil, weight, discipline, wind, wave):
    sizes = FOIL_SIZES[foil]
    idx = sizes.index(REFERENCE_SIZE[foil])
    idx += WEIGHT_OFFSET[weight]
    idx += DISCIPLINE_OFFSET.get(discipline, 0)
    idx += WIND_OFFSET[wind]
    idx += WAVE_OFFSET[wave]
    return max(0, min(idx, len(sizes)-1))

# ------------------------------------------------------------
# SCORE (with Downwind-Wave Flow bias)
# ------------------------------------------------------------

def foil_score(foil, discipline, category):
    base = sum(
        FOIL_SCORES[foil][k] * DISCIPLINE_WEIGHTS[discipline][k]
        for k in DISCIPLINE_WEIGHTS[discipline]
    )

    if (
        category == "Downwind-Wave"
        and foil == "Flow"
        and discipline in ["Wingfoil Freeride", "Parawing", "Pumpfoil"]
    ):
        base *= 1.12  # Flow push (soft)

    return base

# ------------------------------------------------------------
# GENERATE MATRIX
# ------------------------------------------------------------

rows = []

for combo in itertools.product(DISCIPLINES, LEVELS, GEWICHT, KATEGORIE, WIND, WELLEN):
    discipline, level, weight, category, wind, wave = combo

    row = {
        "Disziplin": discipline,
        "Level": level,
        "Gewicht": weight,
        "Kategorie": category,
        "Wind": wind,
        "Wellen": wave,
    }

    # initialise foil columns
    for foil, sizes in FOIL_SIZES.items():
        for s in sizes:
            row[f"{foil} {s}"] = 0

    candidates = []

    for foil in FOIL_SIZES:
        if not is_valid(level, category, foil):
            continue

        idx = target_index(foil, weight, discipline, wind, wave)
        size = FOIL_SIZES[foil][idx]
        score = foil_score(foil, discipline, category)

        candidates.append((foil, size, idx, score))

    candidates.sort(key=lambda x: x[3], reverse=True)
    if not candidates:
        rows.append(row)
        continue

    # Recommendation 1
    f1, s1, i1, _ = candidates[0]
    row[f"{f1} {s1}"] = 3

    # Recommendation 2 (different foil)
    for f, s, i, _ in candidates[1:]:
        if f != f1:
            row[f"{f} {s}"] = 2
            break

    # Recommendation 3 (same foil, neighbour size)
    sizes = FOIL_SIZES[f1]
    if category == "Downwind-Wave" and f1 == "Flow":
        neighbour_order = [i1-1, i1+1]  # prefer smaller
    else:
        neighbour_order = [i1-1, i1+1]

    for ni in neighbour_order:
        if 0 <= ni < len(sizes):
            row[f"{f1} {sizes[ni]}"] = 1
            break

    rows.append(row)

# ------------------------------------------------------------
# EXPORT
# ------------------------------------------------------------

df = pd.DataFrame(rows)
df.to_csv("progress_prefilled_with_discipline copy.csv", index=False)
print(f"Done. Generated {len(df)} rows.")
