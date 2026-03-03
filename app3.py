# ============================================================
# 🥭 FARMER’S MANGO PROFIT NAVIGATOR 🥭
# Find the Best Market. Earn the Highest Return.
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

st.title("🥭 Farmer’s Mango Profit Navigator 🥭")
st.subheader("🧭 Find the Best Market. Earn the Highest Return.")

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

# ---------------- ROAD ROUTING ----------------
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
st.sidebar.header("👨‍🌾 Farmer Details 🥭")

farmer_name = st.sidebar.text_input("Farmer Name 🥭")

selected_village = st.sidebar.selectbox(
    "Select Village 🏡",
    villages[detect_name(villages)].unique()
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
if st.session_state.run:

    st.markdown(f"## 🙏🥭 Namaste **{farmer_name}** 🥭")

    st.subheader("🧠 Alternative Selection Logic")
    st.markdown(f"""
**Step 1:** Filter categories that accept {variety}  
**Step 2:** Calculate distance using Haversine formula  
**Step 3:** Transport Cost = Distance × ₹200 × Quantity  
**Step 4:** Revenue = Base Price × (1 + Margin) × 100 × Quantity  
**Step 5:** Net Profit = Revenue − Transport Cost  
**Step 6:** Select Top 10 by highest Net Profit
""")

    village_row = villages[villages[detect_name(villages)]==selected_village].iloc[0]
    v_lat, v_lon = village_row[detect_lat_lon(villages)[0]], village_row[detect_lat_lon(villages)[1]]

    mandi_data = prices.merge(geo,on="market",how="left")
    lat_m, lon_m = detect_lat_lon(mandi_data)
    mandi_data = mandi_data.dropna(subset=[lat_m,lon_m])

    mandi_data["distance"] = mandi_data.apply(
        lambda r: haversine(v_lat,v_lon,r[lat_m],r[lon_m]),axis=1)

    nearest = mandi_data.loc[mandi_data["distance"].idxmin()]
    base_price = nearest["today_price(rs/kg)"]

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
                transport = dist * 200 * quantity_qtl   # UPDATED RULE
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

    df_top10 = pd.DataFrame(results).drop_duplicates(
        subset=["Name","Category"]
    ).sort_values("Net Profit",ascending=False).head(10).reset_index(drop=True)

    df_top10["Rank"]=df_top10.index+1

    # ---------------- CHARTS ----------------
    st.subheader("📊🥭 Profit Comparison")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_top10["Name"],
        x=df_top10["Net Profit"],
        orientation='h',
        text=[f"₹{x:,.0f}" for x in df_top10["Net Profit"]],
        textposition="outside",
        marker=dict(color=df_top10["Net Profit"], colorscale="Turbo")
    ))
    fig.update_layout(height=700, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🥭 Category-wise Profit Distribution")
    pie_data = df_top10.groupby("Category")["Net Profit"].sum().reset_index()
    pie_fig = px.pie(pie_data, names="Category", values="Net Profit", hole=0.4)
    st.plotly_chart(pie_fig, use_container_width=True)

    st.subheader("📋🥭 Detailed Comparison Table")
    st.dataframe(df_top10[[
        "Rank","Name","Category",
        "Distance_km","Revenue",
        "Transport Cost","Net Profit"
    ]])
