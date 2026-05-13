import streamlit as st
from shapely.geometry import shape
import folium
from folium.plugins import Draw, Fullscreen, MiniMap
from streamlit.components.v1 import html
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import tempfile
from branca.element import MacroElement
from jinja2 import Template

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="DataMapWales Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# ENTERPRISE CSS
# =========================================================
st.markdown(
    """
    <style>

    .stApp {
        background-color: #0B0F19;
        color: #E5E7EB;
        font-family: 'Inter', sans-serif;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    .main-title {
        font-size: 42px;
        font-weight: 700;
        color: white;
        margin-bottom: 0;
        letter-spacing: -1px;
    }

    .subtitle {
        font-size: 16px;
        color: #9CA3AF;
        margin-top: 4px;
        margin-bottom: 30px;
    }

    .glass-card {
        background: rgba(17, 24, 39, 0.85);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.35);
        backdrop-filter: blur(12px);
    }

    .metric-card {
        background: linear-gradient(135deg, #111827, #1F2937);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 24px;
        transition: 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        border: 1px solid rgba(59,130,246,0.4);
    }

    .metric-title {
        font-size: 13px;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .metric-value {
        font-size: 34px;
        font-weight: 700;
        color: white;
        margin-top: 10px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        color: white;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    .ai-panel {
        background: linear-gradient(135deg, #0F172A, #111827);
        border: 1px solid rgba(6,182,212,0.3);
        border-radius: 18px;
        padding: 22px;
    }

    .stTextInput input,
    .stTextArea textarea {
        background-color: #111827;
        color: white;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
    }

    .stButton button {
        background: linear-gradient(135deg, #2563EB, #06B6D4);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 20px;
        font-weight: 600;
    }

    .stButton button:hover {
        background: linear-gradient(135deg, #1D4ED8, #0891B2);
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# HEADER
# =========================================================
st.markdown(
    """
    <div class="main-title">DataMapWales Intelligence Platform</div>
    <div class="subtitle">
    AI-assisted spatial risk assessment and geospatial planning intelligence.
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# DEFAULT LAYERS
# =========================================================
def get_default_layers():
    return [
        {
            "name": "Flood Exposure Zone",
            "weight": 5,
            "color": "#3B82F6",
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
            "name": "Protected Ecological Habitat",
            "weight": 4,
            "color": "#EF4444",
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
            "name": "Strategic Greenbelt Zone",
            "weight": 2,
            "color": "#10B981",
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

# =========================================================
# LOAD GEOJSON
# =========================================================
def load_geojson(file):
    data = json.load(file)
    features = data["features"]

    zones = []

    for f in features:
        zones.append({
            "name": f["properties"].get("name", "Spatial Layer"),
            "geometry": shape(f["geometry"]),
            "weight": f["properties"].get("weight", 3),
            "color": "#F59E0B"
        })

    return zones

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## Platform Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload Geospatial Dataset",
    type=["geojson"]
)

risk_sensitivity = st.sidebar.slider(
    "Risk Sensitivity",
    1,
    10,
    5
)

map_style = st.sidebar.selectbox(
    "Map Visualization",
    ["Dark", "Satellite", "Terrain"]
)

if uploaded_file:
    layers = load_geojson(uploaded_file)
else:
    layers = get_default_layers()

# =========================================================
# ANALYSIS ENGINE
# =========================================================
def analyze(geom):

    score = 0
    hits = []

    for layer in layers:
        if geom.intersects(layer["geometry"]):
            score += layer["weight"]
            hits.append(layer["name"])

    environmental_index = min(score * 12, 100)
    viability = max(100 - (score * 10), 5)

    if score >= 7:
        risk = "HIGH"
    elif score >= 3:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    explanation = generate_explanation(hits, score, risk)

    return (
        risk,
        score,
        hits,
        explanation,
        environmental_index,
        viability
    )

# =========================================================
# AI EXPLANATION ENGINE
# =========================================================
def generate_explanation(hits, score, risk):

    if not hits:
        return """
        Spatial analysis indicates minimal environmental and regulatory constraints
        affecting the selected development zone.

        Current spatial intelligence scoring suggests a favorable planning profile
        with low projected resistance across environmental assessment categories.

        The site appears strategically suitable for preliminary development review.
        """

    return f"""
    Spatial analysis indicates significant planning and environmental constraints
    affecting the selected development region.

    Primary spatial conflicts originate from:

    • {' • '.join(hits)}

    Composite spatial risk score: {score}
    Classification: {risk}

    Environmental sensitivity and overlapping regulatory restrictions may increase
    planning complexity and approval resistance.

    Additional ecological surveys, mitigation frameworks, and planning reviews are
    recommended before formal submission.
    """

# =========================================================
# MAIN GRID
# =========================================================
left, right = st.columns([3.2, 1.2])

# =========================================================
# MAP SECTION
# =========================================================
with left:

    st.markdown(
        '<div class="section-title">Geospatial Intelligence Map</div>',
        unsafe_allow_html=True
    )

    if map_style == "Dark":
        tiles = "CartoDB dark_matter"
    else:
        tiles = "OpenStreetMap"

    m = folium.Map(
        location=[51.5, -3.5],
        zoom_start=7,
        tiles=tiles
    )

    if map_style == "Satellite":
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri",
            name="Satellite"
        ).add_to(m)

    Fullscreen().add_to(m)
    MiniMap().add_to(m)
    Draw(export=True).add_to(m)

    for layer in layers:

        folium.GeoJson(
            layer["geometry"],
            name=layer["name"],
            style_function=lambda x, color=layer["color"]: {
                "fillColor": color,
                "color": color,
                "weight": 2,
                "fillOpacity": 0.45
            }
        ).add_to(m)

    folium.LayerControl().add_to(m)

    html(m._repr_html_(), height=720)

# =========================================================
# RIGHT PANEL
# =========================================================
with right:

    st.markdown(
        """
        <div class="glass-card">
        <div class="section-title">Platform Status</div>
        <p>Spatial Intelligence Engine Active</p>
        <p>Environmental Dataset Integrity: Stable</p>
        <p>Risk Classification Network Online</p>
        <p>Geospatial Processing Status: Operational</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="ai-panel">
        <div class="section-title">AI Planning Copilot</div>
        <p>
        Ask natural language questions about development suitability,
        environmental impact, or planning resistance.
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    ai_question = st.text_input("Planning Query")

# =========================================================
# ANALYSIS INPUT
# =========================================================
st.markdown(
    '<div class="section-title">Spatial Analysis Engine</div>',
    unsafe_allow_html=True
)

geojson_input = st.text_area(
    "Paste GeoJSON Geometry",
    height=180
)

# =========================================================
# ANALYSIS EXECUTION
# =========================================================
if st.button("Run Spatial Analysis"):

    try:

        data = json.loads(geojson_input)
        geom = shape(data["geometry"] if "geometry" in data else data)

        (
            risk,
            score,
            hits,
            explanation,
            environmental_index,
            viability
        ) = analyze(geom)

        # =========================================================
        # ENTERPRISE METRICS
        # =========================================================
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(
                f"""
                <div class="metric-card">
                <div class="metric-title">Planning Risk</div>
                <div class="metric-value">{risk}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:
            st.markdown(
                f"""
                <div class="metric-card">
                <div class="metric-title">Risk Score</div>
                <div class="metric-value">{score}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c3:
            st.markdown(
                f"""
                <div class="metric-card">
                <div class="metric-title">Environmental Sensitivity</div>
                <div class="metric-value">{environmental_index}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c4:
            st.markdown(
                f"""
                <div class="metric-card">
                <div class="metric-title">Development Viability</div>
                <div class="metric-value">{viability}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # =========================================================
        # AI EXPLANATION
        # =========================================================
        st.markdown(
            '<div class="section-title">Spatial Intelligence Assessment</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="glass-card">
            {explanation}
            </div>
            """,
            unsafe_allow_html=True
        )

        # =========================================================
        # ADVANCED CHARTS
        # =========================================================
        st.markdown(
            '<div class="section-title">Risk Analytics</div>',
            unsafe_allow_html=True
        )

        chart1, chart2 = st.columns(2)

        with chart1:

            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                title={'text': "Composite Risk Index"},
                gauge={
                    'axis': {'range': [0, 12]},
                    'bar': {'color': "#3B82F6"},
                    'steps': [
                        {'range': [0, 3], 'color': "#10B981"},
                        {'range': [3, 7], 'color': "#F59E0B"},
                        {'range': [7, 12], 'color': "#EF4444"}
                    ]
                }
            ))

            gauge.update_layout(
                paper_bgcolor="#0B0F19",
                font_color="white",
                height=400
            )

            st.plotly_chart(gauge, use_container_width=True)

        with chart2:

            radar_df = pd.DataFrame({
                'Category': [
                    'Flood Exposure',
                    'Ecological Risk',
                    'Planning Resistance',
                    'Infrastructure Stress',
                    'Environmental Impact'
                ],
                'Score': [
                    min(score * 1.3, 10),
                    min(score * 1.1, 10),
                    min(score * 1.2, 10),
                    min(score * 0.8, 10),
                    min(score * 1.4, 10)
                ]
            })

            radar = px.line_polar(
                radar_df,
                r='Score',
                theta='Category',
                line_close=True
            )

            radar.update_traces(fill='toself')

            radar.update_layout(
                paper_bgcolor="#0B0F19",
                font_color="white",
                height=400
            )

            st.plotly_chart(radar, use_container_width=True)

        # =========================================================
        # DECISION ENGINE
        # =========================================================
        st.markdown(
            '<div class="section-title">Strategic Recommendation</div>',
            unsafe_allow_html=True
        )

        if risk == "HIGH":
            recommendation = "Development exposure is critically elevated. Significant planning resistance and environmental review complexity are anticipated."

        elif risk == "MEDIUM":
            recommendation = "Development may proceed conditionally subject to mitigation strategies, environmental assessments, and planning negotiations."

        else:
            recommendation = "Current spatial intelligence indicates a favorable development profile with limited environmental resistance."

        st.markdown(
            f"""
            <div class="glass-card">
            {recommendation}
            </div>
            """,
            unsafe_allow_html=True
        )

        # =========================================================
        # AI ASSISTANT RESPONSES
        # =========================================================
        if ai_question:

            st.markdown(
                '<div class="section-title">AI Copilot Response</div>',
                unsafe_allow_html=True
            )

            if "approval" in ai_question.lower():
                response = f"Based on current spatial intelligence scoring, projected planning approval probability aligns with a {risk.lower()}-risk development profile."

            elif "environment" in ai_question.lower():
                response = "Environmental assessment indicators suggest that ecological and spatial mitigation reviews should be prioritized before submission."

            else:
                response = "The selected site demonstrates overlapping spatial constraints that influence planning feasibility, environmental exposure, and infrastructure compatibility."

            st.markdown(
                f"""
                <div class="glass-card">
                {response}
                </div>
                """,
                unsafe_allow_html=True
            )

        # =========================================================
        # PDF REPORT GENERATION
        # =========================================================
        def generate_pdf():

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

            doc = SimpleDocTemplate(
                tmp.name,
                pagesize=A4
            )

            styles = getSampleStyleSheet()
            content = []

            content.append(
                Paragraph(
                    "DataMapWales Intelligence Report",
                    styles['Title']
                )
            )

            content.append(Spacer(1, 18))

            content.append(
                Paragraph(
                    f"Planning Risk Classification: {risk}",
                    styles['Normal']
                )
            )

            content.append(
                Paragraph(
                    f"Composite Risk Score: {score}",
                    styles['Normal']
                )
            )

            content.append(
                Paragraph(
                    f"Environmental Sensitivity Index: {environmental_index}%",
                    styles['Normal']
                )
            )

            content.append(
                Paragraph(
                    f"Development Viability: {viability}%",
                    styles['Normal']
                )
            )

            content.append(Spacer(1, 18))

            content.append(
                Paragraph(
                    explanation,
                    styles['BodyText']
                )
            )

            doc.build(content)

            return tmp.name

        pdf = generate_pdf()

        with open(pdf, "rb") as f:
            st.download_button(
                "Download Intelligence Report",
                f,
                file_name="datamapwales_report.pdf"
            )

    except Exception as e:

        st.error(
            f"Spatial processing error: {e}"
        )
