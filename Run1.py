print("hello you")
import pandas as pd
import matplotlib.pyplot as plt

# Excel-Datei laden
pfad = r"C:\Users\micha\Documents\Python\Datenfile\Daten_Simulationen.xlsx"
df = pd.read_excel(pfad)

# Zeitspalte in Timedelta umwandeln
df['Zeit'] = pd.to_timedelta(df['Zeit'], unit='h')
df.set_index('Zeit', inplace=True)

# Resample auf 1 Stunde und Mittelwert berechnen
stundenmittel = df.resample('1h').mean()

# Ausgabe anzeigen
print(stundenmittel.head())

# Optional: Als neue Excel-Datei speichern
#stundenmittel.to_excel("C:/Users/micha/Documents/Python/Ergebnis_Stundenmittel.xlsx")


# ---------- BLOCKMITTEL ----------
blockmittel = df.resample('1h').mean()

# ---------- GLEITENDER MITTELWERT ----------
gleitmittel = df.rolling(window=6).mean()

# ---------- VERGLEICH GRAFISCH ----------
plt.figure(figsize=(12, 6))

# Beispiel: Temperatur T-ABL vergleichen
plt.plot(df.index.total_seconds()/3600, df['T-ABL'], label='Original', alpha=0.4)
plt.plot(blockmittel.index.total_seconds()/3600, blockmittel['T-ABL'], label='Blockmittel (1h)', marker='o')
plt.plot(gleitmittel.index.total_seconds()/3600, gleitmittel['T-ABL'], label='Gleitend (6 Werte)')

plt.xlabel("Zeit [h]")
plt.ylabel("T-ABL [°C]")
plt.legend()
plt.title("Vergleich: Original vs. Blockmittel vs. Gleitmittel")
plt.grid()
plt.tight_layout()
plt.show()