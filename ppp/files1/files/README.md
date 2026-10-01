# Aqua-Sentinel AI

### A Hierarchical Geo-Intelligent Framework for Real-Time Multi-Spectral Water Quality Monitoring & Forensic Anomaly Reporting

> An end-to-end **Geospatial Intelligence (GEOINT)** platform that automates the monitoring
> of India's hydrological assets using satellite telemetry, spectral reasoning, and
> explainable AI to detect and classify water pollution with surgical-grade precision.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF?logo=yolo&logoColor=white)
![Sentinel-2](https://img.shields.io/badge/Sentinel--2-MSI-4285F4?logo=satellite&logoColor=white)
![Landsat](https://img.shields.io/badge/Landsat_8/9-TIRS-FF6B6B?logo=google-earth&logoColor=white)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)

---

## System Architecture

```
                    +-------------------------------------------+
                    |       AQUA-SENTINEL AI PLATFORM           |
                    +-------------------------------------------+
                                      |
          +---------------------------+---------------------------+
          |                           |                           |
  +-------v--------+     +-----------v-----------+    +----------v---------+
  | Module A        |     | Module B               |    | Module C            |
  | Hierarchical    |     | Live Telemetry         |    | Hydrological        |
  | Spatial         |     | Acquisition            |    | Masking & Noise     |
  | Navigation      |     | Pipeline               |    | Reduction           |
  | (State/City/    |     | (Landsat 8/9 TIRS +    |    | (NDWI Water Mask)   |
  |  Water Body)    |     |  Sentinel-2 MSI)       |    |                     |
  +-----------------+     +------------------------+    +---------------------+
                                      |                           |
                          +-----------v---------------------------v---------+
                          |                                                  |
                          |        Module D: AI Detection &                  |
                          |        Forensic Reasoning Engine                 |
                          |  +-------------------------------------------+  |
                          |  | YOLOv8-Seg  |  Heuristic Reasoning Engine |  |
                          |  | (5-Class    |  (Pollution Source           |  |
                          |  |  Detector)  |   Classification)           |  |
                          |  +-------------------------------------------+  |
                          |                                                  |
                          +--------------------------------------------------+
                                      |
                    +-----------------v------------------+
                    | Module E: Interactive GIS          |
                    | Intelligence Dashboard             |
                    | (Streamlit + FastAPI + Leaflet)     |
                    | + PDF Incident Report Generator     |
                    +------------------------------------+
```

---

## Core Modules

### Module A: Hierarchical Spatial Navigation
- Multi-tier selection engine: **State -> City -> Water Body**
- Covers **15+ Indian states**, **30+ cities**, **40+ rivers/lakes**
- Automatic ROI (Region of Interest) bounding box generation
- Uses OpenStreetMap coordinate references

### Module B: Live Telemetry Acquisition Pipeline
- **Landsat 8/9 TIRS**: Surface Temperature anomalies (thermal effluent)
- **Sentinel-2 MSI**: Turbidity, Algal Blooms (Chlorophyll-a), Oil Slicks
- Cloud-masked, date-filtered, clear-sky imagery
- Demo mode with physics-inspired synthetic data generator

### Module C: Hydrological Masking & Noise Reduction
- **NDWI (Normalized Difference Water Index)**: `NDWI = (Green - NIR) / (Green + NIR)`
- Binary water mask ensures AI processes **only water surfaces**
- Eliminates false positives from roads, buildings, and rooftops
- Morphological refinement for clean boundaries

### Module D: AI Detection & Forensic Reasoning Engine
- **YOLOv8-Segmentation** trained on 5 anomaly classes:
  1. Thermal Plume (industrial coolant discharge)
  2. Algal Bloom (eutrophication / fertilizer runoff)
  3. Turbidity Spike (siltation / construction runoff)
  4. Oil Slick (chemical spill / petroleum)
  5. Sewage Discharge (organic waste / untreated effluent)

- **Heuristic Reasoning Engine** for pollution source identification:
  - `Temp > +8C + Industrial Zone < 500m` -> "Untreated Industrial Coolant Discharge"
  - `High Turbidity + Brown/Opaque color` -> "Siltation or Construction Runoff"
  - `High Chlorophyll-a + Stagnant Lake` -> "Eutrophication (Fertilizer Overload)"
  - `High SWIR/NIR Ratio` -> "Oil Slick or Chemical Spill"
  - `Chlorophyll + Turbidity + Mild Thermal` -> "Untreated Sewage Discharge"

### Module E: Interactive GIS Intelligence Dashboard
- **Live Reporting**: Interactive map with high-accuracy GPS coordinates
- **Forensic Analysis Panel**: Step-by-step reasoning chains with evidence
- **Spectral Analysis View**: NDWI, Chlorophyll-a, Turbidity, Oil Index metrics
- **PDF Incident Reports**: Automated for environmental agencies with time-stamped evidence

---

## Quick Start (Demo Mode -- No API Keys Needed)

```bash
# 1. Clone & install
git clone <your-repo-url>
cd aqua-sentinel-ai
python -m venv venv
venv\Scripts\activate           # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt

# 2. Run the full pipeline (synthetic data -> train -> detect -> forensic analysis)
python run_pipeline.py --demo

# 3. Launch the interactive dashboard (choose one)
streamlit run dashboard.py          # Streamlit dashboard
python server.py                    # FastAPI web dashboard (http://localhost:8000)
```

## Deploy a free preview on Render

The repository includes a root-level `render.yaml` Blueprint for a Docker
web service in Render's Singapore region. Connect the GitHub repository to
Render and deploy the Blueprint. Render will prompt for
`AQUAVISION_ADMIN_PASSWORD`; use a unique password for the public preview.
The deployment excludes the local Punjab training archive from the Docker
build context.

This free preview sleeps after 15 minutes without traffic and has ephemeral
storage. Local SQLite records, generated reports, and collected observations
can be lost when the service restarts or sleeps. Persistent collection needs
a paid service with persistent storage or a managed database.

---

## Project Structure

```
aqua-sentinel-ai/
|
|-- config.py                        <- Central configuration (all parameters)
|-- run_pipeline.py                  <- Unified pipeline runner (6 steps)
|
|-- geo_hierarchy.py                 <- Module A: State/City/Water Body database
|-- spectral_indices.py              <- Module C: NDWI, Chlorophyll-a, Turbidity, Oil Index
|-- water_masking.py                 <- Module C: NDWI-based water body masking
|-- forensic_engine.py               <- Module D: Forensic Reasoning Engine
|-- pdf_report.py                    <- PDF incident report generator
|
|-- generate_synthetic_data.py       <- Multi-class synthetic GeoTIFF generator
|-- generate_training_dataset.py     <- Multi-class auto-annotation (masks -> YOLO labels)
|
|-- module1_gee_acquisition.py       <- Module B: GEE + Sentinel-2 data acquisition
|-- module2_preprocessing.py         <- GeoTIFF -> NDWI mask -> heatmap tiles
|-- module3_train_yolov8.py          <- YOLOv8 multi-class training
|-- module4_inference.py             <- Inference + forensic analysis + reporting
|
|-- dashboard.py                     <- Streamlit web dashboard
|-- dashboard_utils.py               <- Dashboard helper functions
|-- server.py                        <- FastAPI web server + REST API
|
|-- static/
|   |-- index.html                   <- FastAPI dashboard frontend
|   |-- css/style.css                <- Premium dark theme
|   |-- js/app.js                    <- Frontend application logic
|
|-- requirements.txt
|-- yolov8n.pt                       <- Pre-trained YOLOv8 nano weights
|
|-- data/
|   |-- raw_geotiff/                 <- Satellite GeoTIFFs (synthetic or real)
|   |-- synthetic_ground_truth/      <- Plume locations + class labels (JSON)
|   |-- processed_heatmaps/
|   |   |-- tiles/                   <- 640x640 JET heatmap chips
|   |   |-- masks/                   <- Binary anomaly masks
|   |   |-- meta/                    <- Per-chip geo-metadata JSON
|   |-- spectral_analysis/           <- NDWI water mask stats
|   |-- dataset/                     <- YOLO-format multi-class training data
|   |-- inference_input/
|   |-- inference_output/
|
|-- runs/aqua_sentinel_v1/           <- Training artefacts (auto-created)
|   |-- weights/best.pt              <- Best model weights
|
|-- reports/
    |-- detections.csv               <- All detections with confidence scores
    |-- hotspots.geojson             <- GPS-located hotspots (GIS import)
    |-- forensic_analysis.json       <- Forensic reasoning results
    |-- summary_report.html          <- Visual HTML report
    |-- incident_report.pdf          <- PDF report for agencies
```

---

## Running the Pipeline

### One-command run (recommended)

```bash
python run_pipeline.py                          # Full demo pipeline
python run_pipeline.py --epochs 10              # Quick test (10 epochs)
python run_pipeline.py --skip-training          # Skip training, use existing weights
python run_pipeline.py --module 2               # Run only preprocessing
python run_pipeline.py --state Punjab --city Ludhiana --water-body "Buddha Dariya"
```

### Individual modules

```bash
# Step 1 -- Generate synthetic satellite data
python generate_synthetic_data.py

# Step 2 -- Preprocess into NDWI-masked heatmap tiles
python module2_preprocessing.py

# Step 3 -- Auto-annotate (multi-class masks -> YOLO labels)
python generate_training_dataset.py

# Step 4 -- Train YOLOv8 (5 anomaly classes)
python module3_train_yolov8.py --epochs 50

# Step 5 -- Run inference + forensic analysis
python module4_inference.py --use-tiles

# Step 6 -- Launch dashboard
streamlit run dashboard.py
# OR
python server.py
```

---

## API Endpoints (FastAPI Server)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web dashboard |
| GET | `/api/detections` | All detections (JSON) |
| GET | `/api/geojson` | GeoJSON hotspots |
| GET | `/api/stats` | Summary statistics |
| GET | `/api/forensic` | Forensic analysis results |
| GET | `/api/pdf-report` | Download PDF incident report |
| GET | `/api/geo/states` | List of Indian states |
| GET | `/api/geo/districts?state=Punjab` | Official BharatMap districts; omit state for all India |
| GET | `/api/geo/cities/{state}` | Cities in a state |
| GET | `/api/geo/water-bodies/{state}/{city}` | Water bodies near a city |
| GET | `/api/geo/roi/{state}/{city}/{name}` | ROI config for a water body |
| GET | `/api/heatmaps` | Heatmap image list |
| GET | `/api/detection-images` | Detection image list |
| GET | `/api/measurements?state=Punjab&district=Ludhiana&parameter=pH` | Filter stored surface-water measurements |
| GET | `/api/measurements/collector-status` | Automatic collection status and stored record count |
| POST | `/api/measurements/collect?state=Punjab` | Immediately download current CPCB/NWDP CSVs (omit state for India-wide collection) |
| POST | `/api/measurements/import` | Import 1-1000 CPCB/NWDP observation records as JSON |

### India-wide geography and measurements

The state/UT list comes from the project's India geography database. District names are looked up from the Government of India's [BharatMap district service](https://mapservice.gov.in/gismapservice/rest/services/BharatMapService/Admin_Boundary_District/MapServer/1), cached for one day, and can be refreshed with `?refresh=true`.

Water quality measurements are real CPCB observations published through the [National Water Data Portal](https://www.nwdp.nwic.gov.in/dataset/surface-water-quality-manual-chemical-parameters-cpcb). At server startup, a background collector discovers state and union territory CSV resources and imports recognizable station-level measurements. It repeats every 24 hours. To collect on demand, call `POST /api/measurements/collect`; optionally pass `?state=Punjab`. The application stores imported records in `data/india_water_quality.sqlite3`; empty locations have no fabricated readings. Check `/api/measurements/collector-status` for progress and errors. NWDP currently publishes manual sampling datasets in period-based CSV resources, so update frequency depends on CPCB/NWDP publication rather than live sensors.

```json
{
  "items": [
    {
      "state": "Punjab",
      "district": "Ludhiana",
      "station": "CPCB station name",
      "measured_at": "2024-06-15",
      "parameter": "pH",
      "value": 7.2,
      "unit": "pH",
      "source": "CPCB/NWDP",
      "source_url": "https://www.nwdp.nwic.gov.in/dataset/surface-water-quality-manual-chemical-parameters-cpcb"
    }
  ]
}
```

The measurement endpoint supports `state`, `district`, `station`, `parameter`, `date_from`, `date_to`, `limit` (up to 5000), and `offset` filters. The import route uses the server's existing access middleware; keep it behind authentication when deployed.

---

## Dashboard Features

| Feature | Description |
|---------|-------------|
| Hotspot Map | Interactive Leaflet map with anomaly-type-colored markers |
| Heatmap Gallery | Thermal heatmaps with NDWI water mask overlays |
| Detection Gallery | YOLOv8 annotated tiles with multi-class bounding boxes |
| Forensic Analysis | Step-by-step reasoning chains for each detected anomaly |
| Detection Log | Sortable table with CSV/GeoJSON download |
| Analysis Report | Automated severity breakdown and findings summary |
| Spectral Indices | NDWI, Chlorophyll-a, Turbidity, Oil Index metrics |
| Geo Navigation | State -> City -> Water Body hierarchical selection |
| PDF Reports | One-click PDF incident report for agencies |

---

## Anomaly Classes

| Class | Detection Target | Spectral Indicator |
|-------|------------------|--------------------|
| Thermal Plume | Industrial coolant discharge | Landsat TIRS (Band 10) |
| Algal Bloom | Eutrophication / fertilizer runoff | Sentinel-2 NDCI (B5/B4) |
| Turbidity Spike | Siltation / construction runoff | Sentinel-2 Red (B4) |
| Oil Slick | Chemical spill / petroleum | Sentinel-2 SWIR/NIR (B11/B8) |
| Sewage Discharge | Organic waste / untreated effluent | Multi-band composite |

---

## Spectral Indices

| Index | Formula | Purpose |
|-------|---------|---------|
| **NDWI** | `(Green - NIR) / (Green + NIR)` | Water body identification |
| **Chlorophyll-a** | `NIR / Red` or `NDCI = (RedEdge - Red) / (RedEdge + Red)` | Algal bloom detection |
| **Turbidity** | Red band reflectance | Suspended sediment detection |
| **Oil Index** | `SWIR1 / NIR` | Oil slick identification |
| **Thermal Anomaly** | `T_pixel - T_baseline > 8C` | Industrial discharge detection |

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.10+ |
| Cloud Engine | Google Earth Engine API (GEE) |
| Satellite Data | Landsat 8/9 TIRS + Sentinel-2 MSI |
| Deep Learning | Ultralytics YOLOv8 / PyTorch |
| Geospatial | GDAL, Rasterio, GeoPandas, Shapely |
| Spectral Analysis | NumPy, OpenCV, SciPy |
| Forensic Engine | Custom Heuristic Reasoning System |
| Dashboard | Streamlit / FastAPI / Leaflet.js |
| Reporting | fpdf2 (PDF) / GeoJSON / HTML / CSV |
| Visualisation | Matplotlib, Seaborn, Chart.js |

---

## Demo Mode vs Production Mode

| Feature | Demo Mode | Production Mode |
|---------|-----------|-----------------|
| Data Source | Synthetic GeoTIFFs | Google Earth Engine (real satellite) |
| Sensors | Simulated thermal | Landsat 8/9 + Sentinel-2 |
| API Keys | None required | GEE auth required |
| Setup Time | Instant | 10-15 minutes |
| Command | `python run_pipeline.py --demo` | `python run_pipeline.py --production` |

### Switching to Production

1. Install GEE: `pip install earthengine-api && earthengine authenticate`
2. Set `DEMO_MODE = False` in `config.py`
3. Run: `python run_pipeline.py --production`

---

## Future Roadmap

| Feature | Status |
|---------|--------|
| Predictive Forecasting (LSTM networks) | Planned |
| Automated Email/Telegram alerts | Planned |
| SAR Integration (Sentinel-1 for night/cloud) | Research |
| Multi-river temporal trend analysis | Planned |
| Cloud deployment (Streamlit Cloud) | Ready |
| Real-time monitoring dashboard | Planned |

---

## Strategic Value

This project represents a shift from **passive observation to active environmental forensics**.
It demonstrates mastery in:

- **Big Data & Remote Sensing** -- Processing multi-spectral satellite imagery at scale
- **Explainable AI (XAI)** -- Transparent reasoning chains for every pollution classification
- **Geospatial Intelligence** -- Hierarchical navigation across India's entire hydrological network
- **Environmental Forensics** -- Evidence-based pollution source identification
- **Full-Stack Engineering** -- From satellite data to interactive dashboards and PDF reports

---

## License

MIT -- feel free to adapt for other rivers, countries, and pollutants.
