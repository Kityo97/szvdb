"""
Politikai Hőtérkép – Századvég Alapítvány
Újratervezett, modern Streamlit dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os, base64

# ═══════════════════════════════════════════════════════
# OLDAL KONFIGURÁCIÓ
# ═══════════════════════════════════════════════════════
st.set_page_config(
    page_title="Politikai Hőtérkép · Századvég",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════
# LOGÓK BETÖLTÉSE
# ═══════════════════════════════════════════════════════
def load_logo_b64(path):
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except:
        pass
    return None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_B64 = load_logo_b64(os.path.join(BASE_DIR, "szv_logo.png"))
ICON_B64 = load_logo_b64(os.path.join(BASE_DIR, "szv_icon.png"))

logo_img  = f'<img src="data:image/png;base64,{LOGO_B64}" style="height:34px;">' if LOGO_B64 else '<span style="font-weight:700;font-size:15px;letter-spacing:.15em;color:#E8E8E8;">SZÁZADVÉG</span>'
icon_img  = f'<img src="data:image/png;base64,{ICON_B64}" style="height:26px;filter:brightness(0) invert(1);">' if ICON_B64 else "✦"

# ═══════════════════════════════════════════════════════
# DESIGN KONSTANSOK
# ═══════════════════════════════════════════════════════
C = {
    "navy":     "#0E2841", "navy_mid":  "#163555",
    "blue":     "#156082", "sky":       "#0F9ED5",
    "orange":   "#E97132", "orange_lt": "#F4A469",
    "green":    "#196B24", "purple":    "#A02B93",
    "gray_lt":  "#E8E8E8", "gray_mid":  "#8aaac0",
    "white":    "#FFFFFF", "bg":        "#F0F2F5",
    "red":      "#C0392B", "red_lt":    "#E74C3C",
    "teal":     "#1ABC9C",
}

PARTY_COLORS = {
    "Fidesz-KDNP": C["orange"], "Ellenzék": C["blue"],
    "Mi Hazánk":   C["green"],  "MKKP":     C["purple"],
    "DK":          "#2F7EC7",   "TISZA":    C["sky"],
    "Egyéb":       C["gray_mid"],
}

PLOT_BASE = dict(
    font_family="Inter, system-ui, sans-serif",
    font_color=C["navy"],
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=8, r=8, t=36, b=8),
)

# ═══════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', system-ui, sans-serif;
    background: {C["bg"]};
    color: {C["navy"]};
}}
.block-container {{ padding: 0 !important; max-width: 100% !important; }}
.main > div {{ padding: 0; }}

/* ── Topbar ── */
#topbar {{
    background: {C["navy"]};
    padding: 0 28px; height: 60px;
    display: flex; align-items: center; justify-content: space-between;
    position: sticky; top: 0; z-index: 999;
    box-shadow: 0 2px 12px rgba(0,0,0,.25);
    border-bottom: 2px solid {C["orange"]};
}}
#topbar .tb-title {{
    font-family: 'Playfair Display', serif;
    font-size: 17px; font-weight: 700; color: {C["white"]}; letter-spacing:.02em;
}}
#topbar .tb-badge {{
    background: {C["orange"]}; color: white; font-size: 10px; font-weight: 700;
    padding: 2px 8px; border-radius: 20px; letter-spacing:.08em; text-transform:uppercase;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{ background: {C["navy"]} !important; border-right: none !important; }}
[data-testid="stSidebar"] > div:first-child {{ padding: 0 !important; }}
[data-testid="stSidebar"] * {{ color: {C["gray_lt"]} !important; }}
[data-testid="stSidebar"] .stSelectbox > div > div {{
    background: {C["navy_mid"]} !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    border-radius: 8px !important; color: white !important;
}}
.nav-sec {{ padding: 6px 16px 4px; font-size:10px; font-weight:700;
    letter-spacing:.1em; text-transform:uppercase; color:{C["sky"]} !important; margin-top:12px; }}

/* ── KPI kártyák ── */
.kpi-wrap {{
    background: {C["navy"]}; border-radius: 12px; padding: 16px 16px 18px;
    position: relative; overflow: hidden;
    box-shadow: 0 4px 20px rgba(14,40,65,.18); min-height: 110px;
}}
.kpi-wrap::after {{ content:''; position:absolute; bottom:0; left:0; right:0; height:3px; background:{C["orange"]}; }}
.kpi-label {{ font-size:9px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:{C["sky"]} !important; margin-bottom:6px; line-height:1.4; }}
.kpi-value {{ font-family:'Playfair Display',serif; font-size:24px; font-weight:700; color:{C["white"]} !important; line-height:1.15; white-space:nowrap; }}
.kpi-pct {{ display:inline-block; margin-top:5px; background:rgba(233,113,50,.15); color:{C["orange_lt"]} !important; font-size:11px; font-weight:600; padding:2px 7px; border-radius:20px; }}
.kpi-note {{ font-size:10px; color:rgba(255,255,255,.35) !important; margin-top:4px; }}
.kpi-na {{ font-family:'Playfair Display',serif; font-size:22px; color:rgba(255,255,255,.3) !important; }}

/* ── Chart kártyák ── */
.chart-card {{
    background: {C["white"]}; border-radius: 12px; padding: 20px;
    box-shadow: 0 1px 6px rgba(14,40,65,.06); border: 1px solid rgba(14,40,65,.05); margin-bottom: 16px;
}}
.chart-card h4 {{ font-size:13px; font-weight:700; color:{C["navy"]}; margin:0 0 14px; padding-bottom:10px; border-bottom:1px solid {C["gray_lt"]}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}

/* ── Section ── */
.sec-title {{ font-family:'Playfair Display',serif; font-size:20px; font-weight:700; color:{C["navy"]}; margin:0 0 4px; }}
.sec-sub {{ font-size:12px; color:{C["gray_mid"]}; margin:0 0 18px; }}
.divider {{ height:1px; background:rgba(14,40,65,.08); margin:20px 0; }}

/* ── Info sáv ── */
.info-bar {{ background:rgba(15,158,213,.07); border:1px solid rgba(15,158,213,.2); border-radius:8px; padding:10px 16px; font-size:12px; color:{C["navy"]}; margin-bottom:16px; }}

/* ── Filter badge ── */
.filter-badge {{ display:inline-flex; align-items:center; gap:6px; background:rgba(233,113,50,.1); border:1px solid {C["orange"]}; color:{C["orange"]}; border-radius:20px; padding:4px 14px; font-size:11px; font-weight:600; margin-bottom:18px; }}

/* ── Party rows ── */
.party-row {{ display:flex; align-items:center; padding:8px 12px; border-radius:6px; margin-bottom:4px; background:rgba(14,40,65,.025); }}
.party-dot {{ width:10px; height:10px; border-radius:50%; margin-right:10px; flex-shrink:0; }}
.party-name {{ font-size:12px; font-weight:600; flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.party-right {{ text-align:right; }}
.party-pct {{ font-size:13px; font-weight:700; color:{C["navy"]}; }}
.party-votes {{ font-size:10px; color:{C["gray_mid"]}; }}

/* ── Streamlit overrides ── */
h1,h2,h3 {{ font-family:'Playfair Display',serif; color:{C["navy"]}; }}
.stButton > button {{ background:{C["blue"]} !important; color:white !important; border:none !important; border-radius:8px !important; font-weight:600 !important; font-size:13px !important; padding:9px 18px !important; transition:background .2s; }}
.stButton > button:hover {{ background:{C["orange"]} !important; }}
.stTabs [data-baseweb="tab-list"] {{ gap:0; background:{C["gray_lt"]}; border-radius:8px; padding:3px; }}
.stTabs [data-baseweb="tab"] {{ border-radius:6px; font-size:12px; font-weight:600; padding:7px 18px; color:{C["navy"]} !important; }}
.stTabs [aria-selected="true"] {{ background:{C["navy"]} !important; color:white !important; }}
.page-wrap {{ padding: 22px 28px 50px; }}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# ADATOK
# ═══════════════════════════════════════════════════════

# Listás/NVI 2022 - országos
NAT_LISTAS = {"valasztopolgar":8215304,"megjelentek":5717182,"ervenytelen":57065,"érvényes":5654860,"reszvetel_pct":69.6,"ervenytelen_pct":1.0}
KSH_ORSZAG = {"nep":9603634,"18plus":7918836}

# Megye adatok
COUNTY = {
    "BÁCS-KISKUN":            {"v":410777,"m":277121,"e":3579,"é":273279,"F":160192,"El":81778,"MH":20364,"MK":6321,"Ey":4624},
    "BARANYA":                {"v":297767,"m":201102,"e":3196,"é":197906,"F":102030,"El":71725,"MH":11631,"MK":5417,"Ey":7103},
    "BÉKÉS":                  {"v":276924,"m":183986,"e":2861,"é":181125,"F":95638,"El":64908,"MH":12455,"MK":3975,"Ey":4149},
    "BORSOD-ABAÚJ-ZEMPLÉN":   {"v":513539,"m":332098,"e":5202,"é":326896,"F":178881,"El":112571,"MH":19243,"MK":5707,"Ey":10494},
    "BUDAPEST":               {"v":1274391,"m":959897,"e":10463,"é":949434,"F":387938,"El":465212,"MH":37459,"MK":36893,"Ey":21932},
    "CSONGRÁD-CSANÁD":        {"v":324670,"m":228779,"e":3003,"é":225776,"F":106010,"El":91161,"MH":17181,"MK":4952,"Ey":6472},
    "FEJÉR":                  {"v":340044,"m":242974,"e":2829,"é":240145,"F":130637,"El":82255,"MH":14896,"MK":7604,"Ey":4753},
    "GYŐR-MOSON-SOPRON":      {"v":358942,"m":264610,"e":3268,"é":261342,"F":155905,"El":80997,"MH":15559,"MK":3355,"Ey":5526},
    "HAJDÚ-BIHAR":            {"v":424034,"m":280418,"e":4148,"é":276270,"F":160213,"El":89122,"MH":14920,"MK":1681,"Ey":10334},
    "HEVES":                  {"v":237737,"m":163980,"e":2226,"é":161754,"F":89444,"El":55370,"MH":11832,"MK":1400,"Ey":3708},
    "JÁSZ-NAGYKUN-SZOLNOK":   {"v":297113,"m":195855,"e":2848,"é":193007,"F":106777,"El":67440,"MH":12219,"MK":2481,"Ey":4090},
    "KOMÁROM-ESZTERGOM":      {"v":242615,"m":168223,"e":1927,"é":166296,"F":85000,"El":62609,"MH":9631,"MK":4371,"Ey":4685},
    "NÓGRÁD":                 {"v":153974,"m":103022,"e":1569,"é":101453,"F":57944,"El":30189,"MH":9275,"MK":1976,"Ey":2069},
    "PEST":                   {"v":1039628,"m":757679,"e":9089,"é":748590,"F":385178,"El":277424,"MH":42121,"MK":25170,"Ey":18697},
    "SOMOGY":                 {"v":247256,"m":168503,"e":2602,"é":165901,"F":92638,"El":59311,"MH":6423,"MK":983,"Ey":6546},
    "SZABOLCS-SZATMÁR-BEREG": {"v":440030,"m":287811,"e":4806,"é":283005,"F":172522,"El":84027,"MH":17006,"MK":1633,"Ey":7817},
    "TOLNA":                  {"v":176842,"m":121580,"e":1915,"é":119665,"F":72106,"El":35922,"MH":7999,"MK":1042,"Ey":2596},
    "VAS":                    {"v":202790,"m":151757,"e":1962,"é":149795,"F":89956,"El":46671,"MH":8030,"MK":2722,"Ey":2416},
    "VESZPRÉM":               {"v":279789,"m":200859,"e":2378,"é":198481,"F":106372,"El":74096,"MH":9515,"MK":5213,"Ey":3285},
    "ZALA":                   {"v":220475,"m":157766,"e":2198,"é":155568,"F":88038,"El":50920,"MH":9305,"MK":3752,"Ey":3553},
}
for d in COUNTY.values():
    d["rp"]=round(d["m"]/d["v"]*100,1); d["ep"]=round(d["e"]/d["m"]*100,1)
    d["fp"]=round(d["F"]/d["é"]*100,1); d["elp"]=round(d["El"]/d["é"]*100,1); d["mhp"]=round(d["MH"]/d["é"]*100,1)

BACS_OEVK = [
    {"oevk":"BK/1 – Kecskemét I.",     "szh":"Kecskemét",        "v":69101,"m":47068,"e":566,"é":46462,"F":27420,"El":13464,"MH":3425,"MK":1691,"Ey":462, "ny":"Dr. Salacz László"},
    {"oevk":"BK/2 – Kecskemét II.",    "szh":"Kecskemét",        "v":71933,"m":50963,"e":723,"é":50197,"F":26606,"El":17208,"MH":3512,"MK":2274,"Ey":597, "ny":"Dr. Szeberényi Gy.T."},
    {"oevk":"BK/3 – Kalocsa",          "szh":"Kalocsa",          "v":65242,"m":45135,"e":550,"é":44540,"F":26592,"El":13464,"MH":2778,"MK":0,   "Ey":1706,"ny":"Font Sándor"},
    {"oevk":"BK/4 – Kiskunfélegyháza", "szh":"Kiskunfélegyháza", "v":71615,"m":48039,"e":625,"é":47382,"F":29835,"El":11727,"MH":3427,"MK":1529,"Ey":864, "ny":"Lezsák Sándor"},
    {"oevk":"BK/5 – Kiskunhalas",      "szh":"Kiskunhalas",      "v":68267,"m":43458,"e":586,"é":42827,"F":25763,"El":12218,"MH":4205,"MK":0,   "Ey":641, "ny":"Bányai Gábor"},
    {"oevk":"BK/6 – Baja",            "szh":"Baja",             "v":64619,"m":42458,"e":529,"é":41871,"F":23976,"El":13697,"MH":3017,"MK":827, "Ey":354, "ny":"Zsigó Róbert"},
]
for r in BACS_OEVK:
    r["rp"]=round(r["m"]/r["v"]*100,1); r["ep"]=round(r["e"]/r["m"]*100,1)
    r["fp"]=round(r["F"]/r["é"]*100,1); r["elp"]=round(r["El"]/r["é"]*100,1); r["diff"]=r["F"]-r["El"]

COUNTY_DF = pd.DataFrame([{"megye":k,**{
    "valasztopolgar":d["v"],"megjelentek":d["m"],"ervenytelen":d["e"],"érvényes":d["é"],
    "Fidesz-KDNP":d["F"],"Ellenzék":d["El"],"Mi Hazánk":d["MH"],"MKKP":d["MK"],"Egyéb":d["Ey"],
    "reszvetel_pct":d["rp"],"ervenytelen_pct":d["ep"],"fidesz_pct":d["fp"],"ellenzek_pct":d["elp"],
}} for k,d in COUNTY.items()])
BACS_DF = pd.DataFrame(BACS_OEVK).rename(columns={"rp":"reszvetel_pct","ep":"ervenytelen_pct","fp":"fidesz_pct","elp":"ellenzek_pct","diff":"kulonbseg"})

# Kutatási adatok
PARTPREF_BACS = pd.DataFrame([
    {"párt":"TISZA","pct":38.4,"szín":C["sky"]},{"párt":"Fidesz-KDNP","pct":36.0,"szín":C["orange"]},
    {"párt":"Mi Hazánk","pct":8.0,"szín":C["green"]},{"párt":"DK","pct":2.2,"szín":"#2F7EC7"},
    {"párt":"Bizonytalan","pct":6.9,"szín":"#999"},{"párt":"Egyéb/NM","pct":8.5,"szín":C["gray_mid"]},
])
PARTPREF_ORSZAG = pd.DataFrame([
    {"párt":"TISZA","pct":39.6,"szín":C["sky"]},{"párt":"Fidesz-KDNP","pct":36.2,"szín":C["orange"]},
    {"párt":"Mi Hazánk","pct":6.0,"szín":C["green"]},{"párt":"DK","pct":2.6,"szín":"#2F7EC7"},
    {"párt":"Bizonytalan","pct":5.8,"szín":"#999"},{"párt":"Egyéb/NM","pct":9.8,"szín":C["gray_mid"]},
])
SZAV_2022 = pd.DataFrame([
    {"párt":"Fidesz-KDNP","pct":43.5,"szín":C["orange"]},{"párt":"Ellenzék össze.","pct":28.5,"szín":C["blue"]},
    {"párt":"Mi Hazánk","pct":5.6,"szín":C["green"]},{"párt":"MKKP","pct":3.6,"szín":C["purple"]},
    {"párt":"Nem szavazott","pct":4.0,"szín":C["gray_mid"]},{"párt":"Nem mondja meg","pct":13.0,"szín":"#ccc"},{"párt":"Egyéb","pct":1.8,"szín":"#aaa"},
])

MEGYE_COORDS = {
    "BUDAPEST":(47.48,19.04),"PEST":(47.44,19.55),"FEJÉR":(47.12,18.44),"KOMÁROM-ESZTERGOM":(47.57,18.29),
    "VESZPRÉM":(47.10,17.91),"GYŐR-MOSON-SOPRON":(47.65,17.13),"VAS":(47.23,16.60),"ZALA":(46.73,16.82),
    "SOMOGY":(46.55,17.65),"TOLNA":(46.47,18.56),"BARANYA":(46.07,18.22),"BÁCS-KISKUN":(46.58,19.49),
    "CSONGRÁD-CSANÁD":(46.26,20.15),"BÉKÉS":(46.73,21.10),"HAJDÚ-BIHAR":(47.53,21.63),
    "JÁSZ-NAGYKUN-SZOLNOK":(47.40,20.51),"HEVES":(47.84,20.16),"NÓGRÁD":(48.02,19.52),
    "BORSOD-ABAÚJ-ZEMPLÉN":(48.20,20.65),"SZABOLCS-SZATMÁR-BEREG":(48.05,22.01),
}

# ═══════════════════════════════════════════════════════
# MAGYARORSZÁG MEGYE GEOJSON (egyszerűsített poligonok)
# ═══════════════════════════════════════════════════════
_HU_POLY = {
    "GYŐR-MOSON-SOPRON": [[16.1,47.4],[16.7,47.8],[17.3,47.9],[17.7,47.9],[17.8,47.7],[17.6,47.5],[17.5,47.3],[17.2,47.2],[16.8,47.2],[16.4,47.2],[16.1,47.3],[16.1,47.4]],
    "KOMÁROM-ESZTERGOM": [[17.5,47.5],[17.7,47.8],[18.0,47.9],[18.5,47.8],[18.7,47.6],[18.6,47.4],[18.3,47.3],[17.9,47.3],[17.6,47.3],[17.5,47.4],[17.5,47.5]],
    "VAS":   [[16.1,47.3],[16.4,47.2],[16.8,47.2],[17.2,47.2],[17.5,47.3],[17.5,47.0],[17.3,46.7],[16.9,46.5],[16.5,46.5],[16.1,46.7],[16.1,47.1],[16.1,47.3]],
    "VESZPRÉM": [[17.2,47.6],[17.5,47.5],[17.7,47.5],[18.0,47.5],[18.4,47.5],[18.5,47.4],[18.4,47.2],[17.9,47.2],[17.5,47.0],[17.3,46.9],[17.1,47.0],[17.0,47.2],[17.0,47.4],[17.2,47.6]],
    "ZALA":  [[16.1,46.7],[16.5,46.5],[16.9,46.5],[17.3,46.6],[17.5,46.5],[17.5,46.2],[17.2,45.9],[16.8,45.9],[16.4,46.1],[16.1,46.4],[16.1,46.7]],
    "SOMOGY": [[17.0,47.1],[17.2,46.9],[17.5,46.8],[17.8,46.8],[18.2,46.9],[18.5,46.7],[18.5,46.2],[18.2,45.8],[17.7,45.7],[17.2,45.8],[16.9,46.1],[16.8,46.4],[17.0,46.7],[17.0,47.1]],
    "BARANYA": [[17.4,46.6],[17.8,46.7],[18.1,46.7],[18.4,46.5],[18.5,46.3],[18.5,45.8],[18.1,45.7],[17.7,45.7],[17.3,45.8],[17.0,46.1],[17.2,46.4],[17.4,46.6]],
    "TOLNA": [[17.9,47.2],[18.1,47.2],[18.6,47.2],[18.8,47.0],[18.9,46.8],[18.7,46.4],[18.5,46.1],[18.2,46.1],[18.0,46.3],[17.9,46.6],[17.8,46.8],[17.9,47.0],[17.9,47.2]],
    "FEJÉR": [[17.8,47.5],[18.0,47.6],[18.4,47.6],[18.7,47.6],[19.0,47.5],[19.0,47.2],[18.9,47.0],[18.7,46.8],[18.5,46.8],[18.2,46.8],[17.9,46.9],[17.8,47.1],[17.7,47.3],[17.8,47.5]],
    "BUDAPEST": [[18.9,47.6],[19.1,47.7],[19.35,47.65],[19.35,47.4],[19.1,47.3],[18.9,47.35],[18.9,47.5],[18.9,47.6]],
    "PEST": [[18.5,48.0],[18.9,48.3],[19.3,48.4],[19.9,48.2],[20.4,48.1],[20.5,47.8],[20.3,47.5],[20.2,47.2],[19.9,46.9],[19.5,46.9],[19.0,46.9],[18.7,47.0],[18.7,47.3],[18.9,47.4],[19.1,47.3],[19.35,47.4],[19.35,47.65],[19.1,47.7],[18.9,47.6],[18.9,47.8],[18.5,48.0]],
    "NÓGRÁD": [[18.7,48.1],[19.0,48.4],[19.5,48.4],[19.9,48.3],[20.1,48.1],[20.0,47.9],[19.6,47.8],[19.1,47.8],[18.8,47.9],[18.7,48.1]],
    "HEVES": [[19.6,48.1],[20.1,48.3],[20.5,48.2],[20.6,47.9],[20.5,47.7],[20.3,47.5],[19.9,47.5],[19.5,47.6],[19.5,47.8],[19.6,48.1]],
    "BORSOD-ABAÚJ-ZEMPLÉN": [[20.0,48.2],[20.5,48.5],[21.3,48.6],[22.1,48.5],[22.2,48.2],[21.8,47.8],[21.3,47.8],[20.8,47.8],[20.5,47.7],[20.3,47.8],[20.1,47.9],[20.0,48.2]],
    "SZABOLCS-SZATMÁR-BEREG": [[21.3,48.5],[22.0,48.6],[22.9,48.2],[22.9,47.7],[22.4,47.6],[21.9,47.7],[21.3,47.9],[21.0,48.0],[21.0,48.3],[21.3,48.5]],
    "HAJDÚ-BIHAR": [[21.0,47.8],[21.3,47.8],[21.8,47.9],[22.0,47.7],[22.4,47.6],[22.3,47.1],[21.9,46.8],[21.5,46.8],[21.0,47.0],[20.8,47.3],[20.8,47.6],[21.0,47.8]],
    "JÁSZ-NAGYKUN-SZOLNOK": [[19.8,47.7],[20.3,47.7],[20.8,47.7],[21.0,47.6],[21.0,47.0],[20.7,46.8],[20.3,46.8],[19.9,46.8],[19.5,47.0],[19.5,47.3],[19.7,47.5],[19.8,47.7]],
    "BÁCS-KISKUN": [[18.7,47.2],[19.0,47.1],[19.5,47.1],[19.9,47.0],[20.2,47.0],[20.2,46.8],[20.3,46.4],[20.1,45.9],[19.6,45.8],[19.1,45.8],[18.7,46.0],[18.6,46.3],[18.7,46.8],[18.8,47.0],[18.7,47.2]],
    "CSONGRÁD-CSANÁD": [[20.2,47.1],[20.7,47.0],[21.0,47.0],[21.3,46.8],[21.3,46.2],[21.1,45.9],[20.5,45.8],[20.1,46.0],[19.9,46.3],[20.1,46.7],[20.2,47.0],[20.2,47.1]],
    "BÉKÉS": [[21.0,47.0],[21.4,47.1],[21.8,47.0],[22.2,47.1],[22.3,46.8],[22.1,46.2],[21.5,45.9],[21.0,46.0],[20.8,46.3],[21.0,46.7],[21.0,47.0]],
}

HU_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "id": name,
            "properties": {"name": name},
            "geometry": {"type": "Polygon", "coordinates": [coords]}
        }
        for name, coords in _HU_POLY.items()
    ]
}


# ═══════════════════════════════════════════════════════
# SEGÉDFÜGGVÉNYEK
# ═══════════════════════════════════════════════════════
def fmt(n):
    try: return f"{int(n):,}".replace(",","\u202f")
    except: return str(n)

def kpi(label, value, pct=None, note=None, icon=""):
    pct_h  = f'<div class="kpi-pct">{pct}</div>' if pct else ""
    note_h = f'<div class="kpi-note">{note}</div>' if note else ""
    val_h  = f'<div class="kpi-value">{value}</div>' if value and value!="N/A" else f'<div class="kpi-na">N/A</div>'
    return f"""<div class="kpi-wrap"><div class="kpi-label">{icon} {label}</div>{val_h}{pct_h}{note_h}</div>"""

def info(text, icon="ℹ️"):
    st.markdown(f'<div class="info-bar">{icon} {text}</div>', unsafe_allow_html=True)

def get_active(szint, terulet):
    if szint == "Országos":
        agg = {k: sum(COUNTY[m][k] for m in COUNTY) for k in ["v","m","e","é","F","El","MH","MK","Ey"]}
        agg["rp"]=round(agg["m"]/agg["v"]*100,1); agg["ep"]=round(agg["e"]/agg["m"]*100,1)
        agg["fp"]=round(agg["F"]/agg["é"]*100,1); agg["elp"]=round(agg["El"]/agg["é"]*100,1)
        return {"nev":"Magyarország – Összesített","valasztopolgar":agg["v"],"megjelentek":agg["m"],
                "ervenytelen":agg["e"],"érvényes":agg["é"],"Fidesz-KDNP":agg["F"],"Ellenzék":agg["El"],
                "Mi Hazánk":agg["MH"],"MKKP":agg["MK"],"Egyéb":agg["Ey"],
                "reszvetel_pct":agg["rp"],"ervenytelen_pct":agg["ep"],"fidesz_pct":agg["fp"],
                "ksh_nep":KSH_ORSZAG["nep"],"ksh_18plus":KSH_ORSZAG["18plus"]}
    elif szint == "Megye":
        d = COUNTY.get(terulet,{}); 
        if not d: return get_active("Országos",None)
        return {"nev":terulet.title(),"valasztopolgar":d["v"],"megjelentek":d["m"],"ervenytelen":d["e"],
                "érvényes":d["é"],"Fidesz-KDNP":d["F"],"Ellenzék":d["El"],"Mi Hazánk":d["MH"],
                "MKKP":d["MK"],"Egyéb":d["Ey"],"reszvetel_pct":d["rp"],"ervenytelen_pct":d["ep"],
                "fidesz_pct":d["fp"],"ksh_nep":None,"ksh_18plus":None}
    else:
        rows = [r for r in BACS_OEVK if r["oevk"]==terulet]
        if not rows: return get_active("Országos",None)
        d=rows[0]
        return {"nev":d["oevk"],"valasztopolgar":d["v"],"megjelentek":d["m"],"ervenytelen":d["e"],
                "érvényes":d["é"],"Fidesz-KDNP":d["F"],"Ellenzék":d["El"],"Mi Hazánk":d["MH"],
                "MKKP":d["MK"],"Egyéb":d["Ey"],"reszvetel_pct":d["rp"],"ervenytelen_pct":d["ep"],
                "fidesz_pct":d["fp"],"ksh_nep":None,"ksh_18plus":None}

def grouped_bar(df, x_col, title, h=320):
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Bács02",x=df[x_col],y=df["B_%"],marker_color=C["orange"],
                          text=df["B_%"],texttemplate="%{text:.1f}%",textposition="outside"))
    fig.add_trace(go.Bar(name="Ország",x=df[x_col],y=df["O_%"],marker_color=C["blue"],
                          text=df["O_%"],texttemplate="%{text:.1f}%",textposition="outside"))
    fig.update_layout(**PLOT_BASE,barmode="group",title=title,height=h,yaxis_title="%",
                       legend=dict(orientation="h",y=1.12))
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

# ═══════════════════════════════════════════════════════
# TOPBAR
# ═══════════════════════════════════════════════════════
st.markdown(f"""
<div id="topbar">
  <div style="display:flex;align-items:center;gap:14px;">
    {icon_img}
    {logo_img}
    <div style="width:1px;height:26px;background:rgba(255,255,255,.15);margin:0 2px;"></div>
    <span class="tb-title">Politikai Hőtérkép</span>
    <span class="tb-badge">2022</span>
  </div>
  <div style="color:rgba(255,255,255,.35);font-size:11px;">Századvég Alapítvány · Belső elemzési eszköz</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-sec">Navigáció</div>', unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "Főoldal"

    pages = [("🏠","Főoldal"),("🗳️","Választástörténet"),("👥","KSH Szociológia"),
             ("📊","Saját Kutatások"),("🔭","Politikai Közvélemény"),("📱","Social Media"),("💰","Gazdasági Adatok")]

    for icon_, name_ in pages:
        if st.button(f"{icon_}  {name_}", key=f"nav_{name_}", use_container_width=True):
            st.session_state.page = name_

    st.markdown('<div class="nav-sec" style="margin-top:18px;">Szűrők</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 8px 0;">', unsafe_allow_html=True)

    ev_ = st.selectbox("📅 Év", ["2022"], help="2010–2018 hamarosan")
    szint_ = st.selectbox("📍 Terület", ["Országos","Megye","OEVK (Bács-Kiskun)"])

    terulet_ = None
    if szint_ == "Megye":
        terulet_ = st.selectbox("Megye:", sorted(COUNTY.keys()))
    elif szint_ == "OEVK (Bács-Kiskun)":
        terulet_ = st.selectbox("OEVK:", [r["oevk"] for r in BACS_OEVK])
        szint_ = "OEVK"

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="padding:14px 16px;margin-top:16px;border-top:1px solid rgba(255,255,255,.06);font-size:10px;color:rgba(255,255,255,.25);line-height:1.8;">
      📂 NVI 2022 – Egyéni + listás<br>
      📊 KSH Népszámlálás 2022<br>
      🔬 Századvég nagykutatás<br>
      <span style="color:rgba(233,113,50,.5);">N=500 Bács02 · N=20 014 Ország</span>
    </div>""", unsafe_allow_html=True)

active = get_active(szint_, terulet_)
page   = st.session_state.page

# ═══════════════════════════════════════════════════════
# TARTALOM
# ═══════════════════════════════════════════════════════
st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

# ──────────────── FŐOLDAL ────────────────
if page == "Főoldal":
    st.markdown(f'<p class="sec-title">Összefoglaló áttekintés</p><p class="sec-sub">2022-es OGY választás · {active["nev"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="filter-badge">📍 {active["nev"]} &nbsp;·&nbsp; 🗳️ {ev_}</div>', unsafe_allow_html=True)

    # ── 1. ELEMZÉSI MODULOK (felül) ──
    st.markdown('<p class="sec-title" style="font-size:15px;margin-bottom:10px;">Elemzési modulok</p>', unsafe_allow_html=True)
    nc = st.columns(6)
    nav_items = [
        ("🗳️","Választástörténet","OEVK eredmények, jelölt adatok","Választástörténet"),
        ("👥","KSH Szociológia","Demográfia, végzettség, vallás","KSH Szociológia"),
        ("📊","Saját Kutatások","Ideológiai profil, Big Five","Saját Kutatások"),
        ("🔭","Politikai Közvélemény","Preferenciák, Sankey","Politikai Közvélemény"),
        ("📱","Social Media","Aktivitás, témák – hamarosan","Social Media"),
        ("💰","Gazdasági Adatok","Percepció, megélhetés","Gazdasági Adatok"),
    ]
    for i,(ic,tit,desc,tgt) in enumerate(nav_items):
        with nc[i]:
            st.markdown(f"""
            <div class="chart-card" style="margin-bottom:8px;padding:14px 12px;text-align:center;min-height:100px;">
                <div style="font-size:22px;margin-bottom:6px;">{ic}</div>
                <div style="font-size:11px;font-weight:700;color:{C['navy']};margin-bottom:4px;line-height:1.3;">{tit}</div>
                <div style="font-size:10px;color:{C['gray_mid']};line-height:1.4;">{desc}</div>
            </div>""", unsafe_allow_html=True)
            if st.button("→", key=f"open_{tgt}", use_container_width=True):
                st.session_state.page = tgt; st.rerun()

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── 2. KPI SOR ──
    k1,k2,k3,k4,k5 = st.columns(5)
    nep = active.get("ksh_nep"); nep18 = active.get("ksh_18plus")

    k1.markdown(kpi("Össznépesség (KSH)",fmt(nep) if nep else "N/A",
        pct=f"{round(nep18/nep*100,1)}% szavazóképes" if nep and nep18 else None,
        note="KSH Népszámlálás 2022",icon="👥"), unsafe_allow_html=True)
    k2.markdown(kpi("18+ korú lakos (KSH)",fmt(nep18) if nep18 else "N/A",
        pct=f"{round(nep18/nep*100,1)}% az össznépességből" if nep and nep18 else None,
        note="Szavazóképes korú lakos",icon="📋"), unsafe_allow_html=True)
    k3.markdown(kpi("Nyilv. választópolgár",fmt(active["valasztopolgar"]),
        note="NVI névjegyzék · 2022",icon="📝"), unsafe_allow_html=True)
    k4.markdown(kpi("Tényleges szavazók",fmt(active["megjelentek"]),
        pct=f"{active['reszvetel_pct']}% részvétel",
        note="Névjegyzékbe vettekhez képest",icon="🗳️"), unsafe_allow_html=True)
    k5.markdown(kpi("Érvénytelen szavazatok",fmt(active["ervenytelen"]),
        pct=f"{active['ervenytelen_pct']}% az urnában",
        note="Leadott szavazatokhoz képest",icon="✗"), unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── 3. TÉRKÉP – teljes szélességben, nagy ──
    st.markdown('<div class="chart-card" style="padding:18px 20px;">', unsafe_allow_html=True)
    st.markdown('<h4 style="font-size:13px;font-weight:700;color:#0E2841;margin:0 0 12px;padding-bottom:10px;border-bottom:1px solid #E8E8E8;">🗺️ Térkép – 2022 egyéni szavazatarányok</h4>', unsafe_allow_html=True)

    map_toggle = st.radio("", ["Fidesz %", "Ellenzék %", "Részvétel %"],
                          horizontal=True, label_visibility="collapsed", key="mt")
    val_col = {"Fidesz %": "fp", "Ellenzék %": "elp", "Részvétel %": "rp"}[map_toggle]
    cscale  = {
        "Fidesz %":    [[0,"#fde8d5"],[.5,C["orange"]],[1,"#7a3010"]],
        "Ellenzék %":  [[0,"#d5e8f5"],[.5,C["blue"]],  [1,"#0a2f42"]],
        "Részvétel %": [[0,"#e8edf5"],[.5,C["blue"]],  [1,"#0a2f42"]],
    }[map_toggle]
    map_data = [
        {"megye": k.title(), "lat": MEGYE_COORDS[k][0], "lon": MEGYE_COORDS[k][1],
         "val": d[val_col], "fp": d["fp"], "elp": d["elp"], "rp": d["rp"], "v": d["v"]}
        for k, d in COUNTY.items()
    ]
    mdf = pd.DataFrame(map_data)
    fig_map = px.scatter_geo(
        mdf, lat="lat", lon="lon", size="v",
        color="val", color_continuous_scale=cscale,
        hover_name="megye", size_max=60,
        hover_data={"fp":":.1f","elp":":.1f","rp":":.1f","lat":False,"lon":False,"v":":,","val":":.1f"},
        labels={"fp":"Fidesz %","elp":"Ellenzék %","rp":"Részvétel %","v":"Választópolgár","val":map_toggle},
    )
    fig_map.update_geos(
        scope="europe", center=dict(lat=47.2, lon=19.3), projection_scale=10,
        showland=True, landcolor="#EEF1F5",
        showocean=False,
        showcoastlines=True, coastlinecolor="#cdd4df",
        showcountries=True, countrycolor="#b0bcc9",
        showframe=False, bgcolor="rgba(0,0,0,0)",
    )
    fig_map.update_layout(
        font_family="Inter, system-ui, sans-serif",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=520,
        coloraxis_colorbar=dict(title=map_toggle, len=0.55, thickness=12, tickfont_size=11),
        geo=dict(bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ──────────────── VÁLASZTÁSTÖRTÉNET ────────────────
elif page == "Választástörténet":
    st.markdown(f'<p class="sec-title">🗳️ Választástörténet</p><p class="sec-sub">2022 · {active["nev"]}</p>', unsafe_allow_html=True)
    info("Jelenleg a 2022-es egyéni OEVK adatok érhetők el. Korábbi évek (2010–2018) adatai hamarosan.",icon="📅")

    tab1,tab2,tab3 = st.tabs(["  📊 Bács-Kiskun OEVK-k  ","  🇭🇺 Megye-összehasonlítás  ","  📋 Rangsor & Táblázat  "])

    with tab1:
        sel = st.selectbox("OEVK:",  [r["oevk"] for r in BACS_OEVK])
        row = next(r for r in BACS_OEVK if r["oevk"]==sel)
        c1,c2,c3,c4 = st.columns(4)
        c1.markdown(kpi("Választópolgár",fmt(row["v"]),note="NVI névjegyzék",icon="📋"), unsafe_allow_html=True)
        c2.markdown(kpi("Megjelentek",fmt(row["m"]),pct=f"{row['rp']}% részvétel",icon="🗳️"), unsafe_allow_html=True)
        c3.markdown(kpi("Érvényes",fmt(row["é"]),icon="✓"), unsafe_allow_html=True)
        c4.markdown(kpi("Érvénytelen",fmt(row["e"]),pct=f"{row['ep']}%",icon="✗"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        ca,cb = st.columns([3,2])
        with ca:
            parties=["Fidesz-KDNP","Ellenzék","Mi Hazánk","MKKP","Egyéb"]
            vals=[row[k] for k in ["F","El","MH","MK","Ey"]]
            pcts=[round(v/row["é"]*100,1) for v in vals]
            fig=go.Figure(go.Bar(x=parties,y=pcts,marker_color=[PARTY_COLORS.get(p) for p in parties],
                                  text=[f"{p:.1f}%" for p in pcts],textposition="outside"))
            fig.update_layout(**PLOT_BASE,height=300,title=f"{sel} – eredmény (%)",showlegend=False,yaxis=dict(range=[0,max(pcts)*1.2]))
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        with cb:
            st.markdown(f"""
            <div class="chart-card" style="margin-top:0">
                <h4>🏆 Nyertes</h4>
                <div style="font-size:19px;font-weight:700;color:{C['orange']};margin:6px 0 4px;">{row['ny']}</div>
                <div style="font-size:12px;color:{C['gray_mid']};margin-bottom:12px;">Fidesz-KDNP</div>
                <div style="font-size:13px;margin-bottom:5px;"><b>{round(row['F']/row['é']*100,1)}%</b> – {fmt(row['F'])} szavazat</div>
                <div style="font-size:12px;color:{C['gray_mid']};">Különbség: <b>{fmt(row['diff'])} szavazat</b></div>
            </div>""", unsafe_allow_html=True)
        # Bubble scatter
        fig_sc = px.scatter(BACS_DF,x="fidesz_pct",y="reszvetel_pct",size="v",color="ellenzek_pct",
            color_continuous_scale=[[0,C["gray_lt"]],[0.5,C["blue"]],[1,C["navy"]]],hover_name="oevk",size_max=38,
            title="Fidesz % vs Részvétel – Bács-Kiskun OEVK-k",
            labels={"fidesz_pct":"Fidesz %","reszvetel_pct":"Részvétel %","ellenzek_pct":"Ell. %","v":"Válasz."})
        fig_sc.update_layout(**PLOT_BASE,height=320,coloraxis_colorbar=dict(title="Ell.%",len=0.7,thickness=10))
        st.plotly_chart(fig_sc,use_container_width=True,config={"displayModeBar":False})

    with tab2:
        c1,c2 = st.columns(2)
        with c1:
            fig_f=px.bar(COUNTY_DF.sort_values("fidesz_pct"),x="fidesz_pct",y="megye",orientation="h",
                         color="fidesz_pct",color_continuous_scale=[[0,"#fde8d5"],[.5,C["orange"]],[1,"#7a3010"]],
                         title="Fidesz-KDNP szavazatarány – megyénként (%)",text="fidesz_pct")
            fig_f.update_traces(texttemplate="%{text:.1f}%",textposition="outside")
            fig_f.update_layout(**PLOT_BASE,height=480,showlegend=False,coloraxis_showscale=False,xaxis=dict(range=[0,75]))
            st.plotly_chart(fig_f,use_container_width=True,config={"displayModeBar":False})
        with c2:
            fig_r=px.bar(COUNTY_DF.sort_values("reszvetel_pct"),x="reszvetel_pct",y="megye",orientation="h",
                         color="reszvetel_pct",color_continuous_scale=[[0,"#e8edf5"],[.5,C["blue"]],[1,C["navy"]]],
                         title="Részvételi arány – megyénként (%)",text="reszvetel_pct")
            fig_r.update_traces(texttemplate="%{text:.1f}%",textposition="outside")
            fig_r.update_layout(**PLOT_BASE,height=480,showlegend=False,coloraxis_showscale=False,xaxis=dict(range=[60,80]))
            st.plotly_chart(fig_r,use_container_width=True,config={"displayModeBar":False})

    with tab3:
        info("Bács-Kiskun OEVK-k összehasonlítása – szortírható táblázat",icon="📋")
        tbl=BACS_DF[["oevk","ny","fidesz_pct","ellenzek_pct","reszvetel_pct","ervenytelen_pct","kulonbseg","v"]].copy()
        tbl["rang"]=tbl["fidesz_pct"].rank(ascending=False).astype(int)
        tbl.columns=["OEVK","Nyertes","Fidesz %","Ellenzék %","Részvétel %","Érvénytelen %","Különbség","Válasz.","Rang"]
        st.dataframe(tbl, use_container_width=True, hide_index=True)

# ──────────────── KSH SZOCIOLÓGIA ────────────────
elif page == "KSH Szociológia":
    st.markdown('<p class="sec-title">👥 KSH Szociológia</p><p class="sec-sub">Bács02 VK · KSH Népszámlálás 2022 · Bács02 vs. Ország</p>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi("Bács02 Össznépesség","91 100",note="KSH Népszámlálás 2022",icon="👥"), unsafe_allow_html=True)
    c2.markdown(kpi("18+ korú lakos","73 848",pct="81,1% az össznépességből",icon="✓"), unsafe_allow_html=True)
    c3.markdown(kpi("Nők aránya","51,6%",note="47 043 fő",icon="♀"), unsafe_allow_html=True)
    c4.markdown(kpi("Roma arány","0,64%",note="582 fő (cirány nemz.)",icon="◉"), unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    KSH_KOR=pd.DataFrame([{"k":"0–14","B":14280,"O":1393232},{"k":"15–17","B":2972,"O":291566},
        {"k":"18–24","B":6677,"O":703667},{"k":"25–39","B":16750,"O":1805868},
        {"k":"40–59","B":27373,"O":2864605},{"k":"60–64","B":5345,"O":565253},
        {"k":"65–79","B":13950,"O":1545252},{"k":"80+","B":3753,"O":434191}])
    KSH_VEG=pd.DataFrame([{"k":"8 oszt. alatt","B":1483,"O":171559},{"k":"8 általános","B":12656,"O":1467235},
        {"k":"Szakképesítés","B":16225,"O":1730141},{"k":"Érettségi","B":25057,"O":2716185},{"k":"Diploma","B":18427,"O":1833716}])
    KSH_AKT=pd.DataFrame([{"k":"Foglalkoztatott","B":46176,"O":4707851},{"k":"Munkanélküli","B":1856,"O":234986},
        {"k":"Inaktív ellátott","B":19035,"O":2257357},{"k":"Eltartott","B":6781,"O":718642}])
    KSH_VAL=pd.DataFrame([{"k":"Katolikus","B":24815,"O":2481487},{"k":"Református","B":6107,"O":799881},
        {"k":"Evangélikus","B":709,"O":148965},{"k":"Más keresztény","B":981,"O":117714},
        {"k":"Más felekezet","B":225,"O":36699},{"k":"Nem vallásos","B":9417,"O":1172298}])
    for df_ in [KSH_KOR,KSH_VEG,KSH_AKT,KSH_VAL]:
        df_["B_%"]=(df_["B"]/df_["B"].sum()*100).round(1)
        df_["O_%"]=(df_["O"]/df_["O"].sum()*100).round(1)

    tab1,tab2,tab3,tab4 = st.tabs(["👶 Korcsoport","🎓 Végzettség","💼 Aktivitás","⛪ Vallás"])
    with tab1:
        grouped_bar(KSH_KOR,"k","Korcsoport megoszlás – Bács02 vs. Ország (%)",360)
        ca,cb=st.columns(2)
        disc=[C["navy"],C["blue"],C["sky"],C["orange"],C["orange_lt"],C["green"],C["purple"],C["gray_mid"]]
        with ca:
            fig_=px.pie(KSH_KOR,values="B",names="k",title="Bács02",color_discrete_sequence=disc,hole=0.38)
            fig_.update_layout(**PLOT_BASE,height=250); st.plotly_chart(fig_,use_container_width=True,config={"displayModeBar":False})
        with cb:
            fig_2=px.pie(KSH_KOR,values="O",names="k",title="Ország",color_discrete_sequence=disc,hole=0.38)
            fig_2.update_layout(**PLOT_BASE,height=250); st.plotly_chart(fig_2,use_container_width=True,config={"displayModeBar":False})
    with tab2:
        grouped_bar(KSH_VEG,"k","Iskolai végzettség – Bács02 vs. Ország (%)",310)
        ca,cb=st.columns(2)
        dip_b=KSH_VEG.loc[KSH_VEG["k"]=="Diploma","B_%"].values[0]
        dip_o=KSH_VEG.loc[KSH_VEG["k"]=="Diploma","O_%"].values[0]
        ca.markdown(kpi("Diploma – Bács02",f"{dip_b:.1f}%",pct=f"Ország: {dip_o:.1f}%",note="Felsőfokú végzettség",icon="🎓"), unsafe_allow_html=True)
        cb.markdown(kpi("Érettségi – Bács02",f"{KSH_VEG.loc[KSH_VEG['k']=='Érettségi','B_%'].values[0]:.1f}%",
            pct=f"Ország: {KSH_VEG.loc[KSH_VEG['k']=='Érettségi','O_%'].values[0]:.1f}%",icon="📄"), unsafe_allow_html=True)
    with tab3:
        ca,cb=st.columns(2)
        disc2=[C["sky"],C["orange"],C["green"],C["purple"]]
        with ca:
            f_=px.pie(KSH_AKT,values="B",names="k",title="Aktivitás – Bács02",color_discrete_sequence=disc2,hole=0.38)
            f_.update_layout(**PLOT_BASE,height=300); st.plotly_chart(f_,use_container_width=True,config={"displayModeBar":False})
        with cb:
            f_2=px.pie(KSH_AKT,values="O",names="k",title="Aktivitás – Ország",color_discrete_sequence=disc2,hole=0.38)
            f_2.update_layout(**PLOT_BASE,height=300); st.plotly_chart(f_2,use_container_width=True,config={"displayModeBar":False})
        grouped_bar(KSH_AKT,"k","Aktivitás összehasonlítás (%)",270)
    with tab4:
        grouped_bar(KSH_VAL,"k","Vallási megoszlás – Bács02 vs. Ország (%)",330)

# ──────────────── SAJÁT KUTATÁSOK ────────────────
elif page == "Saját Kutatások":
    st.markdown('<p class="sec-title">📊 Saját Kutatások</p><p class="sec-sub">Századvég nagykutatás · Bács02 (N=500) · Ország (N=20 014)</p>', unsafe_allow_html=True)
    LIBKONZ=pd.DataFrame([{"sk":"1–Lib","B":4.2,"O":10.4},{"sk":"2","B":5.1,"O":6.2},{"sk":"3","B":10.1,"O":13.2},
        {"sk":"4–Közép","B":36.3,"O":29.3},{"sk":"5","B":14.9,"O":11.6},{"sk":"6","B":6.9,"O":7.3},{"sk":"7–Konz","B":22.5,"O":21.9}])
    BALJOBB=pd.DataFrame([{"sk":"1–Bal","B":9.1,"O":11.2},{"sk":"2","B":5.9,"O":3.3},{"sk":"3","B":6.4,"O":11.0},
        {"sk":"4–Közép","B":34.3,"O":30.7},{"sk":"5","B":12.9,"O":9.4},{"sk":"6","B":7.8,"O":8.2},{"sk":"7–Jobb","B":23.6,"O":26.2}])
    for df_ in [LIBKONZ,BALJOBB]:
        df_["B_%"]=df_["B"]; df_["O_%"]=df_["O"]

    tab1,tab2,tab3 = st.tabs(["🧭 Ideológiai profil","🧠 Big Five","📺 Médiafogyasztás"])
    with tab1:
        ca,cb=st.columns(2)
        with ca: grouped_bar(LIBKONZ,"sk","Liberális ↔ Konzervatív skála (%)",290)
        with cb: grouped_bar(BALJOBB,"sk","Baloldali ↔ Jobboldali skála (%)",290)
        lk_b=sum((i+1)*v/100 for i,v in enumerate(LIBKONZ["B"])); lk_o=sum((i+1)*v/100 for i,v in enumerate(LIBKONZ["O"]))
        bj_b=sum((i+1)*v/100 for i,v in enumerate(BALJOBB["B"])); bj_o=sum((i+1)*v/100 for i,v in enumerate(BALJOBB["O"]))
        m1,m2,m3,m4=st.columns(4)
        m1.markdown(kpi("Lib↔Konz – Bács02",f"{lk_b:.2f}",note="7-es skálán (mag.=konz.)",icon="↔"), unsafe_allow_html=True)
        m2.markdown(kpi("Lib↔Konz – Ország",f"{lk_o:.2f}",note="7-es skálán",icon="↔"), unsafe_allow_html=True)
        m3.markdown(kpi("Bal↔Jobb – Bács02",f"{bj_b:.2f}",note="7-es skálán (mag.=jobb.)",icon="↔"), unsafe_allow_html=True)
        m4.markdown(kpi("Bal↔Jobb – Ország",f"{bj_o:.2f}",note="7-es skálán",icon="↔"), unsafe_allow_html=True)
    with tab2:
        info("Big Five – tájékoztató jellegű (N=45 teljes kitöltő Bács02-ből)",icon="⚠️")
        b5=pd.DataFrame([{"d":"Neuroticizmus – Aggódik","a":2.57},{"d":"Neuroticizmus – Idegessé válik","a":2.43},
            {"d":"Nyitottság – Nyugodt marad","a":2.77},{"d":"Extraverzió – Beszédes","a":3.00},
            {"d":"Extraverzió – Társaságkedvelő","a":2.78},{"d":"Extraverzió – Visszafogott","a":2.53}])
        fig_b5=px.bar(b5,x="a",y="d",orientation="h",color="a",
            color_continuous_scale=[[0,C["gray_lt"]],[.5,C["sky"]],[1,C["navy"]]],
            title="Big Five dimenziók – Bács02 átlagok (1–4 skála)",text="a")
        fig_b5.update_traces(texttemplate="%{text:.2f}",textposition="outside")
        fig_b5.update_layout(**PLOT_BASE,showlegend=False,height=370,coloraxis_showscale=False,xaxis=dict(range=[1,4.5]))
        st.plotly_chart(fig_b5,use_container_width=True,config={"displayModeBar":False})
    with tab3:
        dig=pd.DataFrame([{"k":"Alapszintű","B":26.3,"O":26.7,"B_%":26.3,"O_%":26.7},{"k":"Középszintű","B":45.5,"O":44.7,"B_%":45.5,"O_%":44.7},
            {"k":"Magas szintű","B":10.1,"O":9.9,"B_%":10.1,"O_%":9.9},{"k":"Nem digitális","B":18.1,"O":18.8,"B_%":18.1,"O_%":18.8}])
        med=pd.DataFrame([{"k":"Soha","B":2.1,"O":5.4,"B_%":2.1,"O_%":5.4},{"k":"Nagyon ritkán","B":8.0,"O":3.7,"B_%":8.0,"O_%":3.7},
            {"k":"Inkább ritkán","B":24.3,"O":7.2,"B_%":24.3,"O_%":7.2},{"k":"Inkább sűrűn","B":42.0,"O":45.0,"B_%":42.0,"O_%":45.0},
            {"k":"Nagyon sűrűn","B":23.6,"O":38.7,"B_%":23.6,"O_%":38.7}])
        ca,cb=st.columns(2)
        with ca: grouped_bar(dig,"k","Digitális aktivitás (%)",300)
        with cb: grouped_bar(med,"k","Politikai tartalom a közösségi médiában (%)",300)

# ──────────────── POLITIKAI KÖZVÉLEMÉNY ────────────────
elif page == "Politikai Közvélemény":
    st.markdown('<p class="sec-title">🔭 Politikai Közvéleménykutatás</p><p class="sec-sub">Századvég nagykutatás · Bács02 (N=500) · Ország (N=20 014)</p>', unsafe_allow_html=True)

    tab1,tab2,tab3 = st.tabs(["🗳️ Pártpreferenciák","🔄 Szavazói átváltás","📊 Közhangulat"])
    with tab1:
        ca,cb=st.columns(2)
        def pbar(df,title):
            fig=go.Figure(go.Bar(y=df["párt"],x=df["pct"],orientation="h",
                marker_color=df["szín"].tolist(),text=df["pct"].apply(lambda x:f"{x:.1f}%"),textposition="outside"))
            fig.update_layout(**PLOT_BASE,title=title,height=330,xaxis=dict(range=[0,52],title="%"),showlegend=False)
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        with ca: pbar(PARTPREF_BACS.sort_values("pct"),"Ha most lennének választások – Bács02 (%)")
        with cb: pbar(PARTPREF_ORSZAG.sort_values("pct"),"Ha most lennének választások – Ország (%)")
        comp=PARTPREF_BACS.merge(PARTPREF_ORSZAG,on="párt",suffixes=("_B","_O"))
        fig_cmp=go.Figure()
        fig_cmp.add_trace(go.Bar(name="Bács02",x=comp["párt"],y=comp["pct_B"],marker_color=C["orange"],
            text=comp["pct_B"],texttemplate="%{text:.1f}%",textposition="outside"))
        fig_cmp.add_trace(go.Bar(name="Ország",x=comp["párt"],y=comp["pct_O"],marker_color=C["blue"],
            text=comp["pct_O"],texttemplate="%{text:.1f}%",textposition="outside"))
        fig_cmp.update_layout(**PLOT_BASE,barmode="group",title="Bács02 vs. Ország összehasonlítás (%)",height=300,
                               yaxis_title="%",legend=dict(orientation="h",y=1.12))
        st.plotly_chart(fig_cmp,use_container_width=True,config={"displayModeBar":False})
    with tab2:
        ca,cb=st.columns(2)
        with ca: pbar2=lambda df,t: [px.bar(df.sort_values("pct"),x="pct",y="párt",orientation="h",color="párt",
            color_discrete_map={r["párt"]:r["szín"] for _,r in df.iterrows()},title=t,text="pct") or None]
        def hbar(df,title):
            fig=px.bar(df.sort_values("pct"),x="pct",y="párt",orientation="h",color="párt",
                color_discrete_map={r["párt"]:r["szín"] for _,r in df.iterrows()},title=title,text="pct")
            fig.update_traces(texttemplate="%{text:.1f}%",textposition="outside")
            fig.update_layout(**PLOT_BASE,showlegend=False,height=330,xaxis=dict(range=[0,55]))
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        with ca: hbar(SZAV_2022,"2022 OGY leadott szavazat – Bács02 (%)")
        with cb: hbar(PARTPREF_BACS,"Jelenlegi preferencia – Bács02 (%)")
        info("Fidesz: 43,5% → 36,0% (−7,5pp)  ·  TISZA/Ellenzék: 28,5% → 38,4% (+9,9pp)  ·  Mi Hazánk: 5,6% → 8,0% (+2,4pp)",icon="📌")
        fig_sk=go.Figure(go.Sankey(
            node=dict(pad=18,thickness=22,
                label=["Fidesz 2022","Ellenzék 2022","Mi Hazánk 2022","Más/NS 2022","Fidesz ma","TISZA ma","Mi Hazánk ma","DK/más ma","Bizony./NM"],
                color=[C["orange"],C["blue"],C["green"],C["gray_mid"],C["orange"],C["sky"],C["green"],C["blue"],"#999"]),
            link=dict(source=[0,0,0,0,1,1,1,1,2,2,2,3,3,3],target=[4,5,6,8,5,4,6,8,5,4,6,4,5,8],
                value=[179,25,8,6,142,5,5,10,10,5,13,10,5,30],
                color=["rgba(233,113,50,.35)"]*4+["rgba(21,96,130,.35)"]*4+["rgba(25,107,36,.35)"]*3+["rgba(138,170,192,.3)"]*3)))
        fig_sk.update_layout(**PLOT_BASE,title="Szavazói átváltás – 2022 → jelenlegi preferencia (becslés, Bács02)",height=370)
        st.plotly_chart(fig_sk,use_container_width=True,config={"displayModeBar":False})
    with tab3:
        HANG=pd.DataFrame([{"á":"Ország rossz irányba","pct":64.9},{"á":"Infláció hat a megélhetésre","pct":89.2},
            {"á":"Gazdasági helyzet romlott","pct":67.6},{"á":"Közszolgáltatások romlottak","pct":69.0},{"á":"Munkanélküliség nőtt","pct":36.9}])
        IRANY=pd.DataFrame([{"v":"Határozottan rossz","pct":38.6,"c":C["red"]},{"v":"Inkább rossz","pct":26.3,"c":C["red_lt"]},
            {"v":"Is-is","pct":12.5,"c":C["gray_mid"]},{"v":"Inkább jó","pct":18.3,"c":C["green"]},{"v":"Határozottan jó","pct":3.4,"c":C["teal"]}])
        ca,cb=st.columns(2)
        with ca:
            fig_ir=px.pie(IRANY,values="pct",names="v",color="v",
                color_discrete_map={r["v"]:r["c"] for _,r in IRANY.iterrows()},
                title="Jó/rossz irányba az ország? (Bács02, %)",hole=0.42)
            fig_ir.update_layout(**PLOT_BASE,height=310); st.plotly_chart(fig_ir,use_container_width=True,config={"displayModeBar":False})
        with cb:
            fig_h=px.bar(HANG.sort_values("pct"),x="pct",y="á",orientation="h",color="pct",
                color_continuous_scale=[[0,C["gray_lt"]],[.5,C["orange"]],[1,C["red"]]],
                title="Közhangulati állítások – egyet értők % (Bács02)",text="pct")
            fig_h.update_traces(texttemplate="%{text:.1f}%",textposition="outside")
            fig_h.update_layout(**PLOT_BASE,showlegend=False,height=310,coloraxis_showscale=False,xaxis=dict(range=[0,100]))
            st.plotly_chart(fig_h,use_container_width=True,config={"displayModeBar":False})

# ──────────────── SOCIAL MEDIA ────────────────
elif page == "Social Media":
    st.markdown('<p class="sec-title">📱 Social Media Monitor</p><p class="sec-sub">API integráció folyamatban · Hamarosan elérhető</p>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{C['navy']},{C['blue']});border-radius:16px;padding:56px 40px;text-align:center;margin:10px 0 28px;">
        <div style="font-size:52px;margin-bottom:18px;">📱</div>
        <div style="font-family:'Playfair Display',serif;font-size:24px;color:white;margin-bottom:12px;">Social Media Elemzési Modul</div>
        <div style="color:rgba(255,255,255,.55);font-size:13px;max-width:460px;margin:0 auto;line-height:1.8;">
            Helyi közszereplők aktivitása · Facebook-csoportok témamodell<br>
            Komment-klasszifikáció · Sentiment-elemzés · AI összefoglaló
        </div>
    </div>""", unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    for col,(ic,t,d) in zip([c1,c2,c3],[
        ("👤","Helyi szereplők","Jelöltek FB/Instagram aktivitása: követők, lájkok, kommentek időbeli változása"),
        ("🏷️","Témamodellezés","NLP topic modeling: helyi FB csoportok és híroldal főbb témái, szógyakoriságok"),
        ("😊","Komment-klasszifikáció","Pozitív/negatív/semleges arányok per jelölt – sentiment timeline"),]):
        col.markdown(f"""<div class="chart-card" style="text-align:center;padding:28px 18px;">
            <div style="font-size:30px;margin-bottom:10px;">{ic}</div>
            <div style="font-size:13px;font-weight:700;color:{C['navy']};margin-bottom:8px;">{t}</div>
            <div style="font-size:11px;color:{C['gray_mid']};line-height:1.6;">{d}</div>
            <div style="margin-top:12px;font-size:11px;color:{C['orange']};font-weight:700;">🚧 Hamarosan</div>
        </div>""", unsafe_allow_html=True)

# ──────────────── GAZDASÁGI ADATOK ────────────────
elif page == "Gazdasági Adatok":
    st.markdown('<p class="sec-title">💰 Gazdasági Adatok</p><p class="sec-sub">Századvég nagykutatás · Bács02 (N=464) · Percepciók, megélhetés, megtakarítás</p>', unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    c1.markdown(kpi("Rossz irányba az ország","64,9%",note="38,6% határozottan",icon="📉"), unsafe_allow_html=True)
    c2.markdown(kpi("Érzi az inflációt","89,2%",note="57,5% teljesen",icon="💸"), unsafe_allow_html=True)
    c3.markdown(kpi("Van megtakarítása","42,7%",note="52,2% egyáltalán nincs",icon="🏦"), unsafe_allow_html=True)
    c4.markdown(kpi("Anyagi gondok","13,3%",note="Hónapról-hónapra / nélkülöz",icon="⚠️"), unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    tab1,tab2,tab3=st.tabs(["🌡️ Makroérzékelés","🏠 Megélhetés","💳 Megtakarítás"])
    with tab1:
        GAZD=pd.DataFrame([{"k":"Határozottan romlott","pct":43.5,"c":C["red"]},{"k":"Kismértékben romlott","pct":24.1,"c":C["red_lt"]},
            {"k":"Nem változott","pct":18.1,"c":C["gray_mid"]},{"k":"Kismértékben javult","pct":9.7,"c":C["green"]},{"k":"Határozottan javult","pct":3.0,"c":C["teal"]}])
        INFL=pd.DataFrame([{"k":"<1%","pct":0.6},{"k":"1–2%","pct":1.7},{"k":"3–4%","pct":3.0},{"k":"5–6%","pct":10.8},
            {"k":"7–8%","pct":4.5},{"k":"9–10%","pct":18.5},{"k":"11–15%","pct":10.8},{"k":"16–20%","pct":14.7},{"k":">20%","pct":34.1}])
        ca,cb=st.columns(2)
        with ca:
            fig_g=px.bar(GAZD,x="pct",y="k",orientation="h",title="Ország gazd. helyzete az elmúlt 1 évben (%)",text="pct")
            fig_g.update_traces(texttemplate="%{text:.1f}%",textposition="outside",marker_color=GAZD["c"].tolist())
            fig_g.update_layout(**PLOT_BASE,showlegend=False,height=300,xaxis=dict(range=[0,55]))
            st.plotly_chart(fig_g,use_container_width=True,config={"displayModeBar":False})
        with cb:
            fig_i=px.bar(INFL,x="k",y="pct",color="pct",color_continuous_scale=[[0,C["gray_lt"]],[.5,C["orange"]],[1,C["red"]]],
                title="Becsült infláció az elmúlt évben (Bács02, %)",text="pct")
            fig_i.update_traces(texttemplate="%{text:.1f}%",textposition="outside")
            fig_i.update_layout(**PLOT_BASE,showlegend=False,height=300,coloraxis_showscale=False)
            st.plotly_chart(fig_i,use_container_width=True,config={"displayModeBar":False})
    with tab2:
        HAZ=pd.DataFrame([{"h":"Gondok nélkül","pct":7.3,"c":C["teal"]},{"h":"Jól kijövünk","pct":35.3,"c":C["green"]},
            {"h":"Éppen kijövünk","pct":43.8,"c":C["gray_mid"]},{"h":"Anyagi gondok","pct":11.4,"c":C["red_lt"]},{"h":"Nélkülözünk","pct":1.9,"c":C["red"]}])
        MEG=pd.DataFrame([{"m":"Sokkal rosszabb","pct":9.1,"c":C["red"]},{"m":"Kicsit rosszabb","pct":19.2,"c":C["red_lt"]},
            {"m":"Átlagos","pct":47.8,"c":C["gray_mid"]},{"m":"Kicsit jobb","pct":18.8,"c":C["green"]},{"m":"Sokkal jobb","pct":2.6,"c":C["teal"]}])
        ca,cb=st.columns(2)
        with ca:
            fh=px.pie(HAZ,values="pct",names="h",color="h",color_discrete_map={r["h"]:r["c"] for _,r in HAZ.iterrows()},
                title="Háztartás anyagi helyzete (Bács02, %)",hole=0.42)
            fh.update_layout(**PLOT_BASE,height=310); st.plotly_chart(fh,use_container_width=True,config={"displayModeBar":False})
        with cb:
            fm=px.bar(MEG,x="pct",y="m",orientation="h",title="Anyagi helyzet korcsoporthoz képest (Bács02, %)",text="pct")
            fm.update_traces(texttemplate="%{text:.1f}%",textposition="outside",marker_color=MEG["c"].tolist())
            fm.update_layout(**PLOT_BASE,showlegend=False,height=310,xaxis=dict(range=[0,60]))
            st.plotly_chart(fm,use_container_width=True,config={"displayModeBar":False})
    with tab3:
        M2=pd.DataFrame([{"m":"Van megtakarítása","pct":42.7,"c":C["blue"]},{"m":"Nincs","pct":52.2,"c":C["orange"]},{"m":"NT/NV","pct":5.2,"c":C["gray_mid"]}])
        FL=pd.DataFrame([{"f":"Havonta/gyakrabban","pct":21.3,"c":C["teal"]},{"f":"2–3 havonta","pct":15.9,"c":C["green"]},
            {"f":"Félévente","pct":7.1,"c":C["blue"]},{"f":"Évente egyszer","pct":9.7,"c":C["sky"]},
            {"f":"Soha","pct":38.6,"c":C["orange"]},{"f":"NT/NV","pct":7.3,"c":C["gray_mid"]}])
        ca,cb=st.columns(2)
        with ca:
            fm2=px.pie(M2,values="pct",names="m",color="m",color_discrete_map={r["m"]:r["c"] for _,r in M2.iterrows()},
                title="Van pénzügyi megtakarítása? (Bács02, %)",hole=0.42)
            fm2.update_layout(**PLOT_BASE,height=310); st.plotly_chart(fm2,use_container_width=True,config={"displayModeBar":False})
        with cb:
            ff=px.bar(FL,x="pct",y="f",orientation="h",title="Milyen rendszerességgel tesz félre pénzt? (%)",text="pct")
            ff.update_traces(texttemplate="%{text:.1f}%",textposition="outside",marker_color=FL["c"].tolist())
            ff.update_layout(**PLOT_BASE,showlegend=False,height=310,xaxis=dict(range=[0,48]))
            st.plotly_chart(ff,use_container_width=True,config={"displayModeBar":False})

st.markdown('</div>', unsafe_allow_html=True)
