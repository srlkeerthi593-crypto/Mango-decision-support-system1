# ============================================================
# 🥭 FARMER’S MANGO PROFIT NAVIGATOR (FINAL CLEAN VERSION)
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import folium
import requests
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")

# ---------------- BACKGROUND ----------------
def set_bg():
    st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1592928302636-c83cf1c0b6c7");
        background-size: cover;
        background-position: center;
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

set_bg()

st.title("🥭 Farmer’s Mango Profit Navigator")
st.subheader("🧭 Find the Best Place. Earn Maximum Profit.")

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
        if "lat" in c: lat = c
        if "lon" in c or "long" in c: lon = c
    return lat, lon

def detect_name(df):
    for col in ["name","place","market","unit_name","company_name"]:
        if col in df.columns:
            return col
    return df.columns[0]

# ----------- REAL ROAD ROUTE (OSRM) -----------
def get_road_data(lat1, lon1, lat2, lon2):
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    try:
        res = requests.get(url).json()
        route = res["routes"][0]["geometry"]["coordinates"]
        dist = res["routes"][0]["distance"]/1000
        route = [(c[1],c[0]) for c in route]
        return route, dist
    except:
        return None, None

# ---------------- SIDEBAR ----------------
st.sidebar.header("👨‍🌾 Farmer Details 🥭")

farmer_name = st.sidebar.text_input("Farmer Name 🥭")

selected_village = st.sidebar.selectbox(
    "Select Village 🏡",
    sorted(villages[detect_name(villages)].unique())
)

variety = st.sidebar.selectbox(
    "Select Variety 🥭",
    ["Banganapalli","Totapuri","Neelam","Rasalu"]
)

quantity_qtl = st.sidebar.number_input("Quantity (Quintals) 📦", min_value=1, value=10)

if "run" not in st.session_state:
    st.session_state.run = False

if st.sidebar.button("🚀 Run Smart Analysis 🥭"):
    st.session_state.run = True

# ---------------- MAIN ----------------
if st.session_state.run:

    st.markdown(f"## 🙏🥭 Namaste **{farmer_name}**")

    village_row = villages[villages[detect_name(villages)]==selected_village].iloc[0]
    v_lat, v_lon = village_row[detect_lat_lon(villages)[0]], village_row[detect_lat_lon(villages)[1]]

    mandi_data = prices.merge(geo,on="market",how="left")
    lat_m, lon_m = detect_lat_lon(mandi_data)
    mandi_data = mandi_data.dropna(subset=[lat_m,lon_m])

    # price per kg
    base_price = mandi_data.iloc[0]["today_price(rs/kg)"]

    results=[]

    category_dfs = [mandi_data, processing, pulp, pickle_units, local_export, abroad_export]

    # -------- PERFORMANCE OPTIMIZATION (only first 20 points) --------
    for df in category_dfs:
        lat,lon = detect_lat_lon(df)
        name_col = detect_name(df)
        if lat is None: continue

        df_sample = df.head(20)

        for _,row in df_sample.iterrows():
            if pd.notnull(row[lat]) and pd.notnull(row[lon]):

                route, dist = get_road_data(v_lat, v_lon, row[lat], row[lon])

                if dist is None: continue

                transport = dist * 12 * quantity_qtl
                revenue = base_price*(1.05)*100*quantity_qtl
                net = revenue - transport

                results.append({
                    "Name":row[name_col],
                    "Distance":round(dist,2),
                    "Net":round(net,2),
                    "Lat":row[lat],
                    "Lon":row[lon],
                    "Route":route
                })

    df_top = pd.DataFrame(results).drop_duplicates(subset=["Name"])
    df_top = df_top.sort_values("Net",ascending=False).head(3).reset_index(drop=True)

    colors = ["green","orange","red"]
    df_top["Color"] = colors[:len(df_top)]

    # ---------------- DISPLAY ----------------
    st.subheader("🌱 Top 3 Best Options")

    for i,row in df_top.iterrows():
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.15);padding:15px;border-radius:10px;
                    border-left:10px solid {row['Color']};margin-bottom:10px;">
            <h3>#{i+1} {row['Name']}</h3>
            <p>💰 Profit: ₹{row['Net']}</p>
            <p>📍 Distance: {row['Distance']} km</p>
            <p>🥭 Price: ₹{base_price}/kg</p>
        </div>
        """, unsafe_allow_html=True)

    # ---------------- MAP ----------------
    st.subheader("🗺️ Real Road Routes")

    m = folium.Map(location=[v_lat,v_lon],zoom_start=9)

    folium.Marker([v_lat,v_lon],
                  popup="Your Village",
                  icon=folium.Icon(color="black")).add_to(m)

    for _,row in df_top.iterrows():

        folium.Marker(
            [row["Lat"],row["Lon"]],
            popup=row["Name"],
            icon=folium.Icon(color=row["Color"])
        ).add_to(m)

        if row["Route"]:
            folium.PolyLine(
                row["Route"],
                color=row["Color"],
                weight=5
            ).add_to(m)

    st_folium(m,width=1100,height=600)
