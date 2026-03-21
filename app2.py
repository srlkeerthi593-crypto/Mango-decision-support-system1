import streamlit as st
import pandas as pd
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Mango DSS", layout="wide")

# -------------------------------
# MULTILINGUAL SUPPORT
# -------------------------------
language = st.sidebar.selectbox("🌐 Language / भाषा", ["English", "Hindi"])

translations = {
    "English": {
        "title": "Mango Decision Support System",
        "top3": "Top 3 Best Market Options",
        "distance": "Distance",
        "select_location": "Select Locations",
        "source": "Source (Farm)",
        "destination": "Destination (Market)",
        "result": "Best Recommendations",
    },
    "Hindi": {
        "title": "आम निर्णय समर्थन प्रणाली",
        "top3": "शीर्ष 3 बाजार विकल्प",
        "distance": "दूरी",
        "select_location": "स्थान चुनें",
        "source": "स्रोत (खेत)",
        "destination": "गंतव्य (बाजार)",
        "result": "सर्वश्रेष्ठ विकल्प",
    }
}

t = translations[language]

st.title("🥭 " + t["title"])

# -------------------------------
# SAMPLE DATA (Replace with your dataset)
# -------------------------------
data = {
    "Option": ["Market A", "Market B", "Market C", "Market D"],
    "Price": [3000, 2800, 2600, 3200],
    "Distance": [10, 5, 3, 20]
}

df = pd.DataFrame(data)

# SCORING FUNCTION (customizable)
df["Score"] = df["Price"] / df["Distance"]

# -------------------------------
# TOP 3 FUNCTION
# -------------------------------
def get_top_3_alternatives(df):
    df_sorted = df.sort_values(by="Score", ascending=False).head(3)

    colors = ["#2ecc71", "#f39c12", "#e74c3c"]

    results = []
    for i, (_, row) in enumerate(df_sorted.iterrows()):
        results.append({
            "name": row["Option"],
            "score": round(row["Score"], 2),
            "color": colors[i],
            "rank": i + 1,
            "price": row["Price"],
            "distance": row["Distance"]
        })
    return results

# -------------------------------
# EXPLANATION FUNCTION
# -------------------------------
def explain_option(option):
    explanations = {
        "Market A": "High price but moderate distance",
        "Market B": "Balanced option with good profit",
        "Market C": "Closest market with quick selling",
        "Market D": "Very high price but far distance"
    }
    return explanations.get(option, "")

# -------------------------------
# ROUTE FUNCTION (OSM)
# -------------------------------
@st.cache_resource
def get_route(lat1, lon1, lat2, lon2):
    G = ox.graph_from_point((lat1, lon1), dist=10000, network_type='drive')

    orig = ox.distance.nearest_nodes(G, lon1, lat1)
    dest = ox.distance.nearest_nodes(G, lon2, lat2)

    route = nx.shortest_path(G, orig, dest, weight='length')
    distance = nx.shortest_path_length(G, orig, dest, weight='length')

    return G, route, distance

def show_map(G, route):
    return ox.plot_route_folium(G, route)

# -------------------------------
# LOCATION INPUT
# -------------------------------
st.sidebar.header(t["select_location"])

lat1 = st.sidebar.number_input("Farm Latitude", value=30.3165)
lon1 = st.sidebar.number_input("Farm Longitude", value=78.0322)

lat2 = st.sidebar.number_input("Market Latitude", value=30.0668)
lon2 = st.sidebar.number_input("Market Longitude", value=79.0193)

# -------------------------------
# DISPLAY TOP 3
# -------------------------------
st.subheader("🌱 " + t["top3"])

top3 = get_top_3_alternatives(df)

for item in top3:
    st.markdown(
        f"""
        <div style="background-color:{item['color']}; padding:15px; border-radius:10px; margin-bottom:10px;">
            <h3 style="color:white;">Rank {item['rank']} - {item['name']}</h3>
            <p style="color:white;">💰 Price: ₹{item['price']}</p>
            <p style="color:white;">📍 Distance: {item['distance']} km</p>
            <p style="color:white;">⭐ Score: {item['score']}</p>
            <p style="color:white;">📌 {explain_option(item['name'])}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# MAP + ROUTE
# -------------------------------
st.subheader("🗺️ Route & Distance")

if st.button("Show Route"):
    try:
        G, route, dist = get_route(lat1, lon1, lat2, lon2)

        st.success(f"🚜 {t['distance']}: {round(dist/1000, 2)} km")

        route_map = show_map(G, route)
        st_folium(route_map, width=900)

    except Exception as e:
        st.error("Error loading map. Try nearby locations.")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.markdown("🚜 Built for Farmers | Smart Agriculture DSS")
