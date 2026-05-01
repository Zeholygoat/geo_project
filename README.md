# 🌍 DataMapWales AI Planning Assistant (Prototype) BY Sadab 

A **geospatial decision-support system** that simulates how planning authorities assess land suitability by analyzing environmental and legal constraints.

This project demonstrates how platforms similar to **DataMapWales** can automate traditionally manual workflows by combining spatial data, rule-based analysis, and explainable outputs.

---

## 🚀 Live Demo

👉 *(Add your Streamlit link here once deployed)*
Example: `https://your-app.streamlit.app`

---

## 🎯 Project Purpose

Planning departments often spend significant time manually checking whether a proposed development site is affected by:

* Flood risk zones
* Environmental protection areas
* Heritage constraints
* Policy zones (e.g. greenbelt)

This project explores how that process can be **automated and standardized** using geospatial computation.

---

## 🧠 Key Features

### 🗺️ Interactive Map Interface

* Built using Folium
* Supports:

  * OpenStreetMap base layer
  * Satellite imagery
  * Toggleable constraint layers
* Users can draw custom development areas directly on the map

---

### 📂 GeoJSON Data Integration

* Upload custom GeoJSON datasets
* Supports standard geospatial formats used by government platforms
* Enables flexible dataset simulation (e.g. Natural Resources Wales-style layers)

---

### ⚙️ Spatial Analysis Engine

* Built using Shapely
* Performs:

  * Polygon intersection checks
  * Multi-layer constraint detection
* Each
