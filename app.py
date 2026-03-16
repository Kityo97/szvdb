"""
Politikai Hőtérkép Dashboard – Századvég Alapítvány
Streamlit alkalmazás – 2022 választási adatok + Bács-Kiskun kutatási adatok
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# OLDAL KONFIGURÁCIÓ
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Politikai Hőtérkép",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBÁLIS STÍLUS (SZV színvilág)
# ─────────────────────────────────────────────
SZV_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Source+Sans+3:wght@300;400;600;700&display=swap');

/* ─── Alapok ─── */
html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
    background-color: #f4f5f7;
    color: #0E2841;
}

/* ─── Sidebar ─── */
[data-testid="stSidebar"] {
    background: #0E2841 !important;
    border-right: 3px solid #E97132;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: #E8E8E8 !important; }
[data-testid="stSidebar"] .stRadio label { color: #E8E8E8 !important; }
[data-testid="stSidebar"] select { background: #156082 !important; color: white !important; }

/* ─── KPI kártyák ─── */
.kpi-card {
    background: #0E2841;
    border-radius: 10px;
    padding: 20px 16px 16px;
    border-left: 4px solid #E97132;
    margin-bottom: 8px;
    box-shadow: 0 4px 15px rgba(14,40,65,0.15);
    min-height: 120px;
}
.kpi-card .kpi-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #0F9ED5 !important;
    margin-bottom: 6px;
}
.kpi-card .kpi-value {
    font-family: 'Libre Baskerville', serif;
    font-size: 28px;
    font-weight: 700;
    color: #FFFFFF !important;
    line-height: 1.1;
}
.kpi-card .kpi-sub {
    font-size: 13px;
    color: #E97132 !important;
    margin-top: 5px;
    font-weight: 600;
}
.kpi-card .kpi-note {
    font-size: 10px;
    color: #8aaac0 !important;
    margin-top: 2px;
}

/* ─── Nav kártyák ─── */
.nav-card {
    background: white;
    border-radius: 10px;
    padding: 20px;
    border-top: 4px solid #156082;
    box-shadow: 0 2px 10px rgba(14,40,65,0.08);
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 10px;
    min-height: 110px;
}
.nav-card:hover { border-top-color: #E97132; box-shadow: 0 6px 20px rgba(14,40,65,0.15); }
.nav-card .nav-icon { font-size: 24px; margin-bottom: 8px; }
.nav-card .nav-title { font-size: 14px; font-weight: 700; color: #0E2841; }
.nav-card .nav-desc { font-size: 11px; color: #6b7c93; margin-top: 4px; }

/* ─── Szekció fejléc ─── */
.section-header {
    background: linear-gradient(135deg, #0E2841 0%, #156082 100%);
    border-radius: 8px;
    padding: 18px 22px;
    margin-bottom: 20px;
    margin-top: 10px;
}
.section-header h2 {
    font-family: 'Libre Baskerville', serif;
    color: #FFFFFF !important;
    margin: 0;
    font-size: 22px;
}
.section-header p {
    color: #0F9ED5 !important;
    margin: 4px 0 0;
    font-size: 13px;
}

/* ─── Oldal cím ─── */
.page-title {
    font-family: 'Libre Baskerville', serif;
    font-size: 28px;
    color: #0E2841;
    font-weight: 700;
    border-bottom: 3px solid #E97132;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

/* ─── Fidesz badge ─── */
.badge-fidesz  { background:#E97132; color:white; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700; }
.badge-tisza   { background:#156082; color:white; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700; }
.badge-mihazank{ background:#196B24; color:white; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700; }
.badge-mkkp    { background:#A02B93; color:white; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700; }
.badge-egyeb   { background:#8aaac0; color:white; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700; }

/* ─── Info box ─── */
.info-box {
    background: #EBF4FB;
    border-left: 4px solid #0F9ED5;
    border-radius: 6px;
    padding: 12px 16px;
    font-size: 13px;
    color: #0E2841;
    margin-bottom: 16px;
}

/* ─── Plotly charts bg ─── */
.js-plotly-plot { border-radius: 8px; }

/* ─── Stacked bar legend ─── */
.result-bar-wrap {
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(14,40,65,0.08);
    margin-bottom: 12px;
}
.result-bar-wrap .oevk-name {
    font-size: 12px;
    font-weight: 700;
    color: #0E2841;
    margin-bottom: 6px;
}

/* ─── Scrollable table ─── */
.stDataFrame { border-radius: 8px; }

/* Streamlit tweaks */
.stButton>button {
    background: #156082; color: white; border: none;
    border-radius: 6px; font-weight: 600;
}
.stButton>button:hover { background: #E97132; }
h1,h2,h3 { font-family: 'Libre Baskerville', serif; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
</style>
"""
st.markdown(SZV_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KONSTANSOK ÉS SZÍNEK
# ─────────────────────────────────────────────
COLORS = {
    "Fidesz-KDNP":     "#E97132",
    "Ellenzék/TISZA":  "#156082",
    "TISZA":           "#0F9ED5",
    "Mi Hazánk":       "#196B24",
    "MKKP":            "#A02B93",
    "DK":              "#2F7EC7",
    "Egyéb":           "#8aaac0",
    "Nem szavaz":      "#cccccc",
    "Bizonytalan":     "#888888",
}

PLOTLY_LAYOUT = dict(
    font_family="Source Sans 3",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=40, b=10),
)

# ─────────────────────────────────────────────
# ADATOK
# ─────────────────────────────────────────────

# 2022 Bács-Kiskun egyéni OEVK eredmények
BACS_OEVK = pd.DataFrame([
    {"oevk": "BK/1 – Kecskemét I.",      "szkhely": "Kecskemét",       "valasztopolgár": 69101, "megjelentek": 47068, "ervenytelen": 566, "érvényes": 46462,
     "Fidesz-KDNP": 27420, "Ellenzék/TISZA": 13464, "Mi Hazánk": 3425, "MKKP": 1691, "Egyéb": 462,  "nyertes": "Dr. Salacz László",       "nyertes_part": "Fidesz-KDNP"},
    {"oevk": "BK/2 – Kecskemét II.",     "szkhely": "Kecskemét",       "valasztopolgár": 71933, "megjelentek": 50963, "ervenytelen": 723, "érvényes": 50197,
     "Fidesz-KDNP": 26606, "Ellenzék/TISZA": 17208, "Mi Hazánk": 3512, "MKKP": 2274, "Egyéb": 597,  "nyertes": "Dr. Szeberényi Gy. T.", "nyertes_part": "Fidesz-KDNP"},
    {"oevk": "BK/3 – Kalocsa",           "szkhely": "Kalocsa",         "valasztopolgár": 65242, "megjelentek": 45135, "ervenytelen": 550, "érvényes": 44540,
     "Fidesz-KDNP": 26592, "Ellenzék/TISZA": 13464, "Mi Hazánk": 2778, "MKKP": 0,    "Egyéb": 1706, "nyertes": "Font Sándor",            "nyertes_part": "Fidesz-KDNP"},
    {"oevk": "BK/4 – Kiskunfélegyháza",  "szkhely": "Kiskunfélegyháza","valasztopolgár": 71615, "megjelentek": 48039, "ervenytelen": 625, "érvényes": 47382,
     "Fidesz-KDNP": 29835, "Ellenzék/TISZA": 11727, "Mi Hazánk": 3427, "MKKP": 1529, "Egyéb": 864,  "nyertes": "Lezsák Sándor",           "nyertes_part": "Fidesz-KDNP"},
    {"oevk": "BK/5 – Kiskunhalas",       "szkhely": "Kiskunhalas",     "valasztopolgár": 68267, "megjelentek": 43458, "ervenytelen": 586, "érvényes": 42827,
     "Fidesz-KDNP": 25763, "Ellenzék/TISZA": 12218, "Mi Hazánk": 4205, "MKKP": 0,    "Egyéb": 641,  "nyertes": "Bányai Gábor",            "nyertes_part": "Fidesz-KDNP"},
    {"oevk": "BK/6 – Baja",             "szkhely": "Baja",            "valasztopolgár": 64619, "megjelentek": 42458, "ervenytelen": 529, "érvényes": 41871,
     "Fidesz-KDNP": 23976, "Ellenzék/TISZA": 13697, "Mi Hazánk": 3017, "MKKP": 827,  "Egyéb": 354,  "nyertes": "Zsigó Róbert",            "nyertes_part": "Fidesz-KDNP"},
])
BACS_OEVK["részvétel_pct"] = (BACS_OEVK["megjelentek"] / BACS_OEVK["valasztopolgár"] * 100).round(1)
BACS_OEVK["ervenytelen_pct"] = (BACS_OEVK["ervenytelen"] / BACS_OEVK["megjelentek"] * 100).round(1)
BACS_OEVK["fidesz_pct"]  = (BACS_OEVK["Fidesz-KDNP"]      / BACS_OEVK["érvényes"] * 100).round(1)
BACS_OEVK["ellenZek_pct"] = (BACS_OEVK["Ellenzék/TISZA"]   / BACS_OEVK["érvényes"] * 100).round(1)
BACS_OEVK["mihazank_pct"] = (BACS_OEVK["Mi Hazánk"]        / BACS_OEVK["érvényes"] * 100).round(1)
BACS_OEVK["kulonbseg"]    = BACS_OEVK["Fidesz-KDNP"] - BACS_OEVK["Ellenzék/TISZA"]

# Aggregált Bács-Kiskun
BACS_AGG = {
    "valasztopolgár": 410777,
    "megjelentek":    277121,
    "ervenytelen":    3579,
    "érvényes":       273542,
    "részvétel_pct":  67.5,
    "ervenytelen_pct": 1.3,
    "Fidesz-KDNP":    160192,
    "Ellenzék/TISZA": 81778,
    "Mi Hazánk":      20364,
    "MKKP":           6321,
    "Egyéb":          4618,
}

# Listás 2022 – Országos
LISTAS_ORSZAGOS = {
    "valasztopolgár": 8215304,
    "megjelentek":    5717182,
    "ervenytelen":    57065,
    "érvényes":       5654860,
    "részvétel_pct":  69.6,
    "ervenytelen_pct": 1.0,
}
LISTAS_PÁRTOK = pd.DataFrame([
    {"párt": "Fidesz-KDNP",    "szavazat": 3060706, "mandatum": 48, "szín": "#E97132"},
    {"párt": "Ellenzék összefogás", "szavazat": 1947331, "mandatum": 38, "szín": "#156082"},
    {"párt": "Mi Hazánk",      "szavazat": 332487,  "mandatum": 6,  "szín": "#196B24"},
    {"párt": "MKKP",           "szavazat": 80844,   "mandatum": 0,  "szín": "#A02B93"},
    {"párt": "Egyéb",          "szavazat": 233492,  "mandatum": 0,  "szín": "#8aaac0"},
])
LISTAS_PÁRTOK["pct"] = (LISTAS_PÁRTOK["szavazat"] / LISTAS_PÁRTOK["szavazat"].sum() * 100).round(1)

# KSH Bács02 vs Ország
KSH_DEMOGR = {
    "nepesseg": {"Bács02": 91100, "Ország": 9603634},
    "18plus":   {"Bács02": 73848, "Ország": 7918836},
    "ferfi":    {"Bács02": 44057, "Ország": 4620846},
    "no":       {"Bács02": 47043, "Ország": 4982788},
}
KSH_KORCSOPORT = pd.DataFrame([
    {"korcsoport": "0–14",   "Bács02": 14280, "Ország": 1393232},
    {"korcsoport": "15–17",  "Bács02": 2972,  "Ország": 291566},
    {"korcsoport": "18–24",  "Bács02": 6677,  "Ország": 703667},
    {"korcsoport": "25–39",  "Bács02": 16750, "Ország": 1805868},
    {"korcsoport": "40–59",  "Bács02": 27373, "Ország": 2864605},
    {"korcsoport": "60–64",  "Bács02": 5345,  "Ország": 565253},
    {"korcsoport": "65–79",  "Bács02": 13950, "Ország": 1545252},
    {"korcsoport": "80+",    "Bács02": 3753,  "Ország": 434191},
])
for col in ["Bács02", "Ország"]:
    KSH_KORCSOPORT[f"{col}_pct"] = (KSH_KORCSOPORT[col] / KSH_KORCSOPORT[col].sum() * 100).round(1)

KSH_VEGZETTSEG = pd.DataFrame([
    {"végzettség": "8 oszt. alatt",          "Bács02": 1483,  "Ország": 171559},
    {"végzettség": "8 általános",            "Bács02": 12656, "Ország": 1467235},
    {"végzettség": "Szakképesítés (érettségi nélkül)", "Bács02": 16225, "Ország": 1730141},
    {"végzettség": "Érettségi",              "Bács02": 25057, "Ország": 2716185},
    {"végzettség": "Diploma",                "Bács02": 18427, "Ország": 1833716},
])
for col in ["Bács02", "Ország"]:
    KSH_VEGZETTSEG[f"{col}_pct"] = (KSH_VEGZETTSEG[col] / KSH_VEGZETTSEG[col].sum() * 100).round(1)

KSH_AKTIVITAS = pd.DataFrame([
    {"aktivitás": "Foglalkoztatott",  "Bács02": 46176, "Ország": 4707851},
    {"aktivitás": "Munkanélküli",     "Bács02": 1856,  "Ország": 234986},
    {"aktivitás": "Inaktív ellátott", "Bács02": 19035, "Ország": 2257357},
    {"aktivitás": "Eltartott",        "Bács02": 6781,  "Ország": 718642},
])
for col in ["Bács02", "Ország"]:
    KSH_AKTIVITAS[f"{col}_pct"] = (KSH_AKTIVITAS[col] / KSH_AKTIVITAS[col].sum() * 100).round(1)

KSH_VALLASS = pd.DataFrame([
    {"vallás": "Katolikus",            "Bács02": 24815, "Ország": 2481487},
    {"vallás": "Református",           "Bács02": 6107,  "Ország": 799881},
    {"vallás": "Evangélikus",          "Bács02": 709,   "Ország": 148965},
    {"vallás": "Más keresztény",       "Bács02": 981,   "Ország": 117714},
    {"vallás": "Más felekezet",        "Bács02": 225,   "Ország": 36699},
    {"vallás": "Nem vallásos",         "Bács02": 9417,  "Ország": 1172298},
    {"vallás": "Nem válaszolt",        "Bács02": 31543, "Ország": 3150983},
])
for col in ["Bács02", "Ország"]:
    KSH_VALLASS[f"{col}_pct"] = (KSH_VALLASS[col] / KSH_VALLASS[col].sum() * 100).round(1)

# Kutatási adatok – Bács02 (N=500) vs Ország (N=20014)
SURVEY_LIBKONZ = pd.DataFrame([
    {"skála": "1 – Liberális", "Bács02": 4.2,  "Ország": 10.4},
    {"skála": "2",             "Bács02": 5.1,  "Ország": 6.2},
    {"skála": "3",             "Bács02": 10.1, "Ország": 13.2},
    {"skála": "4 – Közép",     "Bács02": 36.3, "Ország": 29.3},
    {"skála": "5",             "Bács02": 14.9, "Ország": 11.6},
    {"skála": "6",             "Bács02": 6.9,  "Ország": 7.3},
    {"skála": "7 – Konzervatív","Bács02": 22.5, "Ország": 21.9},
])
SURVEY_BALJOBB = pd.DataFrame([
    {"skála": "1 – Baloldali", "Bács02": 9.1,  "Ország": 11.2},
    {"skála": "2",             "Bács02": 5.9,  "Ország": 3.3},
    {"skála": "3",             "Bács02": 6.4,  "Ország": 11.0},
    {"skála": "4 – Közép",     "Bács02": 34.3, "Ország": 30.7},
    {"skála": "5",             "Bács02": 12.9, "Ország": 9.4},
    {"skála": "6",             "Bács02": 7.8,  "Ország": 8.2},
    {"skála": "7 – Jobboldali","Bács02": 23.6, "Ország": 26.2},
])

# Pártpreferenciák (jelenlegi mérés)
PARTPREF_BACS = pd.DataFrame([
    {"párt": "TISZA",        "pct": 38.4, "szín": "#0F9ED5"},
    {"párt": "Fidesz-KDNP", "pct": 36.0, "szín": "#E97132"},
    {"párt": "Mi Hazánk",   "pct": 8.0,  "szín": "#196B24"},
    {"párt": "DK",          "pct": 2.2,  "szín": "#2F7EC7"},
    {"párt": "MKKP",        "pct": 0.7,  "szín": "#A02B93"},
    {"párt": "Bizonytalan", "pct": 6.9,  "szín": "#888888"},
    {"párt": "Nem menne el","pct": 0.8,  "szín": "#cccccc"},
    {"párt": "Nem mondja meg","pct": 6.5,"szín": "#aaaaaa"},
])
PARTPREF_ORSZAG = pd.DataFrame([
    {"párt": "TISZA",         "pct": 39.6, "szín": "#0F9ED5"},
    {"párt": "Fidesz-KDNP",  "pct": 36.2, "szín": "#E97132"},
    {"párt": "Mi Hazánk",    "pct": 6.0,  "szín": "#196B24"},
    {"párt": "DK",           "pct": 2.6,  "szín": "#2F7EC7"},
    {"párt": "MKKP",         "pct": 2.5,  "szín": "#A02B93"},
    {"párt": "Bizonytalan",  "pct": 5.8,  "szín": "#888888"},
    {"párt": "Nem menne el", "pct": 1.5,  "szín": "#cccccc"},
    {"párt": "Nem mondja meg","pct": 4.6, "szín": "#aaaaaa"},
])

# 2022-es visszamenőleges szavazat (survey)
SZAVAZAT_2022_BACS = pd.DataFrame([
    {"párt": "Fidesz-KDNP",     "pct": 43.5, "szín": "#E97132"},
    {"párt": "Ellenzéki összef.","pct": 28.5, "szín": "#156082"},
    {"párt": "Mi Hazánk",       "pct": 5.6,  "szín": "#196B24"},
    {"párt": "MKKP",            "pct": 3.6,  "szín": "#A02B93"},
    {"párt": "Egyéb",           "pct": 1.8,  "szín": "#8aaac0"},
    {"párt": "Nem szavazott",   "pct": 4.0,  "szín": "#dddddd"},
    {"párt": "Nem mondja meg",  "pct": 13.0, "szín": "#aaaaaa"},
])

# Gazdasági percepciók (Bács02, N=464)
GAZD_IRANY = pd.DataFrame([
    {"vélemény": "Határozottan rossz irányba", "pct": 38.6, "szín": "#c0392b"},
    {"vélemény": "Inkább rossz irányba",       "pct": 26.3, "szín": "#e74c3c"},
    {"vélemény": "Is-is",                      "pct": 12.5, "szín": "#8aaac0"},
    {"vélemény": "Inkább jó irányba",          "pct": 18.3, "szín": "#196B24"},
    {"vélemény": "Határozottan jó irányba",    "pct": 3.4,  "szín": "#1abc9c"},
    {"vélemény": "NT/NV",                      "pct": 0.9,  "szín": "#cccccc"},
])
GAZD_MULT = pd.DataFrame([
    {"változás": "Jelentősen romlott",   "pct": 43.5, "szín": "#c0392b"},
    {"változás": "Kismértékben romlott", "pct": 24.1, "szín": "#e74c3c"},
    {"változás": "Nem változott",        "pct": 18.1, "szín": "#8aaac0"},
    {"változás": "Kismértékben javult",  "pct": 9.7,  "szín": "#196B24"},
    {"változás": "Jelentősen javult",    "pct": 3.0,  "szín": "#1abc9c"},
    {"változás": "NT/NV",                "pct": 1.5,  "szín": "#cccccc"},
])
HAZTARTAS_ANYAG = pd.DataFrame([
    {"helyzet": "Gondok nélkül",         "pct": 7.3,  "szín": "#1abc9c"},
    {"helyzet": "Jól kijövünk",          "pct": 35.3, "szín": "#196B24"},
    {"helyzet": "Éppen kijövünk",        "pct": 43.8, "szín": "#8aaac0"},
    {"helyzet": "Anyagi gondok",         "pct": 11.4, "szín": "#e74c3c"},
    {"helyzet": "Nélkülözünk",           "pct": 1.9,  "szín": "#c0392b"},
    {"helyzet": "NT/NV",                 "pct": 0.2,  "szín": "#cccccc"},
])
INFLACIO_ERZEKELES = pd.DataFrame([
    {"válasz": "Egyáltalán nem",   "pct": 2.8,  "szín": "#1abc9c"},
    {"válasz": "Inkább nem",       "pct": 7.3,  "szín": "#196B24"},
    {"válasz": "Inkább igen",      "pct": 31.7, "szín": "#E97132"},
    {"válasz": "Teljesen igen",    "pct": 57.5, "szín": "#c0392b"},
    {"válasz": "NT/NV",            "pct": 0.6,  "szín": "#cccccc"},
])
MEGTAKARITAS = pd.DataFrame([
    {"válasz": "Van megtakarítása", "pct": 42.7, "szín": "#156082"},
    {"válasz": "Nincs",             "pct": 52.2, "szín": "#E97132"},
    {"válasz": "NT/NV",             "pct": 5.2,  "szín": "#cccccc"},
])

# ─────────────────────────────────────────────
# SEGÉDFÜGGVÉNYEK
# ─────────────────────────────────────────────

def fmt_num(n):
    """Szám formázás ezres elválasztóval"""
    if isinstance(n, float):
        return f"{n:,.0f}".replace(",", " ")
    return f"{int(n):,}".replace(",", " ")

def kpi_card(label, value, sub="", note=""):
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {"<div class='kpi-sub'>" + sub + "</div>" if sub else ""}
        {"<div class='kpi-note'>" + note + "</div>" if note else ""}
    </div>"""

def section_header(title, subtitle=""):
    return f"""
    <div class="section-header">
        <h2>{title}</h2>
        {"<p>" + subtitle + "</p>" if subtitle else ""}
    </div>"""

def info_box(text):
    return f'<div class="info-box">ℹ️ {text}</div>'

def diverging_bar(df, col_left, col_right, label_col, title, colors=("#E97132","#156082")):
    """Divergáló sávdiagram bal/jobb összehasonlításhoz"""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df[label_col], x=-df[col_left],
        orientation="h", name=col_left,
        marker_color=colors[0],
        text=[f"{v:.1f}%" for v in df[col_left]],
        textposition="inside", insidetextanchor="end",
    ))
    fig.add_trace(go.Bar(
        y=df[label_col], x=df[col_right],
        orientation="h", name=col_right,
        marker_color=colors[1],
        text=[f"{v:.1f}%" for v in df[col_right]],
        textposition="inside", insidetextanchor="start",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=title, font_size=14, x=0, font_color="#0E2841"),
        barmode="relative",
        xaxis=dict(showticklabels=False, zeroline=True, zerolinewidth=2, zerolinecolor="#0E2841"),
        yaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=300,
    )
    return fig

# ─────────────────────────────────────────────
# SIDEBAR – NAVIGÁCIÓ + SZŰRŐK
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🗺️ POLITIKAI HŐTÉRKÉP")
    st.markdown("---")

    # Területi szűrő
    st.markdown("**📍 Területi szűrő**")
    terulet_szint = st.selectbox(
        "Szint", ["Bács-Kiskun megye", "BK/1 – Kecskemét I.", "BK/2 – Kecskemét II.",
                  "BK/3 – Kalocsa", "BK/4 – Kiskunfélegyháza", "BK/5 – Kiskunhalas",
                  "BK/6 – Baja"],
        label_visibility="collapsed"
    )

    # Év szűrő
    st.markdown("**📅 Választás éve**")
    ev = st.selectbox("Év", ["2022"], label_visibility="collapsed")
    st.markdown("*További évek hamarosan*", help="2010, 2014, 2018 adatai folyamatban")

    st.markdown("---")

    # Oldalnavigáció
    st.markdown("**📑 Oldalak**")
    page = st.radio(
        "Oldal",
        [
            "🏠  Főoldal",
            "🗳️  Választástörténet",
            "👥  KSH Szociológia",
            "📊  Saját Kutatások",
            "🔭  Politikai Közvélemény",
            "📱  Social Media",
            "💰  Gazdasági Adatok",
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:10px;color:#8aaac0;'>Forrás: NVI 2022, KSH 2022,<br>Századvég nagykutatás (N=500 Bács02, N=20014 Ország)</div>",
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
# AKTÍV TERÜLETI ADAT
# ─────────────────────────────────────────────

def get_active_data():
    if terulet_szint == "Bács-Kiskun megye":
        row = BACS_AGG.copy()
        row["cim"] = "Bács-Kiskun megye"
        row["fidesz_pct"] = round(BACS_AGG["Fidesz-KDNP"] / BACS_AGG["érvényes"] * 100, 1)
        row["ellenzek_pct"] = round(BACS_AGG["Ellenzék/TISZA"] / BACS_AGG["érvényes"] * 100, 1)
        return row
    else:
        r = BACS_OEVK[BACS_OEVK["oevk"] == terulet_szint].iloc[0].to_dict()
        r["cim"] = terulet_szint
        return r

active = get_active_data()

# ─────────────────────────────────────────────
# FŐOLDAL
# ─────────────────────────────────────────────

def render_fooldal():
    st.markdown('<div class="page-title">🗺️ Politikai Hőtérkép – Főoldal</div>', unsafe_allow_html=True)
    st.markdown(f"Jelenleg megtekintett terület: **{active['cim']}** &nbsp;|&nbsp; Választás éve: **{ev}**", unsafe_allow_html=True)

    # KPI sor
    kols = st.columns(5)
    pop = KSH_DEMOGR["nepesseg"]["Bács02"] if "Kiskun" in terulet_szint or terulet_szint == "Bács-Kiskun megye" else "–"
    szavkep = KSH_DEMOGR["18plus"]["Bács02"] if "Kiskun" in terulet_szint or terulet_szint == "Bács-Kiskun megye" else "–"
    szavkep_pct = round(KSH_DEMOGR["18plus"]["Bács02"] / KSH_DEMOGR["nepesseg"]["Bács02"] * 100, 1) if isinstance(szavkep, int) else "–"

    val = active.get("valasztopolgár", 0)
    meg = active.get("megjelentek", 0)
    erv = active.get("ervenytelen", 0)
    res = active.get("részvétel_pct", 0)
    erv_pct = active.get("ervenytelen_pct", 0)

    kols[0].markdown(kpi_card("Össznépesség (KSH)", fmt_num(pop) if isinstance(pop, int) else "N/A", "Bács-Kiskun VK", "Forrás: KSH Népszámlálás 2022"), unsafe_allow_html=True)
    kols[1].markdown(kpi_card("Szavazóképes korú", fmt_num(szavkep) if isinstance(szavkep, int) else "N/A",
                               f"{szavkep_pct}% az össznépességből" if isinstance(szavkep_pct, float) else "", "18+ lakosság"), unsafe_allow_html=True)
    kols[2].markdown(kpi_card("Nyilvántartott választópolgár", fmt_num(val), f"Szűrt terület: {active['cim']}", "NVI 2022 választói névjegyzék"), unsafe_allow_html=True)
    kols[3].markdown(kpi_card("Tényleges szavazók", fmt_num(meg), f"{res}% részvétel", "A névjegyzékbe vettekhez képest"), unsafe_allow_html=True)
    kols[4].markdown(kpi_card("Érvénytelen szavazatok", fmt_num(erv), f"{erv_pct}% az urnából", "Leadott szavazatokhoz képest"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigációs kártyák
    st.markdown(section_header("Elemzési modulok", "Válasszon aloldalt a részletes elemzéshez – baloldali menüből is elérhető"), unsafe_allow_html=True)

    nav_data = [
        ("🗳️", "Választástörténet", "2022 eredmények OEVK-nként, jelölt adatok, arányok, rangsorok"),
        ("👥", "KSH Szociológia", "Demográfia, korcsoport, végzettség, vallás, gazd. aktivitás"),
        ("📊", "Saját Kutatások", "Ideológiai profil, Big Five, értékek, médiafogyasztás"),
        ("🔭", "Politikai Közvélemény", "Pártpreferenciák, szavazói átváltás, közhangulat"),
        ("📱", "Social Media", "Helyi aktivitás, témák, komment-klasszifikáció (hamarosan)"),
        ("💰", "Gazdasági Adatok", "Percepciók, megélhetés, megtakarítás, inflációérzékelés"),
    ]
    cols_nav = st.columns(3)
    for i, (icon, title, desc) in enumerate(nav_data):
        cols_nav[i % 3].markdown(
            f'<div class="nav-card"><div class="nav-icon">{icon}</div><div class="nav-title">{title}</div><div class="nav-desc">{desc}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 2022 eredmény összefoglaló
    st.markdown(section_header("2022 választási eredmény – összefoglaló", f"{active['cim']} – egyéni választókerületi eredmények"), unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])

    with col_l:
        # OEVK-nkénti stacked bar
        melt_df = BACS_OEVK.melt(
            id_vars=["oevk"], value_vars=["Fidesz-KDNP", "Ellenzék/TISZA", "Mi Hazánk", "MKKP", "Egyéb"],
            var_name="párt", value_name="szavazat"
        )
        melt_df["pct"] = melt_df.apply(
            lambda row: row["szavazat"] / BACS_OEVK.loc[BACS_OEVK["oevk"] == row["oevk"], "érvényes"].values[0] * 100, axis=1
        ).round(1)
        fig_stack = px.bar(
            melt_df, x="pct", y="oevk", color="párt", orientation="h",
            color_discrete_map={k: COLORS[k] for k in COLORS},
            text="pct",
            title="Szavazatarányok OEVK-nként (%)",
            labels={"pct": "Szavazatarány (%)", "oevk": ""},
        )
        fig_stack.update_traces(texttemplate="%{text:.0f}%", textposition="inside")
        fig_stack.update_layout(**PLOTLY_LAYOUT, barmode="stack", height=320,
                                 legend=dict(orientation="h", y=-0.25, font_size=11),
                                 xaxis=dict(range=[0, 101]))
        st.plotly_chart(fig_stack, use_container_width=True)

    with col_r:
        # Részvételi arányok
        fig_res = px.bar(
            BACS_OEVK, x="részvétel_pct", y="oevk", orientation="h",
            color="részvétel_pct",
            color_continuous_scale=["#E8E8E8", "#156082", "#0E2841"],
            title="Részvételi arány OEVK-nként (%)",
            labels={"részvétel_pct": "Részvétel (%)", "oevk": ""},
            text="részvétel_pct",
        )
        fig_res.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_res.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=320,
                               coloraxis_showscale=False,
                               xaxis=dict(range=[0, 80]))
        st.plotly_chart(fig_res, use_container_width=True)

    # Nyertes jelöltek táblázat
    st.markdown("**Nyertes jelöltek 2022 – Bács-Kiskun**")
    nyertes_df = BACS_OEVK[["oevk", "nyertes", "fidesz_pct", "ellenZek_pct", "mihazank_pct", "részvétel_pct", "kulonbseg"]].copy()
    nyertes_df.columns = ["Választókerület", "Nyertes jelölt", "Fidesz %", "Ellenzék %", "Mi Hazánk %", "Részvétel %", "Különbség (fő)"]
    st.dataframe(nyertes_df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# VÁLASZTÁSTÖRTÉNET
# ─────────────────────────────────────────────

def render_valasztas():
    st.markdown('<div class="page-title">🗳️ Választástörténet</div>', unsafe_allow_html=True)
    st.markdown(info_box("Jelenleg a 2022-es országgyűlési választások adatai érhetők el. Korábbi évek (2010, 2014, 2018) adatai hamarosan hozzáadásra kerülnek."), unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 OEVK eredmények", "🇭🇺 Országos listás", "🏆 Jelölt-összehasonlítás"])

    with tab1:
        st.markdown(section_header("Bács-Kiskun – Egyéni OEVK eredmények 2022", "6 választókerület részletes adatai"), unsafe_allow_html=True)

        sel_oevk = st.selectbox("Válasszon OEVK-t a részletekhez:", BACS_OEVK["oevk"].tolist(), key="oevk_sel")
        row = BACS_OEVK[BACS_OEVK["oevk"] == sel_oevk].iloc[0]

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(kpi_card("Választópolgár", fmt_num(row["valasztopolgár"]), "Névjegyzékben"), unsafe_allow_html=True)
        c2.markdown(kpi_card("Megjelentek", fmt_num(row["megjelentek"]), f"{row['részvétel_pct']}% részvétel"), unsafe_allow_html=True)
        c3.markdown(kpi_card("Érvényes szavazat", fmt_num(row["érvényes"]), "Feldolgozott szavazatok"), unsafe_allow_html=True)
        c4.markdown(kpi_card("Érvénytelen", fmt_num(row["ervenytelen"]), f"{row['ervenytelen_pct']}% arány"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns([2, 1])
        with col_a:
            jeloltek = pd.DataFrame([
                {"jelölt": row["nyertes"],              "párt": "Fidesz-KDNP",     "szavazat": row["Fidesz-KDNP"],     "szín": "#E97132", "nyertes": True},
                {"jelölt": "Ellenzéki összefogás jel.", "párt": "Ellenzék/TISZA",  "szavazat": row["Ellenzék/TISZA"],  "szín": "#156082", "nyertes": False},
                {"jelölt": "Mi Hazánk jelölt",          "párt": "Mi Hazánk",       "szavazat": row["Mi Hazánk"],       "szín": "#196B24", "nyertes": False},
                {"jelölt": "MKKP jelölt",               "párt": "MKKP",            "szavazat": row["MKKP"],            "szín": "#A02B93", "nyertes": False},
                {"jelölt": "Egyéb",                     "párt": "Egyéb",           "szavazat": row["Egyéb"],           "szín": "#8aaac0", "nyertes": False},
            ])
            jeloltek["pct"] = (jeloltek["szavazat"] / row["érvényes"] * 100).round(1)
            jeloltek = jeloltek[jeloltek["szavazat"] > 0].sort_values("szavazat", ascending=False)

            fig_jel = px.bar(
                jeloltek, x="párt", y="pct", color="párt",
                color_discrete_map={r["párt"]: r["szín"] for _, r in jeloltek.iterrows()},
                title=f"{sel_oevk} – Eredmény (%)",
                text="pct",
            )
            fig_jel.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_jel.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=300,
                                   yaxis=dict(title="Szavazatarány (%)"))
            st.plotly_chart(fig_jel, use_container_width=True)

        with col_b:
            st.markdown("**Szavazatszámok**")
            disp = jeloltek[["párt", "szavazat", "pct"]].copy()
            disp.columns = ["Párt", "Szavazat (fő)", "%"]
            st.dataframe(disp, use_container_width=True, hide_index=True)
            st.markdown(f"""
            <br><div class='info-box'>
            🏆 <strong>Nyertes:</strong> {row['nyertes']}<br>
            <span class='badge-fidesz'>Fidesz-KDNP</span><br>
            Különbség: <strong>{fmt_num(row['kulonbseg'])} szavazat</strong>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Összes OEVK összehasonlítása**")
        fig_all = px.scatter(
            BACS_OEVK, x="fidesz_pct", y="részvétel_pct",
            size="valasztopolgár", color="ellenZek_pct",
            color_continuous_scale=["#E97132", "#E8E8E8", "#156082"],
            hover_name="oevk",
            hover_data={"fidesz_pct": ":.1f", "ellenZek_pct": ":.1f", "részvétel_pct": ":.1f", "valasztopolgár": ":,"},
            title="Fidesz % vs Részvétel % – buborék mérete: választópolgárok száma",
            labels={"fidesz_pct": "Fidesz-KDNP %", "részvétel_pct": "Részvétel %", "ellenZek_pct": "Ellenzék %"},
        )
        fig_all.update_layout(**PLOTLY_LAYOUT, height=380)
        st.plotly_chart(fig_all, use_container_width=True)

    with tab2:
        st.markdown(section_header("Országos listás eredmények 2022", "Országgyűlési választás – pártlistás szavazatok"), unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(kpi_card("Választópolgár (orsz.)", fmt_num(LISTAS_ORSZAGOS["valasztopolgár"]), "Teljes Magyarország"), unsafe_allow_html=True)
        c2.markdown(kpi_card("Megjelentek", fmt_num(LISTAS_ORSZAGOS["megjelentek"]), f"{LISTAS_ORSZAGOS['részvétel_pct']}% részvétel"), unsafe_allow_html=True)
        c3.markdown(kpi_card("Érvényes listás", fmt_num(LISTAS_ORSZAGOS["érvényes"]), "Feldolgozott szavazat"), unsafe_allow_html=True)
        c4.markdown(kpi_card("Érvénytelen", fmt_num(LISTAS_ORSZAGOS["ervenytelen"]), f"{LISTAS_ORSZAGOS['ervenytelen_pct']}% arány"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        cl, cr = st.columns(2)
        with cl:
            fig_lst = px.bar(
                LISTAS_PÁRTOK.sort_values("szavazat", ascending=False),
                x="párt", y="pct", color="párt",
                color_discrete_map={r["párt"]: r["szín"] for _, r in LISTAS_PÁRTOK.iterrows()},
                title="Listás szavazatarányok 2022 (%)",
                text="pct",
            )
            fig_lst.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_lst.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=350)
            st.plotly_chart(fig_lst, use_container_width=True)

        with cr:
            fig_mand = px.pie(
                LISTAS_PÁRTOK[LISTAS_PÁRTOK["mandatum"] > 0],
                values="mandatum", names="párt",
                color="párt",
                color_discrete_map={r["párt"]: r["szín"] for _, r in LISTAS_PÁRTOK.iterrows()},
                title="Mandátumok megoszlása (92 listás)",
                hole=0.4,
            )
            fig_mand.update_layout(**PLOTLY_LAYOUT, height=350)
            st.plotly_chart(fig_mand, use_container_width=True)

    with tab3:
        st.markdown(section_header("Jelölt-összehasonlítás", "Bács-Kiskun OEVK-k egymás mellett"), unsafe_allow_html=True)
        comp_df = BACS_OEVK[["oevk", "nyertes", "fidesz_pct", "ellenZek_pct", "mihazank_pct", "részvétel_pct", "kulonbseg", "valasztopolgár"]].copy()
        comp_df["Fidesz fölény"] = comp_df["fidesz_pct"] - comp_df["ellenZek_pct"]
        comp_df = comp_df.rename(columns={
            "oevk": "OEVK", "nyertes": "Nyertes", "fidesz_pct": "Fidesz %",
            "ellenZek_pct": "Ellenzék %", "mihazank_pct": "Mi Hazánk %",
            "részvétel_pct": "Részvétel %", "kulonbseg": "Különbség (fő)", "valasztopolgár": "Választópolgár"
        })
        st.dataframe(
            comp_df.style.background_gradient(subset=["Fidesz %"], cmap="Oranges")
                         .background_gradient(subset=["Ellenzék %"], cmap="Blues")
                         .background_gradient(subset=["Részvétel %"], cmap="Greys"),
            use_container_width=True, hide_index=True
        )

        fig_rank = px.bar(
            BACS_OEVK.sort_values("fidesz_pct"),
            x="fidesz_pct", y="oevk", orientation="h",
            color="fidesz_pct",
            color_continuous_scale=["#f5cba7", "#E97132", "#a04000"],
            title="Fidesz-KDNP szavazatarány szerinti rangsor (Bács-Kiskun, 2022)",
            text="fidesz_pct",
        )
        fig_rank.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_rank.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=300,
                                coloraxis_showscale=False)
        st.plotly_chart(fig_rank, use_container_width=True)

# ─────────────────────────────────────────────
# KSH SZOCIOLÓGIA
# ─────────────────────────────────────────────

def render_ksh():
    st.markdown('<div class="page-title">👥 KSH Szociológia</div>', unsafe_allow_html=True)
    st.markdown(info_box("Bács02 választókerület KSH 2022 Népszámlálás adatai, összehasonlítva az országos értékekkel."), unsafe_allow_html=True)

    # Fejléc KPI-ok
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi_card("Bács02 Népesség", fmt_num(91100), "KSH 2022 Népszámlálás"), unsafe_allow_html=True)
    c2.markdown(kpi_card("18+ korú lakos", fmt_num(73848), f"{round(73848/91100*100,1)}% az össznépességből"), unsafe_allow_html=True)
    c3.markdown(kpi_card("Nők aránya", "51,6%", f"{fmt_num(47043)} fő"), unsafe_allow_html=True)
    c4.markdown(kpi_card("Roma nemzetiség", f"{round(582/91100*100,2)}%", f"{fmt_num(582)} fő"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["👶 Korcsoport", "🎓 Végzettség", "💼 Aktivitás", "⛪ Vallás"])

    with tab1:
        col_l, col_r = st.columns(2)
        with col_l:
            fig_kor_b = px.pie(
                KSH_KORCSOPORT, values="Bács02", names="korcsoport",
                title="Korcsoport megoszlás – Bács02",
                color_discrete_sequence=["#0E2841","#156082","#0F9ED5","#E97132","#E8E8E8","#196B24","#A02B93","#8aaac0"],
                hole=0.35,
            )
            fig_kor_b.update_layout(**PLOTLY_LAYOUT, height=320)
            st.plotly_chart(fig_kor_b, use_container_width=True)
        with col_r:
            fig_kor_o = px.pie(
                KSH_KORCSOPORT, values="Ország", names="korcsoport",
                title="Korcsoport megoszlás – Magyarország",
                color_discrete_sequence=["#0E2841","#156082","#0F9ED5","#E97132","#E8E8E8","#196B24","#A02B93","#8aaac0"],
                hole=0.35,
            )
            fig_kor_o.update_layout(**PLOTLY_LAYOUT, height=320)
            st.plotly_chart(fig_kor_o, use_container_width=True)

        fig_kor_comp = go.Figure()
        fig_kor_comp.add_trace(go.Bar(name="Bács02",  x=KSH_KORCSOPORT["korcsoport"], y=KSH_KORCSOPORT["Bács02_pct"], marker_color="#E97132"))
        fig_kor_comp.add_trace(go.Bar(name="Ország",  x=KSH_KORCSOPORT["korcsoport"], y=KSH_KORCSOPORT["Ország_pct"], marker_color="#156082"))
        fig_kor_comp.update_layout(**PLOTLY_LAYOUT, barmode="group", title="Korcsoport összehasonlítás (%)", height=280,
                                    yaxis_title="%", legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_kor_comp, use_container_width=True)

    with tab2:
        fig_veg = go.Figure()
        fig_veg.add_trace(go.Bar(name="Bács02", x=KSH_VEGZETTSEG["végzettség"], y=KSH_VEGZETTSEG["Bács02_pct"], marker_color="#E97132"))
        fig_veg.add_trace(go.Bar(name="Ország", x=KSH_VEGZETTSEG["végzettség"], y=KSH_VEGZETTSEG["Ország_pct"], marker_color="#156082"))
        fig_veg.update_layout(**PLOTLY_LAYOUT, barmode="group", title="Legmagasabb befejezett iskolai végzettség (%)", height=360,
                               yaxis_title="%", legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig_veg, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            dip_b = round(KSH_VEGZETTSEG.loc[KSH_VEGZETTSEG["végzettség"]=="Diploma","Bács02_pct"].values[0], 1)
            dip_o = round(KSH_VEGZETTSEG.loc[KSH_VEGZETTSEG["végzettség"]=="Diploma","Ország_pct"].values[0], 1)
            st.markdown(kpi_card("Felsőfokú végzettség – Bács02", f"{dip_b}%", f"Ország: {dip_o}%"), unsafe_allow_html=True)
        with c2:
            ert_b = round(KSH_VEGZETTSEG.loc[KSH_VEGZETTSEG["végzettség"]=="Érettségi","Bács02_pct"].values[0], 1)
            ert_o = round(KSH_VEGZETTSEG.loc[KSH_VEGZETTSEG["végzettség"]=="Érettségi","Ország_pct"].values[0], 1)
            st.markdown(kpi_card("Érettségizett – Bács02", f"{ert_b}%", f"Ország: {ert_o}%"), unsafe_allow_html=True)

    with tab3:
        cl, cr = st.columns(2)
        with cl:
            fig_ak_b = px.pie(
                KSH_AKTIVITAS, values="Bács02", names="aktivitás",
                title="Gazdasági aktivitás – Bács02",
                color_discrete_sequence=["#0F9ED5","#E97132","#196B24","#A02B93"],
                hole=0.35,
            )
            fig_ak_b.update_layout(**PLOTLY_LAYOUT, height=310)
            st.plotly_chart(fig_ak_b, use_container_width=True)
        with cr:
            fig_ak_o = px.pie(
                KSH_AKTIVITAS, values="Ország", names="aktivitás",
                title="Gazdasági aktivitás – Magyarország",
                color_discrete_sequence=["#0F9ED5","#E97132","#196B24","#A02B93"],
                hole=0.35,
            )
            fig_ak_o.update_layout(**PLOTLY_LAYOUT, height=310)
            st.plotly_chart(fig_ak_o, use_container_width=True)

        st.markdown(info_box(f"Foglalkoztatottság aránya Bács02: {round(46176/(46176+1856+19035+6781)*100,1)}% | Ország: {round(4707851/(4707851+234986+2257357+718642)*100,1)}%"), unsafe_allow_html=True)

    with tab4:
        val_viz = KSH_VALLASS[KSH_VALLASS["vallás"] != "Nem válaszolt"].copy()
        fig_val = go.Figure()
        fig_val.add_trace(go.Bar(name="Bács02", x=val_viz["vallás"], y=val_viz["Bács02_pct"], marker_color="#E97132"))
        fig_val.add_trace(go.Bar(name="Ország", x=val_viz["vallás"], y=val_viz["Ország_pct"], marker_color="#156082"))
        fig_val.update_layout(**PLOTLY_LAYOUT, barmode="group", title="Vallási megoszlás (nem válaszolók nélkül, %)", height=360,
                               yaxis_title="%", legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig_val, use_container_width=True)

# ─────────────────────────────────────────────
# SAJÁT KUTATÁSOK
# ─────────────────────────────────────────────

def render_sajat():
    st.markdown('<div class="page-title">📊 Saját Kutatások – Szociológiai Mérések</div>', unsafe_allow_html=True)
    st.markdown(info_box("Századvég nagykutatás – Bács02 (N=500) és Ország (N=20 014) összehasonlítása"), unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🧭 Ideológiai profil", "🧠 Big Five", "📺 Médiafogyasztás"])

    with tab1:
        st.markdown(section_header("Ideológiai önbesorolás", "7-fokú skálák – Bács02 vs. Ország"), unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            # Liberális-Konzervatív
            fig_lk = go.Figure()
            fig_lk.add_trace(go.Bar(name="Bács02", x=SURVEY_LIBKONZ["skála"], y=SURVEY_LIBKONZ["Bács02"],
                                     marker_color="#E97132", text=SURVEY_LIBKONZ["Bács02"], texttemplate="%{text:.1f}%", textposition="outside"))
            fig_lk.add_trace(go.Bar(name="Ország", x=SURVEY_LIBKONZ["skála"], y=SURVEY_LIBKONZ["Ország"],
                                     marker_color="#156082", text=SURVEY_LIBKONZ["Ország"], texttemplate="%{text:.1f}%", textposition="outside"))
            fig_lk.update_layout(**PLOTLY_LAYOUT, barmode="group", title="Liberális ↔ Konzervatív skála (%)",
                                   height=320, yaxis_title="%",
                                   legend=dict(orientation="h", y=1.08),
                                   xaxis=dict(tickfont_size=10))
            st.plotly_chart(fig_lk, use_container_width=True)

        with c2:
            # Bal-Jobb
            fig_bj = go.Figure()
            fig_bj.add_trace(go.Bar(name="Bács02", x=SURVEY_BALJOBB["skála"], y=SURVEY_BALJOBB["Bács02"],
                                     marker_color="#E97132", text=SURVEY_BALJOBB["Bács02"], texttemplate="%{text:.1f}%", textposition="outside"))
            fig_bj.add_trace(go.Bar(name="Ország", x=SURVEY_BALJOBB["skála"], y=SURVEY_BALJOBB["Ország"],
                                     marker_color="#156082", text=SURVEY_BALJOBB["Ország"], texttemplate="%{text:.1f}%", textposition="outside"))
            fig_bj.update_layout(**PLOTLY_LAYOUT, barmode="group", title="Baloldali ↔ Jobboldali skála (%)",
                                   height=320, yaxis_title="%",
                                   legend=dict(orientation="h", y=1.08),
                                   xaxis=dict(tickfont_size=10))
            st.plotly_chart(fig_bj, use_container_width=True)

        # Átlagok
        lk_avg_b = sum((i+1)*v/100 for i,v in enumerate(SURVEY_LIBKONZ["Bács02"]))
        lk_avg_o = sum((i+1)*v/100 for i,v in enumerate(SURVEY_LIBKONZ["Ország"]))
        bj_avg_b = sum((i+1)*v/100 for i,v in enumerate(SURVEY_BALJOBB["Bács02"]))
        bj_avg_o = sum((i+1)*v/100 for i,v in enumerate(SURVEY_BALJOBB["Ország"]))

        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(kpi_card("Lib-Konz átlag – Bács02", f"{lk_avg_b:.2f} / 7", "Magasabb = konzervatívabb"), unsafe_allow_html=True)
        m2.markdown(kpi_card("Lib-Konz átlag – Ország", f"{lk_avg_o:.2f} / 7", "Magasabb = konzervatívabb"), unsafe_allow_html=True)
        m3.markdown(kpi_card("Bal-Jobb átlag – Bács02", f"{bj_avg_b:.2f} / 7", "Magasabb = jobboldalibb"), unsafe_allow_html=True)
        m4.markdown(kpi_card("Bal-Jobb átlag – Ország", f"{bj_avg_o:.2f} / 7", "Magasabb = jobboldalibb"), unsafe_allow_html=True)

    with tab2:
        st.markdown(section_header("Big Five személyiségprofil", "BFI–10 skála – Bács02 minta (N=45 teljes kit. / N=500)"), unsafe_allow_html=True)
        st.markdown(info_box("A Big Five kérdőív csak a minta egy részénél lett teljesen kitöltve (N=45). Az adatok tájékoztató jellegűek."), unsafe_allow_html=True)

        big5_df = pd.DataFrame([
            {"dimenzió": "Neuroticizmus (aggódás)",      "Bács02 átlag (4-as sk.)": 2.57, "Jellemzés": "Átlagos"},
            {"dimenzió": "Neuroticizmus (idegesség)",    "Bács02 átlag (4-as sk.)": 2.43, "Jellemzés": "Átlagos"},
            {"dimenzió": "Nyitottság (nyugodtság)",      "Bács02 átlag (4-as sk.)": 2.77, "Jellemzés": "Átlag felett"},
            {"dimenzió": "Extraverzió (beszédesség)",    "Bács02 átlag (4-as sk.)": 3.00, "Jellemzés": "Magas"},
            {"dimenzió": "Extraverzió (társaság)",       "Bács02 átlag (4-as sk.)": 2.78, "Jellemzés": "Átlag felett"},
            {"dimenzió": "Extraverzió (visszafogottság)","Bács02 átlag (4-as sk.)": 2.53, "Jellemzés": "Átlagos"},
        ])

        fig_b5 = px.bar(
            big5_df, x="Bács02 átlag (4-as sk.)", y="dimenzió", orientation="h",
            color="Bács02 átlag (4-as sk.)",
            color_continuous_scale=["#E8E8E8","#0F9ED5","#0E2841"],
            title="Big Five dimenziók – Bács02 átlagok (1–4 skála)",
            text="Bács02 átlag (4-as sk.)",
        )
        fig_b5.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig_b5.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=380,
                              coloraxis_showscale=False, xaxis=dict(range=[1, 4.5]))
        st.plotly_chart(fig_b5, use_container_width=True)

    with tab3:
        st.markdown(section_header("Médiafogyasztás és digitális aktivitás", "KSH digitális adatok + kutatási eredmények"), unsafe_allow_html=True)

        dig_df = pd.DataFrame([
            {"szint": "Alapszintű digitális",   "Bács02": 19429, "Ország": 2112155},
            {"szint": "Középszintű digitális",  "Bács02": 33584, "Ország": 3536979},
            {"szint": "Magas szintű digitális", "Bács02": 7472,  "Ország": 780693},
            {"szint": "Nem végez digitális tev.","Bács02": 13363, "Ország": 1489009},
        ])
        for col in ["Bács02", "Ország"]:
            dig_df[f"{col}_pct"] = (dig_df[col] / dig_df[col].sum() * 100).round(1)

        fig_dig = go.Figure()
        fig_dig.add_trace(go.Bar(name="Bács02", x=dig_df["szint"], y=dig_df["Bács02_pct"], marker_color="#E97132"))
        fig_dig.add_trace(go.Bar(name="Ország", x=dig_df["szint"], y=dig_df["Ország_pct"], marker_color="#156082"))
        fig_dig.update_layout(**PLOTLY_LAYOUT, barmode="group", title="Digitális tevékenységi szint (%)",
                               height=320, yaxis_title="%", legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig_dig, use_container_width=True)

        media_df = pd.DataFrame([
            {"freq": "Soha",          "Bács02": 2.1, "Ország": 5.4},
            {"freq": "Nagyon ritkán", "Bács02": 8.0, "Ország": 3.7},
            {"freq": "Inkább ritkán", "Bács02": 24.3,"Ország": 7.2},
            {"freq": "Inkább sűrűn",  "Bács02": 42.0,"Ország": 45.0},
            {"freq": "Nagyon sűrűn",  "Bács02": 23.6,"Ország": 38.7},
        ])
        fig_med = go.Figure()
        fig_med.add_trace(go.Bar(name="Bács02", x=media_df["freq"], y=media_df["Bács02"], marker_color="#E97132"))
        fig_med.add_trace(go.Bar(name="Ország", x=media_df["freq"], y=media_df["Ország"], marker_color="#156082"))
        fig_med.update_layout(**PLOTLY_LAYOUT, barmode="group", title="Milyen gyakran találkozik politikai tartalommal a közösségi médiában? (%)",
                               height=310, yaxis_title="%", legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig_med, use_container_width=True)

# ─────────────────────────────────────────────
# POLITIKAI KÖZVÉLEMÉNY
# ─────────────────────────────────────────────

def render_kozvelem():
    st.markdown('<div class="page-title">🔭 Politikai Közvéleménykutatás</div>', unsafe_allow_html=True)
    st.markdown(info_box("Századvég nagykutatás adatai – Bács02 (N=500) és Ország (N=20 014)"), unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🗳️ Pártpreferenciák", "🔄 Szavazói átváltás", "📊 Közhangulat"])

    with tab1:
        st.markdown(section_header("Jelenlegi pártpreferenciák", "Ha most vasárnap lennének a parlamenti választások..."), unsafe_allow_html=True)

        cl, cr = st.columns(2)
        with cl:
            fig_pref_b = px.pie(
                PARTPREF_BACS, values="pct", names="párt",
                color="párt",
                color_discrete_map={r["párt"]: r["szín"] for _, r in PARTPREF_BACS.iterrows()},
                title="Pártpreferencia – Bács02 (N=500)",
                hole=0.38,
            )
            fig_pref_b.update_traces(textinfo="label+percent")
            fig_pref_b.update_layout(**PLOTLY_LAYOUT, height=380, legend_font_size=11)
            st.plotly_chart(fig_pref_b, use_container_width=True)

        with cr:
            fig_pref_o = px.pie(
                PARTPREF_ORSZAG, values="pct", names="párt",
                color="párt",
                color_discrete_map={r["párt"]: r["szín"] for _, r in PARTPREF_ORSZAG.iterrows()},
                title="Pártpreferencia – Ország (N=20 014)",
                hole=0.38,
            )
            fig_pref_o.update_traces(textinfo="label+percent")
            fig_pref_o.update_layout(**PLOTLY_LAYOUT, height=380, legend_font_size=11)
            st.plotly_chart(fig_pref_o, use_container_width=True)

        # Összehasonlító bar
        comp_df = PARTPREF_BACS.merge(PARTPREF_ORSZAG, on="párt", suffixes=("_Bács", "_Ország"))
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(name="Bács02", x=comp_df["párt"], y=comp_df["pct_Bács"],
                                   marker_color="#E97132", text=comp_df["pct_Bács"], texttemplate="%{text:.1f}%", textposition="outside"))
        fig_comp.add_trace(go.Bar(name="Ország", x=comp_df["párt"], y=comp_df["pct_Ország"],
                                   marker_color="#156082", text=comp_df["pct_Ország"], texttemplate="%{text:.1f}%", textposition="outside"))
        fig_comp.update_layout(**PLOTLY_LAYOUT, barmode="group", title="Bács02 vs. Ország – pártpreferencia összehasonlítás (%)",
                                height=320, yaxis_title="%", legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_comp, use_container_width=True)

    with tab2:
        st.markdown(section_header("2022-es szavazat vs. jelenlegi preferencia", "Visszamenőleges és aktuális mérés – Bács02"), unsafe_allow_html=True)

        cl, cr = st.columns(2)
        with cl:
            fig_2022 = px.bar(
                SZAVAZAT_2022_BACS.sort_values("pct", ascending=True),
                x="pct", y="párt", orientation="h",
                color="párt",
                color_discrete_map={r["párt"]: r["szín"] for _, r in SZAVAZAT_2022_BACS.iterrows()},
                title="2022 OGY választáson leadott szavazat (Bács02 %, N=500)",
                text="pct",
            )
            fig_2022.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_2022.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=340, xaxis=dict(range=[0, 55]))
            st.plotly_chart(fig_2022, use_container_width=True)

        with cr:
            fig_curr = px.bar(
                PARTPREF_BACS.sort_values("pct", ascending=True),
                x="pct", y="párt", orientation="h",
                color="párt",
                color_discrete_map={r["párt"]: r["szín"] for _, r in PARTPREF_BACS.iterrows()},
                title="Jelenlegi pártpreferencia (Bács02 %, N=500)",
                text="pct",
            )
            fig_curr.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_curr.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=340, xaxis=dict(range=[0, 55]))
            st.plotly_chart(fig_curr, use_container_width=True)

        st.markdown(info_box("Főbb változások: Fidesz 43,5% → 36,0% (−7,5pp), Ellenzék/TISZA 28,5% → 38,4% (+9,9pp), Mi Hazánk 5,6% → 8,0% (+2,4pp)"), unsafe_allow_html=True)

        # Szavazói átváltás sankey
        fig_sankey = go.Figure(go.Sankey(
            node=dict(
                pad=15, thickness=20,
                label=["Fidesz 2022", "Ellenzék 2022", "Mi Hazánk 2022", "Más/NS 2022",
                       "Fidesz ma", "TISZA ma", "Mi Hazánk ma", "DK/más ma", "Bizony./NM"],
                color=["#E97132","#156082","#196B24","#8aaac0",
                       "#E97132","#0F9ED5","#196B24","#2F7EC7","#aaaaaa"],
            ),
            link=dict(
                source=[0,0,0,0,  1,1,1,1,  2,2,2,  3,3,3],
                target=[4,5,6,8,  5,4,6,8,  5,4,6,  4,5,8],
                value =[179,25,8,6,  142,5,5,10,  10,5,13, 10,5,30],
                color =["rgba(233,113,50,0.4)","rgba(233,113,50,0.2)","rgba(233,113,50,0.1)","rgba(233,113,50,0.1)",
                        "rgba(21,96,130,0.4)","rgba(21,96,130,0.2)","rgba(21,96,130,0.1)","rgba(21,96,130,0.1)",
                        "rgba(25,107,36,0.3)","rgba(25,107,36,0.2)","rgba(25,107,36,0.2)",
                        "rgba(138,170,192,0.3)","rgba(138,170,192,0.2)","rgba(138,170,192,0.2)"],
            )
        ))
        fig_sankey.update_layout(**PLOTLY_LAYOUT, title="Szavazói átváltás – 2022 szavazat → jelenlegi preferencia (becslés, Bács02)",
                                  height=380, font_size=12)
        st.plotly_chart(fig_sankey, use_container_width=True)

    with tab3:
        st.markdown(section_header("Politikai közhangulat", "Ország iránya, személyek megítélése – Bács02"), unsafe_allow_html=True)

        hang_df = pd.DataFrame([
            {"állítás": "Az emberek jobbra mennek Magyarorsz.", "pct": 38.6},
            {"állítás": "Az emberek rosszabbra mennek",         "pct": 52.0},
            {"állítás": "A politikusok nem törödnek velük",     "pct": 61.0},
            {"állítás": "A kormány jó munkát végez",            "pct": 34.0},
            {"állítás": "Az ellenzék jobb alternatíva lenne",   "pct": 42.0},
        ])

        fig_hang = px.bar(
            hang_df.sort_values("pct"),
            x="pct", y="állítás", orientation="h",
            color="pct",
            color_continuous_scale=["#E8E8E8","#E97132","#c0392b"],
            title="Közhangulati állítások – egyet értők aránya (Bács02, %)",
            text="pct",
        )
        fig_hang.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_hang.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=320,
                                coloraxis_showscale=False, xaxis=dict(range=[0, 75]))
        st.plotly_chart(fig_hang, use_container_width=True)

        st.markdown(info_box("Részletes személyiségi megítélési adatok és problématérkép a következő adatfeltöltésnél kerül be."), unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SOCIAL MEDIA (PLACEHOLDER)
# ─────────────────────────────────────────────

def render_social():
    st.markdown('<div class="page-title">📱 Social Media Monitor</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:linear-gradient(135deg,#0E2841,#156082);border-radius:12px;padding:40px;text-align:center;margin:20px 0;">
        <div style="font-size:48px;margin-bottom:16px;">📱</div>
        <div style="font-family:'Libre Baskerville',serif;font-size:24px;color:white;margin-bottom:12px;">Social Media Elemzési Modul</div>
        <div style="color:#0F9ED5;font-size:15px;max-width:500px;margin:0 auto;">
            Helyi közszereplők aktivitása, Facebook-csoportok témamodellje, komment-klasszifikáció és sentiment-elemzés – hamarosan elérhető.
        </div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    features = [
        ("👤 Helyi szereplők", "Jelöltek és polgármesterek közösségi média aktivitása: követők, lájkok, kommentek időbeli változása"),
        ("🏷️ Témamodellezés", "NLP topic modeling: helyi FB csoportok és híroldal fő témái, szógyakoriságok, kulcsszó felhő"),
        ("😊 Komment-klasszifikáció", "Pozitív / negatív / semleges arányok per jelölt – sentiment timeline és AI összefoglaló"),
    ]
    for col, (title, desc) in zip([c1, c2, c3], features):
        col.markdown(f"""
        <div class="nav-card" style="border-top-color:#E97132;">
            <div class="nav-title">{title}</div>
            <div class="nav-desc" style="font-size:12px;margin-top:8px;">{desc}</div>
            <div style="margin-top:12px;font-size:11px;color:#E97132;font-weight:700;">🚧 Fejlesztés alatt</div>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GAZDASÁGI ADATOK
# ─────────────────────────────────────────────

def render_gazdasag():
    st.markdown('<div class="page-title">💰 Gazdasági Adatok</div>', unsafe_allow_html=True)
    st.markdown(info_box("Századvég nagykutatás – Bács02 (N=464). Gazdasági percepciók, megélhetés, megtakarítás, inflációérzékelés."), unsafe_allow_html=True)

    # Fejléc KPI-ok
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi_card("Rossz irányba megy az ország", "64,9%", "38,6% határozottan rossznak látja"), unsafe_allow_html=True)
    c2.markdown(kpi_card("Érzi az infláció hatását", "89,2%", "57,5% teljes mértékben"), unsafe_allow_html=True)
    c3.markdown(kpi_card("Van megtakarítása", "42,7%", "52,2% egyáltalán nem"), unsafe_allow_html=True)
    c4.markdown(kpi_card("Anyagi gondok", "13,3%", "Hónapról-hónapra vagy nélkülöz"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🌡️ Makroérzékelés", "🏠 Megélhetés", "💳 Megtakarítás & Hitel"])

    with tab1:
        cl, cr = st.columns(2)
        with cl:
            fig_ir = px.bar(
                GAZD_IRANY, x="pct", y="vélemény", orientation="h",
                color="szín", color_discrete_map={r["szín"]: r["szín"] for _, r in GAZD_IRANY.iterrows()},
                title="Jó vagy rossz irányba mennek a dolgok Magyarországon? (%)",
                text="pct",
            )
            fig_ir.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                                  marker_color=GAZD_IRANY["szín"].tolist())
            fig_ir.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=300, xaxis=dict(range=[0, 50]))
            st.plotly_chart(fig_ir, use_container_width=True)

        with cr:
            fig_mult = px.bar(
                GAZD_MULT, x="pct", y="változás", orientation="h",
                title="Hogyan változott az ország gazdasági helyzete az elmúlt 1 évben? (%)",
                text="pct",
            )
            fig_mult.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                                    marker_color=GAZD_MULT["szín"].tolist())
            fig_mult.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=300, xaxis=dict(range=[0, 55]))
            st.plotly_chart(fig_mult, use_container_width=True)

        # Infláció percepció
        fig_infl = px.pie(
            INFLACIO_ERZEKELES, values="pct", names="válasz",
            color="válasz",
            color_discrete_map={r["válasz"]: r["szín"] for _, r in INFLACIO_ERZEKELES.iterrows()},
            title="Az infláció hatással van a mindennapi megélhetésére? (%)",
            hole=0.4,
        )
        fig_infl.update_layout(**PLOTLY_LAYOUT, height=300)
        st.plotly_chart(fig_infl, use_container_width=True)

        # Inflációs percepció számszerűleg
        inflacio_perc = pd.DataFrame([
            {"becsült infláció": "< 1%",       "pct": 0.6},
            {"becsült infláció": "1–2%",        "pct": 1.7},
            {"becsült infláció": "3–4%",        "pct": 3.0},
            {"becsült infláció": "5–6%",        "pct": 10.8},
            {"becsült infláció": "7–8%",        "pct": 4.5},
            {"becsült infláció": "9–10%",       "pct": 18.5},
            {"becsült infláció": "11–15%",      "pct": 10.8},
            {"becsült infláció": "16–20%",      "pct": 14.7},
            {"becsült infláció": "> 20%",       "pct": 34.1},
            {"becsült infláció": "NT/NV",       "pct": 1.3},
        ])
        fig_infl2 = px.bar(
            inflacio_perc, x="becsült infláció", y="pct",
            title="Becsült inflációs ráta az elmúlt 1 évben (Bács02, %)",
            text="pct",
            color="pct", color_continuous_scale=["#E8E8E8","#E97132","#c0392b"],
        )
        fig_infl2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_infl2.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=300, coloraxis_showscale=False)
        st.plotly_chart(fig_infl2, use_container_width=True)

    with tab2:
        cl, cr = st.columns(2)
        with cl:
            fig_haz = px.pie(
                HAZTARTAS_ANYAG, values="pct", names="helyzet",
                color="helyzet",
                color_discrete_map={r["helyzet"]: r["szín"] for _, r in HAZTARTAS_ANYAG.iterrows()},
                title="Háztartás anyagi helyzete (Bács02, %)",
                hole=0.4,
            )
            fig_haz.update_layout(**PLOTLY_LAYOUT, height=320)
            st.plotly_chart(fig_haz, use_container_width=True)

        with cr:
            megel_df = pd.DataFrame([
                {"önértékelés": "Sokkal rosszabb",     "pct": 9.1,  "szín": "#c0392b"},
                {"önértékelés": "Kicsit rosszabb",     "pct": 19.2, "szín": "#e74c3c"},
                {"önértékelés": "Átlagos",             "pct": 47.8, "szín": "#8aaac0"},
                {"önértékelés": "Kicsit jobb",         "pct": 18.8, "szín": "#196B24"},
                {"önértékelés": "Sokkal jobb",         "pct": 2.6,  "szín": "#1abc9c"},
                {"önértékelés": "NT/NV",               "pct": 2.6,  "szín": "#cccccc"},
            ])
            fig_megel = px.bar(
                megel_df, x="pct", y="önértékelés", orientation="h",
                title="Hogyan értékeli anyagi helyzetét korcsoportjához képest? (%)",
                text="pct",
            )
            fig_megel.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                                     marker_color=megel_df["szín"].tolist())
            fig_megel.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=320, xaxis=dict(range=[0, 60]))
            st.plotly_chart(fig_megel, use_container_width=True)

    with tab3:
        cl, cr = st.columns(2)
        with cl:
            fig_meg = px.pie(
                MEGTAKARITAS, values="pct", names="válasz",
                color="válasz",
                color_discrete_map={r["válasz"]: r["szín"] for _, r in MEGTAKARITAS.iterrows()},
                title="Van-e pénzügyi megtakarítása? (%)",
                hole=0.4,
            )
            fig_meg.update_layout(**PLOTLY_LAYOUT, height=310)
            st.plotly_chart(fig_meg, use_container_width=True)

        with cr:
            felre_df = pd.DataFrame([
                {"rendszeresség": "Havonta/gyakrabban", "pct": 21.3, "szín": "#196B24"},
                {"rendszeresség": "2–3 havonta",        "pct": 15.9, "szín": "#0F9ED5"},
                {"rendszeresség": "Félévente",          "pct": 7.1,  "szín": "#156082"},
                {"rendszeresség": "Évente egyszer",     "pct": 9.7,  "szín": "#0E2841"},
                {"rendszeresség": "Soha",               "pct": 38.6, "szín": "#E97132"},
                {"rendszeresség": "NT/NV",              "pct": 7.3,  "szín": "#cccccc"},
            ])
            fig_felre = px.bar(
                felre_df, x="pct", y="rendszeresség", orientation="h",
                title="Milyen rendszerességgel tesz félre pénzt? (%)",
                text="pct",
            )
            fig_felre.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                                     marker_color=felre_df["szín"].tolist())
            fig_felre.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=310, xaxis=dict(range=[0, 48]))
            st.plotly_chart(fig_felre, use_container_width=True)

# ─────────────────────────────────────────────
# ROUTER – Oldal megjelenítése
# ─────────────────────────────────────────────

if page.startswith("🏠"):
    render_fooldal()
elif page.startswith("🗳️"):
    render_valasztas()
elif page.startswith("👥"):
    render_ksh()
elif page.startswith("📊"):
    render_sajat()
elif page.startswith("🔭"):
    render_kozvelem()
elif page.startswith("📱"):
    render_social()
elif page.startswith("💰"):
    render_gazdasag()
