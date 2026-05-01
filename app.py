import streamlit as st
from shapely.geometry import shape
import folium
from folium.plugins import Draw
from streamlit.components.v1 import html
import json
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="DataMapWales AI Prototype", layout="wide")

st.title("🌍 DataMapWales AI Planning Assistant (Prototype) By Sadab")
st.caption("Geospatial Decision Support System for Planning")

# -------------------------------
# DEFAULT DATA (WORKS WITHOUT UPLOAD)
# -------------------------------
def get_default_layers():
    return [
        {
            "name": "Flood Risk Zone",
            "weight": 5,
            "color": "blue",
            "geometry": shape({
                "type": "Polygon",
                "coordinates": [[
                    [-3.8, 51.4], [-3.5, 51.4],
                    [-3.5, 51.7], [-3.8, 51.7],
                    [-3.8, 51.4]
                ]]
            })
        },
        {
            "name": "Protected Habitat",
            "weight": 4,
            "color": "red",
            "geometry": shape({
                "type": "Polygon",
                "coordinates": [[
                    [-3.6, 51.3], [-3.3, 51.3],
                    [-3.3, 51.6], [-3.6, 51.6],
                    [-3.6, 51.3]
                ]]
            })
        },
        {
            "name": "Greenbelt Zone",
            "weight": 2,
            "color": "green",
            "geometry": shape({
                "type": "Polygon",
                "coordinates": [[
                    [-3.9, 51.2], [-3.4, 51.2],
                    [-3.4, 51.4], [-3.9, 51.4],
                    [-3.9, 51.2]
                ]]
            })
        }
    ]

# -------------------------------
# LOAD GEOJSON (SAFE, NO GEOPANDAS)
# -------------------------------
def load_geojson(file):
    data = json.load(file)
    features = data["features"]

    zones = []
    for f in features:
        zones.append({
            "name": f["properties"].get("name", "Layer"),
            "geometry": shape(f["geometry"]),
            "weight": f["properties"].get("weight", 3),
            "color": "orange"
        })

    return zones

# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.header("📂 Data Input")

uploaded_file = st.sidebar.file_uploader("Upload GeoJSON", type=["geojson"])

if uploaded_file:
    layers = load_geojson(uploaded_file)
else:
    layers = get_default_layers()

# -------------------------------
# ANALYSIS ENGINE
# -------------------------------
def analyze(geom):
    score = 0
    hits = []

    for l in layers:
        if geom.intersects(l["geometry"]):
            score += l["weight"]
            hits.append(l["name"])

    if score >= 7:
        risk = "HIGH"
    elif score >= 3:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    explanation = explain(hits, score, risk)

    return risk, score, hits, explanation


def explain(hits, score, risk):
    if not hits:
        return "No planning constraints detected. Site is likely suitable."

    return f"""
This site intersects {len(hits)} constraint layers.

Constraints:
- {', '.join(hits)}

Score: {score} → Risk Level: {risk}

Interpretation:
- Flood zones increase environmental restrictions
- Protected areas require ecological assessments
- Overlapping constraints increase rejection likelihood
"""

# -------------------------------
# MAP
# -------------------------------
st.subheader("🗺️ Interactive Planning Map")

m = folium.Map(location=[51.5, -3.5], zoom_start=7, tiles="OpenStreetMap")

# Satellite
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
    name="Satellite"
).add_to(m)

Draw(export=True).add_to(m)

# Add layers
for l in layers:
    folium.GeoJson(
        l["geometry"],
        name=l["name"],
        style_function=lambda x, color=l["color"]: {
            "fillColor": color,
            "color": color,
            "weight": 2,
            "fillOpacity": 0.4
        }
    ).add_to(m)

folium.LayerControl().add_to(m)

html(m._repr_html_(), height=600)

# -------------------------------
# INPUT
# -------------------------------
st.subheader("📌 Analyze Geometry")

geojson_input = st.text_area("Paste GeoJSON here")

if st.button("Run Analysis"):
    try:
        data = json.loads(geojson_input)
        geom = shape(data["geometry"] if "geometry" in data else data)

        risk, score, hits, explanation = analyze(geom)

        col1, col2, col3 = st.columns(3)
        col1.metric("Risk Level", risk)
        col2.metric("Score", score)
        col3.metric("Constraints", len(hits))

        st.subheader("🧠 Explanation")
        st.write(explanation)

        # Chart
        st.subheader("📊 Risk Chart")
        fig, ax = plt.subplots()
        ax.bar(["Risk Score"], [score])
        st.pyplot(fig)

        # Recommendation
        if risk == "HIGH":
            decision = "❌ Not suitable"
        elif risk == "MEDIUM":
            decision = "⚠️ Conditional approval"
        else:
            decision = "✅ Suitable"

        st.subheader("📢 Decision")
        st.success(decision)

        # -------------------------------
        # AI Assistant (Safe Version)
        # -------------------------------
        st.subheader("🤖 Planning Assistant")

        question = st.text_input("Ask about this site")

        if question:
            if "approve" in question.lower():
                st.write(decision)
            else:
                st.write("This site is influenced by planning constraints and zoning regulations.")

        # -------------------------------
        # PDF REPORT
        # -------------------------------
        def generate_pdf():
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            doc = SimpleDocTemplate(tmp.name)
            styles = getSampleStyleSheet()

            content = []
            content.append(Paragraph("Planning Report", styles["Title"]))
            content.append(Spacer(1, 12))
            content.append(Paragraph(f"Risk: {risk}", styles["Normal"]))
            content.append(Paragraph(f"Score: {score}", styles["Normal"]))
            content.append(Paragraph(f"Constraints: {hits}", styles["Normal"]))
            content.append(Paragraph(f"Decision: {decision}", styles["Normal"]))

            doc.build(content)
            return tmp.name

        pdf = generate_pdf()

        with open(pdf, "rb") as f:
            st.download_button("📄 Download PDF Report", f, file_name="report.pdf")

    except:
        st.error("Invalid GeoJSON format")

