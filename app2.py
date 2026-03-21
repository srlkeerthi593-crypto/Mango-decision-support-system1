# ============================================================
# 🥭 FARMER PROFIT INTELLIGENCE SYSTEM (FAST + DASHBOARD UI)
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import folium
import requests
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(layout="wide")

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align:center;'>🥭 Farmer Profit Intelligence System</h1>
<p style='text-align:center;'>Smart Mango Marketing Decision Engine</p>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    villages = pd.read_csv("Village data.csv")
    prices = pd.read_csv("cleaned_price_data.csv")
    geo = pd.read_csv("cleaned_geo_locations.csv")

    for df in [villages, prices, geo]:
        df.columns = df.columns.str.strip().str.lower()

    return villages, prices, geo

villages, prices, geo = load_data()

# ---------------- HELPERS ----------------
def detect_lat_lon(df):
    lat, lon = None, None
    for c in df.columns:
        if "lat" in c: lat = c
        if "lon" in c: lon = c
    return lat, lon

def detect_name(df):
    for col in ["name","place","market"]:
        if col in df.columns:
            return col
    return df.columns[0]

def fast_dist(lat1, lon1, lat2, lon2):
    return np.sqrt((lat1-lat2)**2 + (lon1-lon2)**2)

def get_route(lat1, lon1, lat2, lon2):
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    try:
        r = requests.get(url).json()
        dist = r["routes"][0]["distance"]/1000
        route = r["routes"][0]["geometry"]["coordinates"]
        route = [(c[1],c[0]) for c in route]
        return route, dist
    except:
        return None, None

# ---------------- SIDEBAR ----------------
st.sidebar.header("📊 Analysis Control Panel")

farmer_name = st.sidebar.text_input("Enter Farmer Name")
village_name = st.sidebar.selectbox("Enter Village Name",
                                   sorted(villages[detect_name(villages)].unique()))

variety = st.sidebar.selectbox("Select Mango Variety",
                              ["Banganapalli","Totapuri","Neelam","Rasalu"])

run = st.sidebar.button("Run Smart Analysis")

# ---------------- MAIN ----------------
if run:

    st.success(f"🙏 Namaste {farmer_name}")

    v_row = villages[villages[detect_name(villages)]==village_name].iloc[0]
    lat_v, lon_v = v_row[detect_lat_lon(villages)[0]], v_row[detect_lat_lon(villages)[1]]

    data = prices.merge(geo, on="market", how="left")
    lat_m, lon_m = detect_lat_lon(data)

    # FAST FILTER
    data["fast_dist"] = data.apply(
        lambda r: fast_dist(lat_v, lon_v, r[lat_m], r[lon_m]), axis=1
    )

    data = data.sort_values("fast_dist").head(10)

    results = []

    for _, row in data.iterrows():
        price = row["today_price(rs/kg)"]

        dist = row["fast_dist"] * 111  # approx km

        revenue = price * 100 * 10
        transport = dist * 12 * 10
        net = revenue - transport

        results.append({
            "Name": row["market"],
            "Distance": round(dist,2),
            "Net": round(net,2),
            "Price": price,
            "Lat": row[lat_m],
            "Lon": row[lon_m]
        })

    df = pd.DataFrame(results).sort_values("Net", ascending=False)

    best = df.iloc[0]

    # ---------------- METRICS ----------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Base Price (₹/kg)", f"{best['Price']}")
    col2.metric("Total Revenue (₹)", f"{int(best['Price']*100*10):,}")
    col3.metric("Best Location", best["Name"])
    col4.metric("Best Profit (₹)", f"{int(best['Net']):,}")

    # ---------------- BAR CHART ----------------
    st.subheader("📊 Profit Comparison")

    fig = px.bar(df.head(10), x="Name", y="Net", color="Net")
    st.plotly_chart(fig, use_container_width=True)

    # ---------------- TABLE ----------------
    st.subheader("📋 Top Locations")

    st.dataframe(df.head(10)[["Name","Distance","Net"]])

    # ---------------- MAP (ONLY TOP 3 REAL ROUTES) ----------------
    st.subheader("🗺️ Market Map")

    m = folium.Map(location=[lat_v, lon_v], zoom_start=9)

    folium.Marker([lat_v, lon_v], popup="Village",
                  icon=folium.Icon(color="black")).add_to(m)

    top3 = df.head(3)

    colors = ["green","orange","red"]

    for i, row in top3.iterrows():

        folium.Marker([row["Lat"], row["Lon"]],
                      popup=row["Name"],
                      icon=folium.Icon(color=colors[i])).add_to(m)

        route, _ = get_route(lat_v, lon_v, row["Lat"], row["Lon"])

        if route:
            folium.PolyLine(route, color=colors[i], weight=5).add_to(m)

    st_folium(m, width=1100, height=500)
