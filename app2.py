# ============================================================
# 🥭 FARMER’S MANGO PROFIT NAVIGATOR (FINAL PRO VERSION)
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import folium
import requests
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

# ---------------- BACKGROUND UI ----------------
def set_background():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1592928302636-c83cf1c0b6c7");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }

        .stApp::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.55);
            z-index: -1;
        }

        .glass {
            background: rgba(255,255,255,0.15);
            padding: 15px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            margin-bottom: 15px;
        }

        section[data-testid="stSidebar"] {
            background: rgba(0,0,0,0.7) !important;
        }

        h1, h2, h3, p {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_background()

# ---------------- TITLE ----------------
st.markdown("""
<h1 style='text-align:center;'>🥭 Mango Profit Navigator</h1>
<p style='text-align:center;'>Smart Decisions for Better Farming</p>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    villages = pd.read_csv("Village data.csv")
    prices = pd.read_csv("cleaned_price_data.csv")
    geo = pd.read_csv("cleaned_geo_locations.csv")
    processing = pd.read_csv("cleaned_processing_facilities.csv")
    pulp = pd.read_csv("Pulp_units_merged_lat_long.csv")
    pickle_units = pd.read_csv("cleaned_pickle_units.csv")
    local_export = pd.read_csv("cleaned_local_export.csv")
    abroad_export = pd.read_csv("cleaned_abroad_export.csv")

    for df in [villages, prices, geo, processing,
               pulp, pickle_units, local_export, abroad_export]:
        df.columns = df.columns.str.strip().str.lower()

    return villages, prices, geo, processing, pulp, pickle_units, local_export, abroad_export

villages, prices, geo, processing, pulp, pickle_units, local_export, abroad_export = load_data()

# ---------------- HELPERS ----------------
def detect_lat_lon(df):
    lat, lon = None, None
    for c in df.columns:
        if "lat" in c:
            lat = c
        if "lon" in c or "long" in c:
            lon = c
    return lat, lon

def detect_name(df):
    for col in ["name","place","market","unit_name","company_name"]:
        if col in df.columns:
            return col
    return df.columns[0]

# ---------------- ROAD ROUTE ----------------
def get_road_route(lat1, lon1, lat2, lon2):
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    try:
        res = requests.get(url).json()
        route = res["routes"][0]["geometry"]["coordinates"]
        distance = res["routes"][0]["distance"] / 1000
        route_coords = [(c[1], c[0]) for c in route]
        return route_coords, distance
    except:
        return None, None

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("<h2 style='color:white;'>👨‍🌾 Farmer Input</h2>", unsafe_allow_html=True)

selected_village = st.sidebar.selectbox(
    "Select Your Village 🏡",
    sorted(villages[detect_name(villages)].unique())
)

variety = st.sidebar.selectbox(
    "Select Mango Variety 🥭",
    ["Banganapalli","Totapuri","Neelam","Rasalu"]
)

quantity_qtl = st.sidebar.number_input("Quantity (Quintals) 📦", min_value=1, value=10)

run = st.sidebar.button("🚀 Show Best Options")

# ---------------- MAIN ----------------
if run:

    village_row = villages[villages[detect_name(villages)] == selected_village].iloc[0]
    lat_v, lon_v = village_row[detect_lat_lon(villages)[0]], village_row[detect_lat_lon(villages)[1]]

    mandi_data = prices.merge(geo, on="market", how="left")
    lat_m, lon_m = detect_lat_lon(mandi_data)
    mandi_data = mandi_data.dropna(subset=[lat_m, lon_m])

    # base price (₹/kg)
    base_price = mandi_data.iloc[0]["today_price(rs/kg)"]

    results = []

    datasets = [mandi_data, processing, pulp, pickle_units, local_export, abroad_export]

    for df in datasets:
        lat, lon = detect_lat_lon(df)
        name_col = detect_name(df)

        if lat is None:
            continue

        for _, row in df.iterrows():

            if pd.notnull(row[lat]) and pd.notnull(row[lon]):

                route, dist = get_road_route(lat_v, lon_v, row[lat], row[lon])

                if dist is None:
                    continue

                transport = dist * 12 * quantity_qtl

                # YOUR PRICE LOGIC (₹/kg based)
                revenue = base_price * (1.05) * 100 * quantity_qtl

                net = revenue - transport

                results.append({
                    "Name": row[name_col],
                    "Distance": round(dist, 2),
                    "Net": round(net, 2),
                    "Lat": row[lat],
                    "Lon": row[lon],
                    "Route": route
                })

    df = pd.DataFrame(results).drop_duplicates(subset=["Name"])

    # ---------------- TOP 3 ----------------
    df = df.sort_values("Net", ascending=False).head(3).reset_index(drop=True)

    colors = ["green", "orange", "red"]
    df["Color"] = colors[:len(df)]

    # ---------------- DISPLAY ----------------
    st.subheader("🌱 Top 3 Best Selling Options")

    for i, row in df.iterrows():
        st.markdown(
            f"""
            <div class="glass" style="border-left: 10px solid {row['Color']}">
                <h3>#{i+1} {row['Name']}</h3>
                <p>💰 Profit: ₹{row['Net']}</p>
                <p>📍 Distance: {row['Distance']} km</p>
                <p>🥭 Price: ₹{base_price}/kg</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------------- MAP ----------------
    st.subheader("🗺️ Real Road Routes")

    m = folium.Map(location=[lat_v, lon_v], zoom_start=9)

    folium.Marker(
        [lat_v, lon_v],
        popup="🏡 Your Village",
        icon=folium.Icon(color="black")
    ).add_to(m)

    for _, row in df.iterrows():

        folium.Marker(
            [row["Lat"], row["Lon"]],
            popup=row["Name"],
            icon=folium.Icon(color=row["Color"])
        ).add_to(m)

        if row["Route"] is not None:
            folium.PolyLine(
                row["Route"],
                color=row["Color"],
                weight=5
            ).add_to(m)

    st_folium(m, width=1100, height=600)
