# ============================================================
# 🥭 FARMER PROFIT INTELLIGENCE SYSTEM 🥭
# Smart Mango Marketing Decision Engine
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

# ---------------- HEADER IMAGE ----------------
st.markdown("""
<style>
.header {
    background-image: url('mango farm1.jpg');
    background-size: cover;
    padding: 60px;
    border-radius: 12px;
    text-align: center;
    color: white;
}
.metric-box {
    background-color: #f2f2f2;
    padding: 15px;
    border-radius: 10px;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h1>🥭 Farmer Profit Intelligence System</h1>
    <h3>Smart Mango Marketing Decision Engine</h3>
</div>
""", unsafe_allow_html=True)

# ---------------- MULTILINGUAL ----------------
language = st.sidebar.selectbox("🌐 Language", ["English", "తెలుగు", "हिंदी"])

text = {
    "English": {
        "farmer": "Farmer Name",
        "village": "Select Village",
        "variety": "Select Mango Variety",
        "run": "Run Smart Analysis",
    },
    "తెలుగు": {
        "farmer": "రైతు పేరు",
        "village": "గ్రామం ఎంచుకోండి",
        "variety": "మామిడి రకం ఎంచుకోండి",
        "run": "విశ్లేషణ ప్రారంభించండి",
    },
    "हिंदी": {
        "farmer": "किसान का नाम",
        "village": "गांव चुनें",
        "variety": "आम की किस्म चुनें",
        "run": "विश्लेषण चलाएं",
    }
}

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
    priority_cols = ["market", "unit_name", "company_name", "place", "name"]
    for col in priority_cols:
        if col in df.columns:
            return col
    return df.columns[0]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(np.radians,[lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return R * 2*np.arcsin(np.sqrt(a))

def get_road_route(lat1, lon1, lat2, lon2):
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    try:
        response = requests.get(url)
        data = response.json()
        if "routes" in data:
            route = data["routes"][0]["geometry"]["coordinates"]
            return [(coord[1], coord[0]) for coord in route]
    except:
        return None
    return None

# ---------------- SIDEBAR ----------------
st.sidebar.header("👨‍🌾 Farmer Details")

farmer_name = st.sidebar.text_input(text[language]["farmer"])

selected_village = st.sidebar.selectbox(
    text[language]["village"],
    villages[detect_name(villages)].unique()
)

variety = st.sidebar.selectbox(
    text[language]["variety"],
    ["Banganapalli","Totapuri","Neelam","Rasalu"]
)

quantity_qtl = st.sidebar.number_input("Quantity (Quintals)", min_value=1, value=10)

run = st.sidebar.button(text[language]["run"])

# ---------------- VARIETY RULES ----------------
variety_acceptance = {
    "Mandi":["Banganapalli","Totapuri","Neelam","Rasalu"],
    "Processing":["Totapuri","Neelam"],
    "Pulp":["Totapuri"],
    "Pickle":["Totapuri","Rasalu"],
    "Local Export":["Banganapalli"],
    "Abroad Export":["Banganapalli"]
}

margin_map = {
    "Mandi":0,
    "Processing":0.03,
    "Pulp":0.04,
    "Pickle":0.025,
    "Local Export":0.05,
    "Abroad Export":0.07
}

# ---------------- MAIN ----------------
if run:

    with st.spinner("Calculating best market for you..."):

        st.markdown(f"## 🙏 Namaste {farmer_name}")

        village_row = villages[villages[detect_name(villages)]==selected_village].iloc[0]
        v_lat, v_lon = village_row[detect_lat_lon(villages)[0]], village_row[detect_lat_lon(villages)[1]]

        mandi_data = prices.merge(geo,on="market",how="left")
        lat_m, lon_m = detect_lat_lon(mandi_data)
        mandi_data = mandi_data.dropna(subset=[lat_m,lon_m])

        mandi_data["distance"] = mandi_data.apply(
            lambda r: haversine(v_lat,v_lon,r[lat_m],r[lon_m]),axis=1)

        nearest = mandi_data.loc[mandi_data["distance"].idxmin()]
        base_price = nearest["today_price(rs/kg)"]

        # PRICE POPUP
        st.success(f"💰 Today's Price: ₹{base_price} per kg")

        results=[]

        category_dfs = {
            "Mandi":mandi_data,
            "Processing":processing,
            "Pulp":pulp,
            "Pickle":pickle_units,
            "Local Export":local_export,
            "Abroad Export":abroad_export
        }

        for cat,df in category_dfs.items():
            if variety not in variety_acceptance[cat]: continue
            lat,lon = detect_lat_lon(df)
            name_col = detect_name(df)
            if lat is None: continue

            for _,row in df.iterrows():
                if pd.notnull(row[lat]) and pd.notnull(row[lon]):

                    dist = haversine(v_lat,v_lon,row[lat],row[lon])
                    transport = dist * 12 * quantity_qtl
                    revenue = base_price*(1+margin_map[cat])*100*quantity_qtl
                    net = revenue - transport

                    results.append({
                        "Category":cat,
                        "Name":row[name_col],
                        "Distance_km":round(dist,2),
                        "Revenue":round(revenue,2),
                        "Transport Cost":round(transport,2),
                        "Net Profit":round(net,2),
                        "Lat":row[lat],
                        "Lon":row[lon]
                    })

        df_top10 = pd.DataFrame(results).sort_values("Net Profit",ascending=False).head(10).reset_index(drop=True)

        # ---------------- TOP CARDS ----------------
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Base Price (₹/kg)", int(base_price))
        col2.metric("Total Revenue (₹)", int(df_top10["Revenue"].max()))
        col3.metric("Best Market", df_top10.iloc[0]["Name"])
        col4.metric("Best Profit (₹)", int(df_top10.iloc[0]["Net Profit"]))

        # ---------------- BAR GRAPH ----------------
        st.subheader("📊 Profit Comparison")

        colors = px.colors.qualitative.Set2

        fig = go.Figure()

        for i in range(len(df_top10)):
            fig.add_trace(go.Bar(
                y=[df_top10["Name"][i]],
                x=[df_top10["Net Profit"][i]],
                orientation='h',
                marker_color=colors[i % len(colors)],
                name=df_top10["Category"][i]
            ))

        fig.update_layout(height=600, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

        # ---------------- TABLE ----------------
        st.subheader("📋 Top 10 Closest Markets")

        st.dataframe(df_top10[[
            "Name","Distance_km","Net Profit"
        ]])

        # ---------------- MAP ----------------
        st.subheader("🗺 Market Location Map")

        m = folium.Map(location=[v_lat,v_lon],zoom_start=9)

        folium.Marker([v_lat,v_lon],popup="Village",
                      icon=folium.Icon(color="black")).add_to(m)

        color_map = {
            "Mandi":"green","Processing":"blue","Pulp":"purple",
            "Pickle":"orange","Local Export":"red","Abroad Export":"darkred"
        }

        for _,row in df_top10.iterrows():

            folium.Marker(
                [row["Lat"],row["Lon"]],
                popup=row["Name"],
                icon=folium.Icon(color=color_map.get(row["Category"],"green"))
            ).add_to(m)

            road = get_road_route(v_lat, v_lon, row["Lat"], row["Lon"])
            if road:
                folium.PolyLine(road,color="orange",weight=4).add_to(m)

        st_folium(m,width=1100,height=500)
