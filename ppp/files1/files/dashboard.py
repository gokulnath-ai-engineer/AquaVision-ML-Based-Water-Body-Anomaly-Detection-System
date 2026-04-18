"""
dashboard.py
━━━━━━━━━━━━
🌊 Aqua-Sentinel AI — Streamlit Dashboard
──────────────────────────────────────────────────────────────
Interactive web dashboard for visualising multi-spectral water
quality monitoring and forensic anomaly detection results.

Features:
  • 🗺️  Interactive map with colour-coded hotspot markers
  • 🌡️  Thermal heatmap gallery with anomaly overlays
  • 📊  Detection statistics and confidence distributions
  • 🔍  Chip inspector — click to see annotated detections
  • 🧪  Forensic analysis verdicts with severity badges
  • 🌈  Spectral analysis (NDWI, Chlorophyll-a, Turbidity)
  • 📋  Full detection table with filtering & sorting

Usage:
    streamlit run dashboard.py
"""

import streamlit as st
import json
from pathlib import Path
from PIL import Image
import numpy as np

from config import ROI, DASHBOARD, INFER, PREPROCESS, SPECTRAL, RIVER_ONLY_MODE
from geo_hierarchy import get_states, get_cities, get_water_bodies, get_roi, get_rivers_only
from dashboard_utils import (
    load_detections_csv,
    load_geojson,
    get_heatmap_files,
    get_detection_images,
    get_tile_images,
    get_mask_images,
    compute_statistics,
    get_severity_color,
    get_severity_label,
    load_forensic_analysis,
    get_anomaly_type_color,
    get_anomaly_type_icon,
    compute_forensic_summary,
)


# ──────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Aqua-Sentinel AI",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ──────────────────────────────────────────────
# Custom CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .main { font-family: 'Inter', sans-serif; }

    .hero-header {
        background: linear-gradient(135deg, #0a1628 0%, #0d2137 30%, #0f3460 60%, #1a5276 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(72,219,251,0.15);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .hero-header h1 {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #48dbfb, #0abde3, #58d68d, #48dbfb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    .hero-header p {
        color: #a0aec0;
        font-size: 1rem;
        margin: 0;
    }

    .metric-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #48dbfb;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.82rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.3rem;
    }

    .severity-critical { color: #ff4444; font-weight: 600; }
    .severity-warning  { color: #ffaa00; font-weight: 600; }
    .severity-monitor  { color: #44aaff; font-weight: 600; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 20px;
        border-radius: 8px;
    }

    div[data-testid="stImage"] img {
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .forensic-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .forensic-card h4 { margin: 0 0 0.5rem 0; }
    .severity-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.05em;
    }
    .severity-badge.critical { background: #ff4444; color: #fff; }
    .severity-badge.high     { background: #ff6600; color: #fff; }
    .severity-badge.warning  { background: #ffaa00; color: #1a1a2e; }
    .severity-badge.low      { background: #44aaff; color: #1a1a2e; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────
st.markdown(f"""
<div class="hero-header">
    <h1>{DASHBOARD['title']}</h1>
    <p>{DASHBOARD['subtitle']}</p>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Load data
# ──────────────────────────────────────────────
@st.cache_data
def load_data():
    detections = load_detections_csv()
    geojson = load_geojson()
    stats = compute_statistics(detections)
    return detections, geojson, stats


detections, geojson, stats = load_data()
heatmaps = get_heatmap_files()
det_images = get_detection_images()
tiles = get_tile_images()
masks = get_mask_images()


# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛰️ Pipeline Status")

    raw_dir = Path(PREPROCESS["raw_dir"])
    proc_dir = Path(PREPROCESS["processed_dir"])
    weights_path = Path(INFER["best_weights"])

    status_items = [
        ("GeoTIFF Data", raw_dir.exists() and any(raw_dir.glob("*.tif"))),
        ("Heatmaps", len(heatmaps) > 0),
        ("Training Dataset", Path("data/dataset/data.yaml").exists()),
        ("Model Weights", weights_path.exists()),
        ("Detection Reports", Path(INFER["report_csv"]).exists()),
    ]

    for name, ready in status_items:
        icon = "✅" if ready else "⏳"
        st.markdown(f"{icon} {name}")

    # ── Hierarchical Geo Navigation ──
    st.markdown("---")
    st.markdown("### 🌍 Geo Navigation")

    states = get_states()
    default_state = ROI.get("state", states[0] if states else "")
    selected_state = st.selectbox(
        "State",
        states if states else [default_state],
        index=states.index(default_state) if default_state in states else 0,
    )

    cities = get_cities(selected_state)
    default_city = ROI.get("city", cities[0] if cities else "")
    selected_city = st.selectbox(
        "City",
        cities if cities else [default_city],
        index=cities.index(default_city) if default_city in cities else 0,
    )

    # RIVER-ONLY MODE: filter to show only rivers, no lakes/reservoirs
    if RIVER_ONLY_MODE:
        water_bodies = get_rivers_only(selected_state, selected_city)
        wb_label = "River"
    else:
        water_bodies = [wb["name"] for wb in get_water_bodies(selected_state, selected_city)]
        wb_label = "Water Body"
    default_wb = ROI.get("water_body", water_bodies[0] if water_bodies else "")
    selected_water_body = st.selectbox(
        wb_label,
        water_bodies if water_bodies else [default_wb],
        index=water_bodies.index(default_wb) if default_wb in water_bodies else 0,
    )

    # Update active ROI from geo-hierarchy selection
    active_roi = get_roi(selected_state, selected_city, selected_water_body)
    if active_roi:
        ROI.update(active_roi)

    st.markdown("---")
    st.markdown("### ⚙️ Study Area")
    st.markdown(f"**{ROI['name']}**")
    st.markdown(f"Lat: {ROI['lat_min']:.2f}° – {ROI['lat_max']:.2f}°")
    st.markdown(f"Lon: {ROI['lon_min']:.2f}° – {ROI['lon_max']:.2f}°")

    st.markdown("---")
    st.markdown("### 📊 Detection Filter")
    min_conf = st.slider("Min Confidence", 0.0, 1.0, 0.0, 0.05)

    # Filter detections
    filtered = [d for d in detections if d["confidence"] >= min_conf]
    filtered_stats = compute_statistics(filtered)

    # ── PDF Download ──
    pdf_path = Path("reports/incident_report.pdf")
    if pdf_path.exists():
        st.markdown("---")
        st.markdown("### 📄 Incident Report")
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                "📥 Download PDF Report",
                data=pdf_file.read(),
                file_name="incident_report.pdf",
                mime="application/pdf",
            )


# ──────────────────────────────────────────────
# Metrics row
# ──────────────────────────────────────────────
cols = st.columns(5)

metric_data = [
    ("🎯", str(filtered_stats["total_detections"]), "Detections"),
    ("📍", str(filtered_stats["unique_chips"]), "Affected Tiles"),
    ("📈", f"{filtered_stats['avg_confidence']:.1%}" if filtered_stats["total_detections"] > 0 else "—", "Avg Confidence"),
    ("🔴", str(filtered_stats["high_conf"]), "Critical (>70%)"),
    ("🗺️", str(filtered_stats["geo_located"]), "GPS Located"),
]

for col, (icon, value, label) in zip(cols, metric_data):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Tabs
# ──────────────────────────────────────────────
tab_map, tab_heatmaps, tab_detections, tab_forensic, tab_table, tab_report, tab_spectral = st.tabs([
    "🗺️ Hotspot Map",
    "🌡️ Heatmaps",
    "🔍 Detection Gallery",
    "🧪 Forensic Analysis",
    "📋 Detection Table",
    "📈 Analysis Report",
    "🌈 Spectral Analysis",
])


# ──────────────────────────────────────────────
# Tab 1: Interactive Map
# ──────────────────────────────────────────────
with tab_map:
    st.markdown(f"### Interactive River Hotspot Map — {ROI.get('water_body', 'River')}")
    if RIVER_ONLY_MODE:
        st.markdown("Each marker represents an anomaly detected **strictly within the river channel**. "
                    "Colour indicates anomaly type.")
    else:
        st.markdown("Each marker represents a detected thermal anomaly. Colour indicates severity.")

    geo_dets = [d for d in filtered if d["centre_lat"] is not None]

    if geo_dets:
        try:
            import folium
            from streamlit_folium import st_folium

            m = folium.Map(
                location=[DASHBOARD["map_center_lat"], DASHBOARD["map_center_lon"]],
                zoom_start=DASHBOARD["map_zoom"],
                tiles="CartoDB dark_matter",
            )

            # Add satellite tile layer
            folium.TileLayer(
                tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                attr="Esri",
                name="Satellite",
            ).add_to(m)

            # Add river study area boundary
            bounds = [
                [ROI["lat_min"], ROI["lon_min"]],
                [ROI["lat_min"], ROI["lon_max"]],
                [ROI["lat_max"], ROI["lon_max"]],
                [ROI["lat_max"], ROI["lon_min"]],
            ]
            folium.Polygon(
                bounds,
                color="#48dbfb",
                fill=True,
                fill_opacity=0.05,
                weight=2,
                tooltip="Study Area Boundary",
            ).add_to(m)

            # Build a lookup of forensic verdicts keyed by chip name
            _forensic_data = load_forensic_analysis()
            _forensic_by_chip = {fa.get("chip", ""): fa for fa in _forensic_data}

            # Add detection markers (colour-coded by anomaly type)
            for d in geo_dets:
                anomaly_type = d.get("class", "")
                color = get_anomaly_type_color(anomaly_type)
                icon_emoji = get_anomaly_type_icon(anomaly_type)

                # Try to attach forensic verdict
                fa = _forensic_by_chip.get(d["chip"], {})
                verdict_line = f"<b>Forensic Verdict:</b> {fa['verdict']}<br>" if fa.get("verdict") else ""

                popup_html = f"""
                <div style="font-family: Inter, sans-serif; min-width: 220px;">
                    <h4 style="margin:0; color: #333;">{icon_emoji} {anomaly_type.replace('_', ' ').title()}</h4>
                    <hr style="margin: 4px 0;">
                    <b>Chip:</b> {d['chip']}<br>
                    <b>Confidence:</b> {d['confidence']:.1%}<br>
                    <b>Severity:</b> {get_severity_label(d['confidence'])}<br>
                    <b>GPS:</b> {d['centre_lat']:.6f}, {d['centre_lon']:.6f}<br>
                    <b>Class:</b> {d['class']}<br>
                    {verdict_line}
                </div>
                """

                folium.CircleMarker(
                    location=[d["centre_lat"], d["centre_lon"]],
                    radius=8 + d["confidence"] * 10,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7,
                    weight=2,
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"{d['chip']} ({d['confidence']:.0%})",
                ).add_to(m)

            # Heatmap layer
            try:
                from folium.plugins import HeatMap
                heat_data = [[d["centre_lat"], d["centre_lon"], d["confidence"]]
                             for d in geo_dets]
                HeatMap(
                    heat_data,
                    radius=25,
                    blur=20,
                    gradient={0.2: 'blue', 0.5: 'yellow', 0.8: 'orange', 1.0: 'red'},
                    name="Thermal Heatmap",
                ).add_to(m)
            except ImportError:
                pass

            folium.LayerControl().add_to(m)
            st_folium(m, width=None, height=600, use_container_width=True)

        except ImportError:
            st.warning("Install folium and streamlit-folium: `pip install folium streamlit-folium`")
            st.map(
                data={"lat": [d["centre_lat"] for d in geo_dets],
                      "lon": [d["centre_lon"] for d in geo_dets]},
            )
    else:
        st.info("No geo-located detections available. Run the full pipeline first.")
        st.map()


# ──────────────────────────────────────────────
# Tab 2: Heatmaps (Enhanced Multi-Type Gallery)
# ──────────────────────────────────────────────
with tab_heatmaps:
    st.markdown("### 🌡️ Thermal Heatmap Gallery — River Analysis")
    if RIVER_ONLY_MODE:
        st.markdown(f"**River-Only Mode:** Heatmaps focused on **{ROI.get('water_body', 'river')}** channel — "
                    "land areas excluded from analysis.")
    st.markdown("Red/yellow = hotter areas, Blue = cooler areas.")

    # Primary JET heatmaps
    if heatmaps:
        st.markdown("#### Primary Thermal Heatmaps (JET Colormap)")
        cols_hm = st.columns(min(3, len(heatmaps)))
        for i, hm_path in enumerate(heatmaps):
            with cols_hm[i % 3]:
                img = Image.open(hm_path)
                st.image(img, caption=hm_path.stem, use_container_width=True)

    # Extra heatmaps — river-only, inferno, hot, turbo, density, gradient, overlay
    proc_dir = Path(PREPROCESS["processed_dir"])
    extra_types = [
        ("river_only",        "River-Only Thermal (Land Blacked Out)"),
        ("inferno",           "INFERNO Colormap"),
        ("hot",               "HOT Colormap"),
        ("turbo",             "TURBO Colormap"),
        ("ocean",             "OCEAN Colormap"),
        ("anomaly_density",   "Anomaly Density Heatmap"),
        ("thermal_gradient",  "Thermal Gradient Map"),
        ("annotated_overlay", "Annotated Overlay (Water + Anomaly Contours)"),
    ]

    for suffix, title in extra_types:
        extra_imgs = sorted(proc_dir.glob(f"*_heatmap_{suffix}.png"))
        if extra_imgs:
            st.markdown("---")
            st.markdown(f"#### {title}")
            cols_ex = st.columns(min(3, len(extra_imgs)))
            for i, ex_path in enumerate(extra_imgs):
                with cols_ex[i % 3]:
                    ex_img = Image.open(ex_path)
                    st.image(ex_img, caption=ex_path.stem, use_container_width=True)

    # Water mask visualisations
    water_mask_imgs = sorted(proc_dir.glob("*_water_mask.png"))
    if water_mask_imgs:
        st.markdown("---")
        st.markdown("#### 🗺️ River Water Mask Visualisation")
        st.markdown("Blue = river water (analysed), Red = excluded land (roads, buildings, soil)")
        cols_wm = st.columns(min(3, len(water_mask_imgs)))
        for i, wm_path in enumerate(water_mask_imgs):
            with cols_wm[i % 3]:
                wm_img = Image.open(wm_path)
                st.image(wm_img, caption=wm_path.stem, use_container_width=True)

    if not heatmaps:
        st.info("No heatmaps generated yet. Run `python run_pipeline.py --demo`")

    # Show tiles and masks side-by-side
    if tiles and masks:
        st.markdown("---")
        st.markdown("### 🔬 Tile vs Water Mask Comparison")

        n_show = min(6, len(tiles), len(masks))
        cols_tm = st.columns(3)
        for i in range(min(n_show, 3)):
            with cols_tm[i]:
                tile_img = Image.open(tiles[i])
                st.image(tile_img, caption=f"Tile: {tiles[i].stem}", use_container_width=True)

                # Find matching mask
                mask_name = f"{tiles[i].stem}_mask.png"
                mask_path = Path(PREPROCESS["processed_dir"]) / "masks" / mask_name
                if mask_path.exists():
                    mask_img = Image.open(mask_path)
                    st.image(mask_img, caption="River Water Mask", use_container_width=True)


# ──────────────────────────────────────────────
# Tab 3: Detection Gallery (Enhanced)
# ──────────────────────────────────────────────
with tab_detections:
    st.markdown(f"### 🔍 River Detection Gallery — {ROI.get('water_body', 'River')}")
    st.markdown("YOLOv8 annotated tiles with bounding boxes around detected anomalies "
                "**strictly within the river channel**.")

    if det_images:
        # Summary bar
        st.markdown(f"**{len(det_images)} detection tiles** from "
                    f"**{ROI.get('water_body', 'river')}**, "
                    f"**{ROI.get('city', '')}**, **{ROI.get('state', '')}**")

        # Gallery grid — 4 columns for comprehensive view
        n_cols = 4
        for i in range(0, min(len(det_images), 24), n_cols):
            cols_det = st.columns(n_cols)
            for j in range(n_cols):
                idx = i + j
                if idx < len(det_images):
                    with cols_det[j]:
                        img = Image.open(det_images[idx])
                        cap = det_images[idx].stem.replace("_detected", "")
                        st.image(img, caption=cap, use_container_width=True)

        # Side-by-side: original tile vs detection
        st.markdown("---")
        st.markdown("### 🔬 Before vs After Detection Comparison")
        st.markdown("Original river tile (left) vs YOLOv8 detection overlay (right)")

        comp_count = min(6, len(det_images))
        for i in range(0, comp_count, 2):
            cols_comp = st.columns(4)
            for j in range(2):
                idx = i + j
                if idx < len(det_images):
                    det_stem = det_images[idx].stem.replace("_detected", "")
                    orig_path = Path(PREPROCESS["processed_dir"]) / "tiles" / f"{det_stem}.png"

                    col_left = cols_comp[j * 2]
                    col_right = cols_comp[j * 2 + 1]

                    with col_left:
                        if orig_path.exists():
                            orig_img = Image.open(orig_path)
                            st.image(orig_img, caption=f"Original: {det_stem}", use_container_width=True)
                        else:
                            st.info(f"Original tile not found")

                    with col_right:
                        det_img = Image.open(det_images[idx])
                        st.image(det_img, caption=f"Detected: {det_stem}", use_container_width=True)

    else:
        st.info("No detection images yet. Run the full pipeline including inference.")


# ──────────────────────────────────────────────
# Tab 4: Forensic Analysis
# ──────────────────────────────────────────────
with tab_forensic:
    st.markdown("### 🧪 Forensic Analysis Verdicts")
    st.markdown("AI-driven forensic classification of each detected anomaly with reasoning chains.")

    forensic_results = load_forensic_analysis()

    if forensic_results:
        fsummary = compute_forensic_summary(forensic_results)
        fcols = st.columns(5)
        for col, (label, key) in zip(fcols, [
            ("Total", "total"), ("Critical", "CRITICAL"), ("High", "HIGH"),
            ("Warning", "WARNING"), ("Low", "LOW"),
        ]):
            with col:
                st.metric(label, fsummary[key])

        st.markdown("---")

        for fa in forensic_results:
            sev = fa.get("severity", "UNKNOWN").upper()
            badge_cls = {"CRITICAL": "critical", "HIGH": "high", "WARNING": "warning"}.get(sev, "low")
            anomaly_type = fa.get("anomaly_type", fa.get("class", "unknown"))
            icon = get_anomaly_type_icon(anomaly_type)
            color = get_anomaly_type_color(anomaly_type)

            verdict = fa.get("verdict", "No verdict available")
            chip = fa.get("chip", "—")

            card_html = f"""
            <div class="forensic-card" style="border-left: 4px solid {color};">
                <h4>{icon} {anomaly_type.replace('_', ' ').title()}
                    <span class="severity-badge {badge_cls}">{sev}</span>
                </h4>
                <p style="color: #cbd5e1; margin: 0.3rem 0;"><b>Chip:</b> {chip}</p>
                <p style="color: #e2e8f0; font-size: 1.05rem; margin: 0.5rem 0;">
                    <b>Verdict:</b> {verdict}
                </p>
            """

            # Reasoning chain
            reasoning = fa.get("reasoning", fa.get("reasoning_chain", []))
            if reasoning:
                card_html += '<p style="color: #94a3b8; margin: 0.4rem 0 0.2rem 0;"><b>Reasoning Chain:</b></p><ul style="color: #94a3b8; margin: 0;">'
                if isinstance(reasoning, list):
                    for step in reasoning:
                        card_html += f"<li>{step}</li>"
                else:
                    card_html += f"<li>{reasoning}</li>"
                card_html += "</ul>"

            # Recommended actions
            actions = fa.get("recommended_actions", fa.get("actions", []))
            if actions:
                card_html += '<p style="color: #94a3b8; margin: 0.6rem 0 0.2rem 0;"><b>Recommended Actions:</b></p><ul style="color: #94a3b8; margin: 0;">'
                if isinstance(actions, list):
                    for action in actions:
                        card_html += f"<li>{action}</li>"
                else:
                    card_html += f"<li>{actions}</li>"
                card_html += "</ul>"

            card_html += "</div>"
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.info("No forensic analysis data available. Run the forensic reasoning engine first.")


# ──────────────────────────────────────────────
# Tab 5: Detection Table
# ──────────────────────────────────────────────
with tab_table:
    st.markdown("### 📋 Full Detection Log")

    if filtered:
        # Convert to display format
        table_data = []
        for i, d in enumerate(filtered):
            table_data.append({
                "#": i + 1,
                "Chip": d["chip"],
                "Class": d["class"],
                "Confidence": f"{d['confidence']:.1%}",
                "Severity": get_severity_label(d["confidence"]),
                "Latitude": f"{d['centre_lat']:.6f}" if d["centre_lat"] else "—",
                "Longitude": f"{d['centre_lon']:.6f}" if d["centre_lon"] else "—",
            })

        st.dataframe(
            table_data,
            use_container_width=True,
            height=400,
        )

        # Download buttons
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv_path = Path(INFER["report_csv"])
            if csv_path.exists():
                with open(csv_path, "r") as f:
                    st.download_button(
                        "📥 Download CSV Report",
                        data=f.read(),
                        file_name="thermal_detections.csv",
                        mime="text/csv",
                    )

        with col_dl2:
            gj_path = Path(INFER["report_geojson"])
            if gj_path.exists():
                with open(gj_path, "r") as f:
                    st.download_button(
                        "🗺️ Download GeoJSON",
                        data=f.read(),
                        file_name="hotspots.geojson",
                        mime="application/geo+json",
                    )
    else:
        st.info("No detections match the current filter. Adjust the confidence slider.")


# ──────────────────────────────────────────────
# Tab 6: Analysis Report
# ──────────────────────────────────────────────
with tab_report:
    st.markdown("### 📈 Automated Analysis Report")

    if stats["total_detections"] > 0:
        # Confidence distribution
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("#### Confidence Distribution")
            import pandas as pd
            confs = [d["confidence"] for d in detections]
            hist_data = pd.DataFrame({"Confidence": confs})
            st.bar_chart(hist_data["Confidence"].value_counts(bins=10).sort_index())

        with col_chart2:
            st.markdown("#### Severity Breakdown")
            severity_data = pd.DataFrame({
                "Severity": ["🔴 Critical (>70%)", "🟡 Warning (50-70%)", "🔵 Monitor (<50%)"],
                "Count": [stats["high_conf"], stats["med_conf"], stats["low_conf"]],
            })
            st.bar_chart(severity_data.set_index("Severity"))

        # Written analysis
        st.markdown("---")
        st.markdown("#### 📝 Findings Summary")

        analysis_text = f"""
**Thermal Anomaly Detection Report — {ROI['name']}**

The satellite-based monitoring system detected **{stats['total_detections']} thermal anomalies**
across **{stats['unique_chips']} tile regions** in the Aqua-Sentinel AI study area.

**Key Findings:**
- **{stats['high_conf']} critical anomalies** (confidence > 70%) — these represent strong thermal
  signatures consistent with industrial discharge or concentrated effluent outlets.
- **{stats['med_conf']} warning-level anomalies** (50-70% confidence) — require field verification.
- **{stats['low_conf']} monitoring-level anomalies** (<50% confidence) — low-intensity thermal
  variations that may be natural or ambient.

**Average Detection Confidence:** {stats['avg_confidence']:.1%}

**Spatial Distribution:**
{stats['geo_located']} of {stats['total_detections']} detections have been geo-referenced with GPS
coordinates and can be visualised on the interactive map.

**Recommendation:**
High-confidence hotspots should be prioritised for ground-truthing by environmental inspectors.
GPS coordinates are available in the downloadable GeoJSON file for field navigation.
"""
        st.markdown(analysis_text)

        # Technology attribution
        st.markdown("---")
        st.markdown("#### 🛰️ Technical Specifications")
        specs = {
            "Satellite": "Landsat 8/9 TIRS (Band 10)",
            "Resolution": "30m (thermal infrared)",
            "AI Model": "YOLOv8 Nano (Ultralytics)",
            "Detection Target": "Multi-spectral water quality anomalies",
            "Study Area": ROI["name"],
            "Coverage": f"{ROI['lat_min']}° - {ROI['lat_max']}° N, {ROI['lon_min']}° - {ROI['lon_max']}° E",
        }
        for key, val in specs.items():
            st.markdown(f"- **{key}:** {val}")

    else:
        st.info("No detections available for analysis. Run the pipeline first.")
        st.markdown("""
        **Quick Start:**
        ```bash
        python run_pipeline.py --demo
        streamlit run dashboard.py
        ```
        """)


# ──────────────────────────────────────────────
# Tab 7: Spectral Analysis
# ──────────────────────────────────────────────
with tab_spectral:
    st.markdown("### 🌈 Spectral Analysis")
    st.markdown("Multi-spectral water quality indices derived from Sentinel-2 MSI imagery.")

    # ── Spectral Index Information ──
    st.markdown("#### Water Quality Indices")
    idx_cols = st.columns(3)

    with idx_cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">🌊</div>
            <div class="metric-value">NDWI</div>
            <div class="metric-label">Normalized Difference Water Index</div>
            <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.5rem;">
                <b>Formula:</b> (Green - NIR) / (Green + NIR)<br>
                <b>Threshold:</b> {SPECTRAL['ndwi_threshold']}<br>
                <b>Purpose:</b> Delineates open water surfaces; values &gt; threshold indicate water pixels.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with idx_cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">🟢</div>
            <div class="metric-value">Chl-a</div>
            <div class="metric-label">Chlorophyll-a (Algal Bloom Proxy)</div>
            <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.5rem;">
                <b>Proxy:</b> NIR / Red band ratio<br>
                <b>Threshold:</b> {SPECTRAL['chlorophyll_threshold']}<br>
                <b>Purpose:</b> High ratios indicate dense algal biomass / eutrophication risk.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with idx_cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">🟤</div>
            <div class="metric-value">Turbidity</div>
            <div class="metric-label">Turbidity Index</div>
            <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.5rem;">
                <b>Proxy:</b> Red band reflectance<br>
                <b>Threshold:</b> {SPECTRAL['turbidity_threshold']}<br>
                <b>Purpose:</b> Higher values indicate murkier, sediment-laden water.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Water Quality Score ──
    st.markdown("#### 💧 Water Quality Score")
    spectral_dir = Path(PREPROCESS.get("spectral_dir", "data/spectral_analysis"))
    wq_score_path = spectral_dir / "water_quality_score.json"

    if wq_score_path.exists():
        with open(wq_score_path, "r") as f:
            wq_data = json.load(f)
        score = wq_data.get("overall_score", None)
        if score is not None:
            score_color = "#44ff44" if score >= 70 else ("#ffaa00" if score >= 40 else "#ff4444")
            st.markdown(f"""
            <div class="metric-card" style="max-width: 300px;">
                <div class="metric-value" style="color: {score_color};">{score:.0f} / 100</div>
                <div class="metric-label">Overall Water Quality Score</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Show component scores if available
            components = wq_data.get("components", {})
            if components:
                comp_cols = st.columns(len(components))
                for col, (name, val) in zip(comp_cols, components.items()):
                    with col:
                        st.metric(name.replace("_", " ").title(), f"{val:.2f}")
        else:
            st.info("Water quality score not computed yet.")
    else:
        st.info("No water quality score data available. Run the spectral analysis pipeline to generate scores.")

    # ── Water Mask Statistics ──
    st.markdown("---")
    st.markdown("#### 🗺️ Water Mask Statistics")
    water_mask_path = spectral_dir / "water_mask_stats.json"

    if water_mask_path.exists():
        with open(water_mask_path, "r") as f:
            mask_stats = json.load(f)

        ms_cols = st.columns(4)
        stat_items = [
            ("Total Pixels", mask_stats.get("total_pixels", "—")),
            ("Water Pixels", mask_stats.get("water_pixels", "—")),
            ("Water Coverage", f"{mask_stats.get('water_fraction', 0):.1%}"),
            ("NDWI Mean", f"{mask_stats.get('ndwi_mean', 0):.4f}"),
        ]
        for col, (label, val) in zip(ms_cols, stat_items):
            with col:
                st.metric(label, val)
    else:
        st.info("No water mask statistics available. Run spectral preprocessing to generate water mask data.")

    # ── Spectral Images ──
    spectral_images = sorted(spectral_dir.glob("*.png")) if spectral_dir.exists() else []
    if spectral_images:
        st.markdown("---")
        st.markdown("#### 📸 Spectral Index Maps")
        sp_cols = st.columns(min(3, len(spectral_images)))
        for i, sp_img_path in enumerate(spectral_images):
            with sp_cols[i % 3]:
                sp_img = Image.open(sp_img_path)
                st.image(sp_img, caption=sp_img_path.stem.replace("_", " ").title(),
                         use_container_width=True)


# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #555; font-size: 0.85rem;'>"
    "🌊 Aqua-Sentinel AI — Hierarchical Geo-Intelligent Water Quality Monitoring • "
    "Landsat 8/9 TIRS + Sentinel-2 MSI + YOLOv8 • "
    f"{ROI.get('name', 'Study Area')}"
    "</div>",
    unsafe_allow_html=True,
)
