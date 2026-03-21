# ============================================================
# 🥭 FARMER PROFIT INTELLIGENCE SYSTEM
# Smart Mango Marketing Decision Engine
# Developed by: S.R.L. Keerthi
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import folium
import requests
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import base64, os

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="Farmer Profit Intelligence System | S.R.L. Keerthi",
    page_icon="🥭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── TRANSLATIONS ─────────────────────────────────────────────
LANGS = {
    "English": {
        "title": "Farmer Profit Intelligence System",
        "subtitle": "Smart Mango Marketing Decision Engine",
        "panel": "Analysis Control Panel",
        "village": "📍 Select Your Village",
        "variety": "🥭 Select Mango Variety",
        "qty": "📦 Quantity (Quintals)",
        "run": "🚀 Run Smart Analysis",
        "tip": "💡 Combine your harvest with nearby farmers to reduce transport cost per quintal!",
        "base_price": "Base Price (₹/kg)",
        "total_rev": "Total Revenue (₹)",
        "best_mkt": "Best Market",
        "best_profit": "Best Profit (₹)",
        "chart_title": "📈 Profit Comparison",
        "table_title": "📋 Top 10 Closest Markets",
        "map_title": "📍 Market Location Map",
        "advice_title": "💡 Selling Advice",
        "col_market": "Market / Buyer",
        "col_type": "Type",
        "col_dist": "Distance (km)",
        "col_rev": "Revenue (₹)",
        "col_trans": "Transport (₹)",
        "col_profit": "Net Profit (₹)",
        "col_pct": "% of Best",
        "adv1_t": "⏰ Best Time to Sell",
        "adv1_b": "Sell early morning when prices are highest at Mandi. Export buyers prefer pre-sorted fruit.",
        "adv2_t": "🤝 Negotiate Better",
        "adv2_b": "Quote 2–3 buyers simultaneously and show them competitor prices to secure a better deal.",
        "adv3_t": "🚛 Transport Tip",
        "adv3_b": "Combine load with neighbouring farmers to split transport cost and increase net profit.",
        "adv4_t": "⭐ Quality Matters",
        "adv4_b": "Grade A fruit fetches 15–25% more. Sort before loading to maximise return.",
        "live_prices": "📈 Live Market Prices Today",
    },
    "తెలుగు": {
        "title": "రైతు లాభ ఇంటెలిజెన్స్ సిస్టమ్",
        "subtitle": "స్మార్ట్ మామిడి మార్కెటింగ్ నిర్ణయ యంత్రం",
        "panel": "విశ్లేషణ నియంత్రణ ప్యానెల్",
        "village": "📍 మీ గ్రామం ఎంచుకోండి",
        "variety": "🥭 మామిడి రకం ఎంచుకోండి",
        "qty": "📦 పరిమాణం (క్వింటాళ్ళు)",
        "run": "🚀 స్మార్ట్ విశ్లేషణ చేయండి",
        "tip": "💡 రవాణా ఖర్చు తగ్గించడానికి పొరుగు రైతులతో కలిసి అమ్మండి!",
        "base_price": "బేస్ ధర (₹/కేజీ)",
        "total_rev": "మొత్తం ఆదాయం (₹)",
        "best_mkt": "అత్యుత్తమ మార్కెట్",
        "best_profit": "అత్యధిక లాభం (₹)",
        "chart_title": "📈 లాభాల పోలిక",
        "table_title": "📋 టాప్ 10 సమీప మార్కెట్లు",
        "map_title": "📍 మార్కెట్ స్థాన మ్యాప్",
        "advice_title": "💡 అమ్మకపు సలహా",
        "col_market": "మార్కెట్ / కొనుగోలుదారు",
        "col_type": "రకం",
        "col_dist": "దూరం (కి.మీ)",
        "col_rev": "ఆదాయం (₹)",
        "col_trans": "రవాణా (₹)",
        "col_profit": "నికర లాభం (₹)",
        "col_pct": "% అత్యుత్తమ",
        "adv1_t": "⏰ అమ్మడానికి అత్యుత్తమ సమయం",
        "adv1_b": "తెల్లవారుజామున అమ్మండి — మండీలో ధరలు అప్పుడు ఎక్కువగా ఉంటాయి.",
        "adv2_t": "🤝 మెరుగైన ధర చర్చించండి",
        "adv2_b": "2-3 మంది కొనుగోలుదారులను ఒకేసారి సంప్రదించి పోటీ ధరలు చూపించండి.",
        "adv3_t": "🚛 రవాణా సూచన",
        "adv3_b": "పొరుగు రైతులతో కలిసి రవాణా చేయండి — ఖర్చు తక్కువవుతుంది.",
        "adv4_t": "⭐ నాణ్యత ముఖ్యం",
        "adv4_b": "గ్రేడ్ A మామిడి 15-25% ఎక్కువ ధర పొందుతుంది.",
        "live_prices": "📈 నేటి మార్కెట్ ధరలు",
    },
    "हिंदी": {
        "title": "किसान लाभ बुद्धिमत्ता प्रणाली",
        "subtitle": "स्मार्ट आम विपणन निर्णय इंजन",
        "panel": "विश्लेषण नियंत्रण पैनल",
        "village": "📍 अपना गांव चुनें",
        "variety": "🥭 आम की किस्म चुनें",
        "qty": "📦 मात्रा (क्विंटल)",
        "run": "🚀 स्मार्ट विश्लेषण चलाएं",
        "tip": "💡 परिवहन लागत कम करने के लिए पड़ोसी किसानों के साथ मिलकर बेचें!",
        "base_price": "आधार मूल्य (₹/किग्रा)",
        "total_rev": "कुल आय (₹)",
        "best_mkt": "सर्वोत्तम बाजार",
        "best_profit": "सर्वाधिक लाभ (₹)",
        "chart_title": "📈 लाभ तुलना",
        "table_title": "📋 शीर्ष 10 निकटतम बाजार",
        "map_title": "📍 बाजार स्थान मानचित्र",
        "advice_title": "💡 बिक्री सलाह",
        "col_market": "बाजार / खरीदार",
        "col_type": "प्रकार",
        "col_dist": "दूरी (कि.मी.)",
        "col_rev": "आय (₹)",
        "col_trans": "परिवहन (₹)",
        "col_profit": "शुद्ध लाभ (₹)",
        "col_pct": "% सर्वोत्तम",
        "adv1_t": "⏰ बेचने का सबसे अच्छा समय",
        "adv1_b": "सुबह जल्दी बेचें — मंडी में भाव ऊंचे होते हैं।",
        "adv2_t": "🤝 बेहतर भाव मांगें",
        "adv2_b": "2-3 खरीदारों से एक साथ बात करें और प्रतिस्पर्धी भाव दिखाएं।",
        "adv3_t": "🚛 परिवहन सुझाव",
        "adv3_b": "पड़ोसी किसानों के साथ मिलकर परिवहन करें — लागत बंटेगी।",
        "adv4_t": "⭐ गुणवत्ता महत्वपूर्ण",
        "adv4_b": "ग्रेड A आम 15-25% ज्यादा भाव पाता है।",
        "live_prices": "📈 आज के बाजार भाव",
    },
    "தமிழ்": {
        "title": "விவசாயி லாப நுண்ணறிவு அமைப்பு",
        "subtitle": "ஸ்மார்ட் மாம்பழ சந்தை முடிவு இயந்திரம்",
        "panel": "பகுப்பாய்வு கட்டுப்பாட்டு பலகை",
        "village": "📍 உங்கள் கிராமத்தை தேர்ந்தெடுக்கவும்",
        "variety": "🥭 மாம்பழ வகையை தேர்ந்தெடுக்கவும்",
        "qty": "📦 அளவு (குவிண்டால்)",
        "run": "🚀 ஸ்மார்ட் பகுப்பாய்வு இயக்கு",
        "tip": "💡 போக்குவரத்து செலவைக் குறைக்க அண்டை விவசாயிகளுடன் சேர்ந்து விற்கவும்!",
        "base_price": "அடிப்படை விலை (₹/கி.கி)",
        "total_rev": "மொத்த வருவாய் (₹)",
        "best_mkt": "சிறந்த சந்தை",
        "best_profit": "அதிகபட்ச லாபம் (₹)",
        "chart_title": "📈 லாப ஒப்பீடு",
        "table_title": "📋 சிறந்த 10 அருகிலுள்ள சந்தைகள்",
        "map_title": "📍 சந்தை இட வரைபடம்",
        "advice_title": "💡 விற்பனை ஆலோசனை",
        "col_market": "சந்தை / வாங்குபவர்",
        "col_type": "வகை",
        "col_dist": "தூரம் (கி.மீ)",
        "col_rev": "வருவாய் (₹)",
        "col_trans": "போக்குவரத்து (₹)",
        "col_profit": "நிகர லாபம் (₹)",
        "col_pct": "% சிறந்த",
        "adv1_t": "⏰ விற்பனைக்கு சிறந்த நேரம்",
        "adv1_b": "அதிகாலையில் விற்கவும் — மண்டியில் விலை அதிகமாக இருக்கும்.",
        "adv2_t": "🤝 சிறந்த விலை பேசுங்கள்",
        "adv2_b": "2-3 வாங்குபவர்களிடம் ஒரே நேரத்தில் பேசி போட்டி விலைகளை காட்டுங்கள்.",
        "adv3_t": "🚛 போக்குவரத்து குறிப்பு",
        "adv3_b": "அண்டை விவசாயிகளுடன் சேர்ந்து போக்குவரத்து செய்யுங்கள்.",
        "adv4_t": "⭐ தரம் முக்கியம்",
        "adv4_b": "தரம் A மாம்பழம் 15-25% அதிக விலை பெறும்.",
        "live_prices": "📈 இன்றைய விலைகள்",
    },
}

# ── CUSTOM CSS ────────────────────────────────────────────────
st.markdown("""
<style>
/* Hide default streamlit elements */
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 0 !important; padding-bottom: 0 !important;}

/* ── FULL PAGE HEADER ── */
.main-header {
    background: linear-gradient(135deg, #1a2e3a 0%, #2c4a5a 100%);
    padding: 12px 24px 14px;
    text-align: center;
    border-bottom: 3px solid #f5a623;
    margin: -1rem -1rem 0 -1rem;
}
.creator-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(245,166,35,0.15);
    border: 1px solid rgba(245,166,35,0.4);
    border-radius: 20px; padding: 3px 14px;
    font-size: 12px; color: #ffd166; font-weight: 500;
    margin-bottom: 7px;
}
.creator-badge strong { color: #f5a623; font-weight: 800; font-size: 13px; }
.main-header h1 { color: #fff; font-size: 24px; font-weight: 800; margin: 0; }
.main-header .sub { color: #a8c5d8; font-size: 13px; margin-top: 3px; }
.hr-gold { width: 160px; height: 2px;
    background: linear-gradient(90deg, transparent, #f5a623, transparent);
    margin: 7px auto; }
.header-meta { margin-top: 7px; font-size: 11px; color: #7fc8e8; }

/* ── PRICE TICKER ── */
.ticker-box {
    background: #0d1f2d; padding: 8px 16px;
    border-bottom: 2px solid #1e3a4a;
    overflow-x: auto; white-space: nowrap;
    margin: 0 -1rem; font-size: 12px;
}
.ticker-item { display: inline-flex; align-items: center; gap: 5px; margin-right: 18px; }
.ticker-place { color: #7fc8e8; }
.ticker-price { color: #ffd166; font-weight: 800; font-size: 13px; }
.ticker-up { color: #4ade80; }
.ticker-dn { color: #f87171; }
.ticker-lbl { color: #f5a623; font-weight: 700; font-size: 11px;
    text-transform: uppercase; letter-spacing: 1px; margin-right: 10px; }

/* ── STAT CARDS ── */
.stat-card {
    background: #fff; border: 1px solid #e0ece0;
    border-radius: 10px; padding: 14px 16px;
    display: flex; align-items: center; gap: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.stat-icon { font-size: 26px; }
.stat-label { font-size: 11px; color: #5a7a5f; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.4px; }
.stat-val { font-size: 22px; font-weight: 800; line-height: 1.2; }
.sv-blue { color: #1565C0; }
.sv-green { color: #2d6a4f; }
.sv-orange { color: #e67e22; }
.sv-bestgreen { color: #27ae60; }

/* ── SECTION CARDS ── */
.section-card {
    background: #fff; border: 1px solid #e0ece0;
    border-radius: 10px; padding: 16px 18px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}
.section-title {
    font-size: 15px; font-weight: 700; color: #1a2e3a;
    border-bottom: 1px solid #e8f5e9; padding-bottom: 10px;
    margin-bottom: 14px;
}

/* ── ADVICE CARDS ── */
.advice-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.advice-card {
    background: #f8fdf8; border: 1.5px solid #c8e6c9;
    border-radius: 10px; padding: 14px;
}
.advice-title { font-size: 13px; font-weight: 700; color: #2d6a4f; margin-bottom: 5px; }
.advice-body { font-size: 12.5px; color: #5a7a5f; line-height: 1.55; }

/* ── FOOTER ── */
.page-footer {
    background: #1a2e3a; color: #a8c5d8;
    padding: 24px 32px; margin: 16px -1rem -1rem -1rem;
    border-top: 3px solid #f5a623;
    display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;
}
.footer-col h4 { color: #f5a623; font-size: 13px; font-weight: 700; margin-bottom: 8px; }
.footer-col p, .footer-col li { font-size: 12px; color: #7fc8e8; line-height: 1.7; }
.footer-bottom {
    background: #0d1f2d; text-align: center;
    padding: 10px; font-size: 11px; color: #7fc8e8;
    margin: 0 -1rem -1rem -1rem; border-top: 1px solid #1e3a4a;
}
.footer-bottom strong { color: #f5a623; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] { background: #fff !important; border-right: 2px solid #c8e6c9; }
[data-testid="stSidebar"] .stButton > button {
    width: 100%; background: #2c3e50 !important;
    color: white !important; font-weight: 700 !important;
    border: none !important; border-radius: 8px !important;
    padding: 12px !important; font-size: 15px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #1a2e3a !important; transform: translateY(-1px);
}

/* ── METRIC OVERRIDE ── */
[data-testid="stMetric"] {
    background: #fff; border: 1px solid #e0ece0;
    border-radius: 10px; padding: 12px 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

/* ── TABLE STYLING ── */
.profit-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.profit-table th {
    background: #f0f7f0; color: #2d6a4f; font-size: 11px;
    font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px;
    padding: 10px 12px; text-align: left; border-bottom: 2px solid #c8e6c9;
}
.profit-table td { padding: 10px 12px; border-bottom: 1px solid #f0f7f0; vertical-align: middle; }
.profit-table tr:hover td { background: #f8fdf8; }
.profit-val { color: #27ae60; font-weight: 700; }
.rank-gold { background:#FFD700; color:#7a5c00; border-radius:50%;
    width:24px;height:24px;display:inline-flex;align-items:center;justify-content:center;font-weight:800;font-size:12px; }
.rank-silver { background:#C0C0C0; color:#444; border-radius:50%;
    width:24px;height:24px;display:inline-flex;align-items:center;justify-content:center;font-weight:800;font-size:12px; }
.rank-bronze { background:#CD7F32; color:#fff; border-radius:50%;
    width:24px;height:24px;display:inline-flex;align-items:center;justify-content:center;font-weight:800;font-size:12px; }
.rank-n { background:#e8f5e9; color:#2d6a4f; border-radius:50%;
    width:24px;height:24px;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:12px; }
</style>
""", unsafe_allow_html=True)


# ── LOAD DATA ────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(__file__)
    def p(f): return os.path.join(base, f)
    villages   = pd.read_csv(p("Village_data.csv"))
    prices     = pd.read_csv(p("cleaned_price_data.csv"))
    geo        = pd.read_csv(p("cleaned_geo_locations.csv"))
    processing = pd.read_csv(p("cleaned_processing_facilities.csv"))
    pulp       = pd.read_csv(p("Pulp_units_merged_lat_long.csv"))
    pickle_u   = pd.read_csv(p("cleaned_pickle_units.csv"))
    local_exp  = pd.read_csv(p("cleaned_local_export.csv"))
    abroad_exp = pd.read_csv(p("cleaned_abroad_export.csv"))
    for df in [villages, prices, geo, processing, pulp, pickle_u, local_exp, abroad_exp]:
        df.columns = df.columns.str.strip().str.lower()
    return villages, prices, geo, processing, pulp, pickle_u, local_exp, abroad_exp

villages, prices, geo, processing, pulp, pickle_u, local_exp, abroad_exp = load_data()


# ── HELPERS ──────────────────────────────────────────────────
def haversine(la1, lo1, la2, lo2):
    R = 6371
    la1,lo1,la2,lo2 = map(np.radians,[la1,lo1,la2,lo2])
    dlat, dlon = la2-la1, lo2-lo1
    a = np.sin(dlat/2)**2 + np.cos(la1)*np.cos(la2)*np.sin(dlon/2)**2
    return R * 2 * np.arcsin(np.sqrt(a))

def get_road_route(la1, lo1, la2, lo2):
    url = (f"https://router.project-osrm.org/route/v1/driving/"
           f"{lo1},{la1};{lo2},{la2}?overview=full&geometries=geojson")
    try:
        r = requests.get(url, timeout=5)
        d = r.json()
        if "routes" in d and d["routes"]:
            route = d["routes"][0]
            coords = [(c[1], c[0]) for c in route["geometry"]["coordinates"]]
            dist_km = route["distance"] / 1000
            return coords, dist_km
    except Exception:
        pass
    return None, None

ROUTE_COLORS = ["#e74c3c","#3498db","#27ae60","#f39c12","#9b59b6",
                "#1abc9c","#e67e22","#c0392b","#2980b9","#8bc34a"]

CAT_COLORS = {
    "Mandi": "#3498db", "Processing": "#9b59b6", "Pulp": "#f39c12",
    "Pickle": "#e91e63", "Local Export": "#27ae60", "Abroad Export": "#1abc9c"
}

VARIETY_ACCEPT = {
    "Mandi":         ["Banganapalli","Totapuri","Neelam","Rasalu"],
    "Processing":    ["Totapuri","Neelam"],
    "Pulp":          ["Totapuri"],
    "Pickle":        ["Totapuri","Rasalu"],
    "Local Export":  ["Banganapalli"],
    "Abroad Export": ["Banganapalli"],
}
MARGIN_MAP = {
    "Mandi":0, "Processing":0.03, "Pulp":0.04,
    "Pickle":0.025, "Local Export":0.05, "Abroad Export":0.07
}


# ── COMPUTE TOP 10 ───────────────────────────────────────────
def compute_top10(v_lat, v_lon, base_price, qty, variety):
    sources = {
        "Mandi":        (prices,     "place",           "lat",      "long"),
        "Processing":   (processing, "facility_name",   "latitude", "longitude"),
        "Pulp":         (pulp,       "facility name",   "latitude", "longitude"),
        "Pickle":       (pickle_u,   "firm_name",       "latitude", "longitude"),
        "Local Export": (local_exp,  "hub_/_firm_name", "latitude", "longitude"),
        "Abroad Export":(abroad_exp, "place_name",      "latitude", "longitude"),
    }
    results = []
    for cat, (df, name_col, lat_col, lon_col) in sources.items():
        if variety not in VARIETY_ACCEPT[cat]:
            continue
        margin = MARGIN_MAP[cat]
        df_c = df.copy()
        df_c.columns = df_c.columns.str.strip().str.lower()
        name_col_l = name_col.lower()
        lat_col_l  = lat_col.lower()
        lon_col_l  = lon_col.lower()
        for _, row in df_c.iterrows():
            try:
                la = float(row[lat_col_l])
                lo = float(row[lon_col_l])
                nm = str(row[name_col_l])
            except Exception:
                continue
            if np.isnan(la) or np.isnan(lo):
                continue
            dist      = haversine(v_lat, v_lon, la, lo)
            transport = dist * 12 * qty
            revenue   = base_price * (1 + margin) * 100 * qty
            net       = revenue - transport
            results.append({
                "Category": cat, "Name": nm,
                "Distance_km": round(dist, 1),
                "Revenue": round(revenue),
                "Transport": round(transport),
                "Net Profit": round(net),
                "Lat": la, "Lon": lo,
            })

    seen = set()
    deduped = []
    for r in results:
        k = r["Name"] + "|" + r["Category"]
        if k not in seen:
            seen.add(k)
            deduped.append(r)

    df_res = pd.DataFrame(deduped)
    if df_res.empty:
        return df_res
    df_res = df_res.sort_values("Net Profit", ascending=False).head(10).reset_index(drop=True)
    df_res["Rank"] = df_res.index + 1
    return df_res


# ── RENDER HEADER ────────────────────────────────────────────
def render_header(L):
    st.markdown(f"""
    <div class="main-header">
      <div class="creator-badge">
        ● &nbsp; Developed by <strong>S.R.L. Keerthi</strong> &nbsp; ●
      </div>
      <h1>🌿 {L['title']}</h1>
      <div class="sub">{L['subtitle']}</div>
      <div class="hr-gold"></div>
      <div class="header-meta">
        🏛️ Agricultural Data Science Project &nbsp;·&nbsp;
        📅 2025–26 &nbsp;·&nbsp;
        🌾 Andhra Pradesh Mango Value Chain
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── RENDER PRICE TICKER ──────────────────────────────────────
def render_ticker(L):
    items_html = ""
    for _, p in prices.iterrows():
        today = float(p.get("today_price(rs/kg)", 0))
        yest  = float(p.get("yesterday_price(rs/kg)", 0))
        diff  = today - yest
        arrow = "▲" if diff >= 0 else "▼"
        cls   = "ticker-up" if diff >= 0 else "ticker-dn"
        place = str(p.get("place",""))[:22]
        items_html += f"""
        <span class="ticker-item">
          <span class="ticker-place">{place}</span>
          <span class="ticker-price">₹{today}/kg</span>
          <span class="{cls}">{arrow}{abs(diff):.0f}</span>
        </span>
        <span style="color:#2c4a5a;margin-right:6px">|</span>"""
    st.markdown(f"""
    <div class="ticker-box">
      <span class="ticker-lbl">{L['live_prices']}</span>
      {items_html}
    </div>
    """, unsafe_allow_html=True)


# ── RENDER STAT CARDS ────────────────────────────────────────
def render_stat_cards(L, base_price, best_row, qty):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="stat-card">
          <span class="stat-icon">📊</span>
          <div><div class="stat-label">{L['base_price']}</div>
          <div class="stat-val sv-blue">{base_price}</div></div></div>""",
          unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="stat-card">
          <span class="stat-icon">💰</span>
          <div><div class="stat-label">{L['total_rev']}</div>
          <div class="stat-val sv-green">{best_row['Revenue']:,}</div></div></div>""",
          unsafe_allow_html=True)
    with c3:
        short_name = best_row['Name'][:20] + ("…" if len(best_row['Name'])>20 else "")
        st.markdown(f"""<div class="stat-card">
          <span class="stat-icon">🏆</span>
          <div><div class="stat-label">{L['best_mkt']}</div>
          <div class="stat-val sv-orange" style="font-size:14px;line-height:1.3">{short_name}</div></div></div>""",
          unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="stat-card">
          <span class="stat-icon">🌿</span>
          <div><div class="stat-label">{L['best_profit']}</div>
          <div class="stat-val sv-bestgreen">{best_row['Net Profit']:,}</div></div></div>""",
          unsafe_allow_html=True)


# ── RENDER BAR CHART ─────────────────────────────────────────
def render_bar_chart(df, L):
    st.markdown(f'<div class="section-card"><div class="section-title">{L["chart_title"]}</div>',
                unsafe_allow_html=True)
    colors = ["#27ae60" if i == 0 else "#52b788" for i in range(len(df))]
    fig = go.Figure(go.Bar(
        x=df["Name"].str[:25],
        y=df["Net Profit"],
        marker_color=colors,
        marker_line_color="#1a2e3a",
        marker_line_width=0.8,
        text=[f"₹{v:,}" for v in df["Net Profit"]],
        textposition="outside",
        textfont=dict(size=11),
    ))
    fig.update_layout(
        height=360,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=20, t=10, b=80),
        xaxis=dict(tickangle=-30, tickfont=dict(size=11),
                   gridcolor="#f0f7f0"),
        yaxis=dict(tickprefix="₹", tickformat=",",
                   gridcolor="#f0f7f0", gridwidth=1),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ── RENDER TABLE ─────────────────────────────────────────────
def render_table(df, L):
    max_net = df["Net Profit"].max()
    rank_html = {1: "rank-gold", 2: "rank-silver", 3: "rank-bronze"}

    rows = ""
    for _, r in df.iterrows():
        rnk    = r["Rank"]
        rclass = rank_html.get(rnk, "rank-n")
        pct    = round(r["Net Profit"] / max_net * 100)
        bar_color = "#27ae60" if rnk == 1 else "#52b788"
        cat_color = CAT_COLORS.get(r["Category"], "#888")
        rows += f"""
        <tr>
          <td><span class="{rclass}">{rnk}</span></td>
          <td><b>{r['Name']}</b></td>
          <td><span style="background:{cat_color}20;color:{cat_color};
              padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700">
              {r['Category']}</span></td>
          <td>{r['Distance_km']}</td>
          <td>₹{r['Revenue']:,}</td>
          <td>₹{r['Transport']:,}</td>
          <td><b class="profit-val">₹{r['Net Profit']:,}</b></td>
          <td>
            <div style="display:flex;align-items:center;gap:6px">
              <div style="flex:1;min-width:50px;height:7px;background:#e8f5e9;
                   border-radius:4px;overflow:hidden">
                <div style="width:{pct}%;height:7px;background:{bar_color};
                     border-radius:4px"></div>
              </div>
              <span style="font-size:11px;color:#5a7a5f">{pct}%</span>
            </div>
          </td>
        </tr>"""

    st.markdown(f"""
    <div class="section-card">
      <div class="section-title">{L['table_title']}</div>
      <div style="overflow-x:auto">
      <table class="profit-table">
        <thead><tr>
          <th>#</th>
          <th>{L['col_market']}</th>
          <th>{L['col_type']}</th>
          <th>{L['col_dist']}</th>
          <th>{L['col_rev']}</th>
          <th>{L['col_trans']}</th>
          <th>{L['col_profit']}</th>
          <th>{L['col_pct']}</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── RENDER MAP ───────────────────────────────────────────────
def render_map(df, v_lat, v_lon, L):
    st.markdown(f'<div class="section-card"><div class="section-title">{L["map_title"]}</div>',
                unsafe_allow_html=True)

    m = folium.Map(location=[v_lat, v_lon], zoom_start=9,
                   tiles="OpenStreetMap")

    # Village marker
    folium.Marker(
        [v_lat, v_lon],
        popup=folium.Popup("<b>Your Village</b>", max_width=200),
        icon=folium.DivIcon(html="""
          <div style="background:#1a2e3a;color:#fff;padding:4px 10px;
               border-radius:20px;font-size:12px;font-weight:800;
               white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,0.4)">
            ● Village
          </div>""", icon_size=(80,28), icon_anchor=(40,14))
    ).add_to(m)

    # Market markers + routes
    for i, row in df.iterrows():
        color = ROUTE_COLORS[i % len(ROUTE_COLORS)]
        rank  = row["Rank"]
        label = "🏆 " + row["Name"][:20] if rank == 1 else row["Name"][:22]

        # Marker
        folium.Marker(
            [row["Lat"], row["Lon"]],
            popup=folium.Popup(
                f"<b>{'🏆 ' if rank==1 else ''}#{rank} {row['Name']}</b><br>"
                f"Type: {row['Category']}<br>"
                f"Distance: {row['Distance_km']} km<br>"
                f"Net Profit: ₹{row['Net Profit']:,}",
                max_width=250
            ),
            icon=folium.DivIcon(
                html=f"""<div style="display:flex;flex-direction:column;align-items:center">
                  <div style="background:{color};color:#fff;padding:4px 10px;
                       border-radius:20px;font-size:11px;font-weight:700;
                       white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,0.3);
                       max-width:170px;overflow:hidden;text-overflow:ellipsis">
                    {label[:26]}
                  </div>
                  <div style="width:2px;height:8px;background:{color}"></div>
                  <div style="width:8px;height:8px;border-radius:50%;background:{color}"></div>
                </div>""",
                icon_size=(170, 48), icon_anchor=(85, 48)
            )
        ).add_to(m)

        # Road route
        coords, road_km = get_road_route(v_lat, v_lon, row["Lat"], row["Lon"])
        if coords:
            folium.PolyLine(
                coords,
                color=color,
                weight=5 if rank == 1 else 3,
                opacity=0.9 if rank == 1 else 0.65,
                dash_array=None if rank == 1 else "6 5",
                tooltip=f"{row['Name']} — Road: {road_km:.1f} km | Air: {row['Distance_km']} km"
            ).add_to(m)
        else:
            folium.PolyLine(
                [[v_lat, v_lon], [row["Lat"], row["Lon"]]],
                color=color, weight=2, opacity=0.5, dash_array="4 8"
            ).add_to(m)

    st_folium(m, width=None, height=420, returned_objects=[])
    st.markdown("</div>", unsafe_allow_html=True)


# ── RENDER ADVICE ────────────────────────────────────────────
def render_advice(L):
    st.markdown(f"""
    <div class="section-card">
      <div class="section-title">{L['advice_title']}</div>
      <div class="advice-grid">
        <div class="advice-card">
          <div class="advice-title">{L['adv1_t']}</div>
          <div class="advice-body">{L['adv1_b']}</div>
        </div>
        <div class="advice-card">
          <div class="advice-title">{L['adv2_t']}</div>
          <div class="advice-body">{L['adv2_b']}</div>
        </div>
        <div class="advice-card">
          <div class="advice-title">{L['adv3_t']}</div>
          <div class="advice-body">{L['adv3_b']}</div>
        </div>
        <div class="advice-card">
          <div class="advice-title">{L['adv4_t']}</div>
          <div class="advice-body">{L['adv4_b']}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── RENDER FOOTER ────────────────────────────────────────────
def render_footer():
    st.markdown("""
    <div class="page-footer">
      <div class="footer-col">
        <h4>👨‍💻 About This Project</h4>
        <p>A smart agricultural decision support system that helps mango farmers identify the most profitable markets by analysing real-time price data, transport costs, and market types across Andhra Pradesh.</p>
      </div>
      <div class="footer-col">
        <h4>🛠️ Technologies Used</h4>
        <p>Python · Pandas · NumPy<br>
        Streamlit · Folium · Leaflet.js<br>
        Plotly · OSRM Routing API<br>
        Multilingual UI (EN / TE / HI / TA)<br>
        Haversine Distance Algorithm</p>
      </div>
      <div class="footer-col">
        <h4>📚 Project Details</h4>
        <p>Developer: S.R.L. Keerthi<br>
        Domain: Agri-Tech / Data Science<br>
        Region: Andhra Pradesh, India<br>
        Dataset: 704 Villages · 99+ Markets<br>
        Year: 2025–26</p>
      </div>
    </div>
    <div class="footer-bottom">
      Developed with ❤️ by <strong>S.R.L. Keerthi</strong> &nbsp;·&nbsp;
      Farmer Profit Intelligence System &nbsp;·&nbsp;
      All Rights Reserved © 2026
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  MAIN APP
# ════════════════════════════════════════════════════════════
def main():

    # ── SIDEBAR ──────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🌐 Language / భాష / भाषा")
        lang_choice = st.selectbox("", list(LANGS.keys()), label_visibility="collapsed")
        L = LANGS[lang_choice]

        st.markdown(f"---\n### {L['panel']}")

        # Village dropdown grouped by Mandal
        mandal_groups = {}
        for _, row in villages.iterrows():
            m  = str(row.get("mandal", row.get("Mandal",""))).strip()
            gp = str(row.get("gram panchayat", row.get("Gram Panchayat",""))).strip()
            if m not in mandal_groups:
                mandal_groups[m] = []
            mandal_groups[m].append(gp)

        all_villages = sorted(
            [gp for gps in mandal_groups.values() for gp in gps]
        )
        st.markdown(f"**{L['village']}**")
        selected_village = st.selectbox("", [""] + all_villages,
                                        label_visibility="collapsed")

        st.markdown(f"**{L['variety']}**")
        variety = st.radio(
            "", ["Banganapalli 🥭 Export", "Totapuri 🥭 Processing",
                 "Neelam 🥭 Mandi",       "Rasalu 🥭 Pickle"],
            label_visibility="collapsed"
        )
        variety = variety.split(" ")[0]  # extract just the variety name

        st.markdown(f"**{L['qty']}**")
        qty = st.number_input("", min_value=1, value=10, step=1,
                              label_visibility="collapsed")

        run = st.button(L["run"], use_container_width=True)

        st.markdown(f"""
        <div style="background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;
             padding:10px 12px;font-size:12px;color:#78350f;line-height:1.55;margin-top:8px">
          {L['tip']}
        </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("""
        <div style="text-align:center;font-size:11px;color:#5a7a5f">
          ⚡ <b>S.R.L. Keerthi</b><br>
          Agricultural Data Science<br>2025–26
        </div>""", unsafe_allow_html=True)

    # ── HERO IMAGE ───────────────────────────────────────────
    L = LANGS[lang_choice]
    render_header(L)
    render_ticker(L)

    # Show hero image if available
    hero_path = os.path.join(os.path.dirname(__file__), "mango_farm1.jpg")
    if os.path.exists(hero_path):
        st.image(hero_path, use_container_width=True)
    else:
        # Try webp
        webp_path = os.path.join(os.path.dirname(__file__), "mango_dashboard.webp")
        if os.path.exists(webp_path):
            st.image(webp_path, use_container_width=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── RESULTS ──────────────────────────────────────────────
    if run:
        if not selected_village:
            st.warning("⚠️ Please select your village first!")
            return

        # Find village coordinates
        v_col_gp  = "gram panchayat" if "gram panchayat" in villages.columns else "Gram Panchayat"
        v_col_lat = "latitude" if "latitude" in villages.columns else "Latitude"
        v_col_lon = "longitude" if "longitude" in villages.columns else "Longitude"
        villages.columns = villages.columns.str.strip().str.lower()
        v_row = villages[villages["gram panchayat"] == selected_village]
        if v_row.empty:
            st.error("Village not found in dataset.")
            return
        v_lat = float(v_row.iloc[0]["latitude"])
        v_lon = float(v_row.iloc[0]["longitude"])

        # Find nearest mandi base price
        prices.columns = prices.columns.str.strip().str.lower()
        base_price = 30
        nearest_dist = float("inf")
        for _, p in prices.iterrows():
            d = haversine(v_lat, v_lon, float(p["lat"]), float(p["long"]))
            if d < nearest_dist:
                nearest_dist = d
                base_price = float(p["today_price(rs/kg)"])

        with st.spinner(f"🔍 {L.get('loading','Calculating best markets...')}"):
            df_top10 = compute_top10(v_lat, v_lon, base_price, qty, variety)

        if df_top10.empty:
            st.warning("No markets found for this variety. Try a different variety.")
            return

        best = df_top10.iloc[0]

        # ── STAT CARDS ──
        render_stat_cards(L, base_price, best, qty)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── TABS ──
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Profit Comparison",
            "📋 Top 10 Markets",
            "📍 Market Map",
            "💡 Selling Advice"
        ])

        with tab1:
            render_bar_chart(df_top10, L)

        with tab2:
            render_table(df_top10, L)

        with tab3:
            render_map(df_top10, v_lat, v_lon, L)

        with tab4:
            render_advice(L)

    else:
        # Welcome screen
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#5a7a5f">
          <div style="font-size:70px;animation:none">🥭</div>
          <h2 style="font-size:22px;font-weight:800;color:#1a2e3a;margin:14px 0 8px">
            Welcome, Mango Farmer!
          </h2>
          <p style="font-size:14px;line-height:1.65;max-width:420px;margin:0 auto">
            Select your <b>village</b> and <b>mango variety</b> from the sidebar,
            then click <b>Run Smart Analysis</b> to discover the most profitable
            market for your harvest across Andhra Pradesh.
          </p>
          <div style="display:flex;justify-content:center;gap:14px;margin-top:24px;flex-wrap:wrap">
            <div style="background:#fff;border:1.5px solid #c8e6c9;border-radius:12px;padding:16px 20px;min-width:130px">
              <div style="font-size:28px">📍</div>
              <b style="color:#2d6a4f;font-size:13px">Pick Village</b><br>
              <span style="font-size:11px;color:#5a7a5f">Find nearby markets</span>
            </div>
            <div style="background:#fff;border:1.5px solid #c8e6c9;border-radius:12px;padding:16px 20px;min-width:130px">
              <div style="font-size:28px">🥭</div>
              <b style="color:#2d6a4f;font-size:13px">Select Variety</b><br>
              <span style="font-size:11px;color:#5a7a5f">Match right buyers</span>
            </div>
            <div style="background:#fff;border:1.5px solid #c8e6c9;border-radius:12px;padding:16px 20px;min-width:130px">
              <div style="font-size:28px">💰</div>
              <b style="color:#2d6a4f;font-size:13px">See Profit</b><br>
              <span style="font-size:11px;color:#5a7a5f">Compare all options</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    render_footer()


if __name__ == "__main__":
    main()
