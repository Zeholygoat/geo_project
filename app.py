import streamlit as st
import geopandas as gpd
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

st.title("🌍 DataMapWales AI Planning Assistant (Prototype) by Sadab")
st.caption("Next-generation geospatial decision support system")

# -------------------------------
# FAKE REALISTIC UK DATA MODEL
# -------------------------------
layers = [
    {
        "name": "NRW Flood Risk Zone",
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
        "name": "Protected Habitat Wales",
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
        "name": "Greenbelt Planning Zone",
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
# CORE ENGINE (EXPLAINABLE AI STYLE)
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
        return "No planning constraints detected. Site is likely suitable for development."

    return f"""
This site intersects {len(hits)} regulatory constraint layers.

Key constraints:
- {', '.join(hits)}

The cumulative planning risk score is {score}, resulting in a {risk} classification.

Interpretation:
- Flood risk zones increase environmental compliance requirements
- Protected habitats require ecological assessment
- Overlapping constraints significantly increase planning rejection probability
"""

# -------------------------------
# MAP ENGINE (PRO GIS STYLE)
# -------------------------------
st.subheader("🗺️ Interactive Planning Map")

m = folium.Map(location=[51.5, -3.5], zoom_start=7, tiles="OpenStreetMap")

# Satellite layer
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri Satellite",
    name="Satellite"
).add_to(m)

# Draw tool (key feature)
Draw(export=True).add_to(m)

# Layers
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
# INPUT ANALYSIS
# -------------------------------
st.subheader("📌 Geo-Constraint Analysis Engine")

geojson_input = st.text_area("Paste Drawn GeoJSON Here")

if st.button("Run Planning Analysis"):
    try:
        data = json.loads(geojson_input)
        geom = shape(data["geometry"] if "geometry" in data else data)

        risk, score, hits, explanation = analyze(geom)

        col1, col2, col3 = st.columns(3)
        col1.metric("Risk Level", risk)
        col2.metric("Score", score)
        col3.metric("Constraints", len(hits))

        st.subheader("🧠 AI Planning Explanation")
        st.write(explanation)

        # -------------------------------
        # DASHBOARD CHART
        # -------------------------------
        st.subheader("📊 Risk Analytics")

        fig, ax = plt.subplots()
        ax.bar(["Risk Score"], [score])
        st.pyplot(fig)

        # -------------------------------
        # DECISION ENGINE
        # -------------------------------
        if risk == "HIGH":
            decision = "❌ Not suitable without major mitigation"
        elif risk == "MEDIUM":
            decision = "⚠️ Conditional approval required"
        else:
            decision = "✅ Suitable for development"

        st.subheader("📢 Planning Decision")
        st.success(decision)

        # -------------------------------
        # PDF REPORT (COUNCIL STYLE)
        # -------------------------------
        def generate_pdf():
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            doc = SimpleDocTemplate(tmp.name)
            styles = getSampleStyleSheet()

            content = []
            content.append(Paragraph("Planning Assessment Report", styles["Title"]))
            content.append(Spacer(1, 12))

            content.append(Paragraph(f"Risk Level: {risk}", styles["Normal"]))
            content.append(Paragraph(f"Score: {score}", styles["Normal"]))
            content.append(Paragraph(f"Constraints: {hits}", styles["Normal"]))
            content.append(Paragraph(f"Decision: {decision}", styles["Normal"]))

            doc.build(content)
            return tmp.name

        pdf = generate_pdf()

        with open(pdf, "rb") as f:
            st.download_button("📄 Download Official Report (PDF)", f, file_name="planning_report.pdf")

    except Exception:
        st.error("Invalid GeoJSON format")
