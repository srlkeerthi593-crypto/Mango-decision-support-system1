# ============================================================
# 🥭 FARMER’S MANGO PROFIT NAVIGATOR (FAST VERSION)
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import folium
import requests
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

# ---------------- BACKGROUND ----------------
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1592928302636-c83cf1c0b6c7");
    background-size: cover;
    background-attachment: fixed;
}
.stApp::before {
    content:"";
    position:fixed;
    width:100%;
    height:100%;
    background:rgba(0,0,0,0.55);
    z-index:-1;
}
h1,h2,h3,p {color:white !important;}
</style>
""", unsafe_allow_html=True)

st.title("🥭 Mango Profit Navigator")
st.subheader("Smart Selling for Farmers")

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
        if "lon" in c or "long" in c: lon = c
    return lat, lon

def detect_name(df):
    for col in ["name","place","market"]:
        if col in df.columns:
            return col
    return df.columns[0]

# FAST DISTANCE (for filtering only)
def fast_dist(lat1, lon1, lat2, lon2):
    return np.sqrt((lat1-lat2)**2 + (lon1-lon2)**2)

# REAL ROAD ROUTE (only few calls)
def get_route(lat1, lon1, lat2, lon2):
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    try:
        r = requests.get(url).json()
        route = r["routes"][0]["geometry"]["coordinates"]
        dist = r["routes"][0]["distance"]/1000
        route = [(c[1],c[0]) for c in route]
        return route, dist
    except:
        return None, None

# ---------------- SIDEBAR ----------------
st.sidebar.header("👨‍🌾 Farmer Input")

farmer_name = st.sidebar.text_input("Farmer Name")

selected_village = st.sidebar.selectbox(
    "Select Village",
    sorted(villages[detect_name(villages)].unique())
)

quantity = st.sidebar.number_input("Quantity (Quintals)", 1, 100, 10)

run = st.sidebar.button("🚀 Run")

# ---------------- MAIN ----------------
if run:

    st.success(f"🙏 Namaste {farmer_name}")

    v_row = villages[villages[detect_name(villages)]==selected_village].iloc[0]
    lat_v, lon_v = v_row[detect_lat_lon(villages)[0]], v_row[detect_lat_lon(villages)[1]]

    data = prices.merge(geo, on="market", how="left")
    lat_m, lon_m = detect_lat_lon(data)

    # FAST FILTER (IMPORTANT FOR SPEED)
    data["fast_dist"] = data.apply(
        lambda r: fast_dist(lat_v, lon_v, r[lat_m], r[lon_m]), axis=1
    )

    data = data.sort_values("fast_dist").head(5)  # only 5 API calls

    results = []

    for _, row in data.iterrows():

        route, dist = get_route(lat_v, lon_v, row[lat_m], row[lon_m])

        if dist is None:
            continue

        price = row["today_price(rs/kg)"]

        revenue = price * 100 * quantity
        transport = dist * 12 * quantity
        net = revenue - transport

        results.append({
            "Name": row["market"],
            "Price": price,
            "Distance": dist,
            "Net": net,
            "Lat": row[lat_m],
            "Lon": row[lon_m],
            "Route": route
        })

    df = pd.DataFrame(results).sort_values("Net", ascending=False).head(3)

    colors = ["green","orange","red"]
    df["Color"] = colors[:len(df)]

    # ---------------- PRICE DISPLAY (IMPORTANT ADDITION) ----------------
    st.markdown("## 💰 Current Mango Price")

    if len(df) > 0:
        st.markdown(f"""
        <div style="background:#27ae60;padding:15px;border-radius:10px;">
        <h2>₹{df.iloc[0]['Price']} per kg</h2>
        </div>
        """, unsafe_allow_html=True)

    # ---------------- TOP 3 ----------------
    st.markdown("## 🌱 Best Selling Options")

    for i, row in df.iterrows():
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.15);padding:15px;border-radius:10px;
                    border-left:10px solid {row['Color']};margin-bottom:10px;">
            <h3>#{i+1} {row['Name']}</h3>
            <p>💰 Profit: ₹{int(row['Net'])}</p>
            <p>📍 Distance: {round(row['Distance'],2)} km</p>
            <p>🥭 Price: ₹{row['Price']}/kg</p>
        </div>
        """, unsafe_allow_html=True)

    # ---------------- MAP ----------------
    m = folium.Map(location=[lat_v, lon_v], zoom_start=9)

    folium.Marker([lat_v, lon_v], popup="Village",
                  icon=folium.Icon(color="black")).add_to(m)

    for _, row in df.iterrows():
        folium.Marker([row["Lat"], row["Lon"]],
                      popup=row["Name"],
                      icon=folium.Icon(color=row["Color"])).add_to(m)

        if row["Route"]:
            folium.PolyLine(row["Route"], color=row["Color"], weight=5).add_to(m)

    st_folium(m, width=1100, height=600)
