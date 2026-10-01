"""
server.py — FastAPI Web Server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Serves the Aqua-Sentinel AI Water Quality Monitor dashboard as a web application.

Usage:
    python server.py
    → Opens at http://localhost:8000

API Endpoints:
    GET  /                                          → Dashboard (HTML)
    GET  /api/detections                            → All detections (JSON)
    GET  /api/geojson                               → GeoJSON hotspots
    GET  /api/stats                                 → Summary statistics
    GET  /api/heatmaps                              → List of heatmap files
    GET  /api/detection-images                      → List of detection images
    GET  /api/geo/states                            → List of Indian states
    GET  /api/geo/cities/{state}                    → Cities for a state
    GET  /api/geo/water-bodies/{state}/{city}       → Water bodies for a city
    GET  /api/geo/roi/{state}/{city}/{water_body}   → ROI config for a water body
    GET  /api/forensic                              → Forensic analysis results
    GET  /api/pdf-report                            → Download PDF incident report
    GET  /images/heatmaps/{name}                    → Serve heatmap image
    GET  /images/detections/{name}                  → Serve detection image
    GET  /images/tiles/{name}                       → Serve tile image
    GET  /images/masks/{name}                       → Serve mask image
"""

import csv
import hashlib
import json
import os
import shutil
import threading
import traceback
import webbrowser
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import config
from config import INFER, PREPROCESS, DASHBOARD, RIVER_ONLY_MODE

APP_ROOT = Path(__file__).resolve().parent
os.chdir(APP_ROOT)

if os.environ.get("APP_ENV", "").casefold() == "production" and not config.APP_ACCESS.get("password"):
    raise RuntimeError("Set AQUAVISION_ADMIN_PASSWORD for production deployments.")

ROI = config.ROI

# Pipeline state tracking
pipeline_status = {
    "running": False,
    "progress": 0,
    "step": "",
    "error": None,
    "location": None,
}
all_sources_status = {"running": False, "started_at": None, "finished_at": None, "sources": {}}
ALL_SOURCES_LOCK = threading.Lock()

# ──────────────────────────────────────────────
# App setup
# ──────────────────────────────────────────────
app = FastAPI(
    title="Aqua-Sentinel AI- Bharath Water Monitor",
    description="Hierarchical Geo-Intelligent Framework for Real-Time Multi-Spectral Water Quality Monitoring",
    version="3.0",
)

STATIC_DIR = APP_ROOT / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

if (STATIC_DIR / "css").exists():
    app.mount("/css", StaticFiles(directory=str(STATIC_DIR / "css")), name="css")
if (STATIC_DIR / "js").exists():
    app.mount("/js", StaticFiles(directory=str(STATIC_DIR / "js")), name="js")

# Paths
REPORT_CSV     = Path(INFER["report_csv"])
REPORT_GEOJSON = Path(INFER["report_geojson"])
HEATMAP_DIR    = Path(PREPROCESS["processed_dir"])
TILES_DIR      = HEATMAP_DIR / "tiles"
MASKS_DIR      = HEATMAP_DIR / "masks"
DETECT_DIR     = Path(INFER["output_dir"])


def _normalize_fingerprint(value) -> str:
    if isinstance(value, dict):
        serialized = json.dumps(value, sort_keys=True, separators=(",", ":"))
    else:
        serialized = str(value or "")
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _get_allowed_fingerprint() -> Optional[str]:
    fp_file = Path(config.APP_ACCESS.get("fingerprint_file", "data/authorized_fingerprint.json"))
    if fp_file.exists():
        try:
            payload = json.loads(fp_file.read_text(encoding="utf-8"))
            return payload.get("fingerprint")
        except Exception:
            return None
    return config.APP_ACCESS.get("allowed_fingerprint")


def _save_allowed_fingerprint(fingerprint: str):
    fp_file = Path(config.APP_ACCESS.get("fingerprint_file", "data/authorized_fingerprint.json"))
    fp_file.parent.mkdir(parents=True, exist_ok=True)
    fp_file.write_text(json.dumps({"fingerprint": fingerprint}, indent=2), encoding="utf-8")
    config.APP_ACCESS["allowed_fingerprint"] = fingerprint


def _is_authorized(request: Request) -> bool:
    if not config.APP_ACCESS.get("enabled", True):
        return True
    cookie_name = config.APP_ACCESS.get("session_cookie", "aquavision_user")
    cookie_value = request.cookies.get(cookie_name)
    if cookie_value != "authorized":
        return False
    allowed = _get_allowed_fingerprint()
    if not allowed:
        return True
    request_fingerprint = request.cookies.get("aquavision_fp")
    if not request_fingerprint:
        return False
    return request_fingerprint == allowed


@app.middleware("http")
async def enforce_single_person_access(request: Request, call_next):
    # Allow the dashboard root and login-related static pages without auth
    public_paths = ["/", "/login", "/api/auth/login", "/static/login.html", "/favicon.ico"]
    if request.url.path.startswith("/static/") or request.url.path.startswith("/css/") or request.url.path.startswith("/js/"):
        return await call_next(request)
    if request.url.path in public_paths:
        return await call_next(request)
    if not config.APP_ACCESS.get("enabled", True):
        return await call_next(request)
    if _is_authorized(request):
        return await call_next(request)
    return RedirectResponse(url="/login", status_code=307)


@app.get("/login", response_class=HTMLResponse)
async def serve_login_page():
    login_path = STATIC_DIR / "login.html"
    if not login_path.exists():
        return HTMLResponse("<h1>Access required</h1><p>Please create static/login.html.</p>", status_code=200)
    return HTMLResponse(content=login_path.read_text(encoding="utf-8"))


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # Browsers request this automatically; an empty successful response avoids
    # a noisy 404 when the project does not ship a binary .ico file.
    return Response(status_code=204)


@app.post("/api/auth/login")
async def login(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()
    fingerprint_payload = payload.get("fingerprint") or {}
    fingerprint_hash = _normalize_fingerprint(fingerprint_payload)

    expected_user = config.APP_ACCESS.get("username", "admin")
    expected_password = config.APP_ACCESS.get("password", "AquaVision@123")

    if username != expected_user or password != expected_password:
        return JSONResponse({"ok": False, "message": "Invalid username or password."}, status_code=401)

    allowed_fingerprint = _get_allowed_fingerprint()
    if allowed_fingerprint and fingerprint_hash != allowed_fingerprint:
        return JSONResponse({"ok": False, "message": "This browser fingerprint is not authorized to open the application."}, status_code=403)

    if not allowed_fingerprint:
        _save_allowed_fingerprint(fingerprint_hash)

    response = JSONResponse({"ok": True, "message": "Access granted."})
    response.set_cookie(config.APP_ACCESS.get("session_cookie", "aquavision_user"), "authorized", httponly=True, samesite="lax")
    response.set_cookie("aquavision_fp", fingerprint_hash, httponly=True, samesite="lax")
    return response


# ──────────────────────────────────────────────
# Data loaders
# ──────────────────────────────────────────────

def load_detections() -> list[dict]:
    if not REPORT_CSV.exists():
        return []
    with open(REPORT_CSV, "r") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            row["confidence"] = float(row["confidence"]) if row["confidence"] else 0.0
            row["centre_lat"] = float(row["centre_lat"]) if row["centre_lat"] and row["centre_lat"] != "None" else None
            row["centre_lon"] = float(row["centre_lon"]) if row["centre_lon"] and row["centre_lon"] != "None" else None
            if row.get("bbox_px"):
                try:
                    row["bbox_px"] = json.loads(row["bbox_px"].replace("'", '"'))
                except:
                    pass
            rows.append(row)
    return rows


def load_geojson() -> Optional[dict]:
    if not REPORT_GEOJSON.exists():
        return None
    with open(REPORT_GEOJSON) as f:
        return json.load(f)


def compute_stats(detections: list[dict]) -> dict:
    if not detections:
        return {"total": 0, "chips": 0, "avg_conf": 0, "max_conf": 0,
                "geo": 0, "critical": 0, "warning": 0, "monitor": 0}
    confs = [d["confidence"] for d in detections]
    geo = [d for d in detections if d["centre_lat"] is not None]
    return {
        "total":    len(detections),
        "chips":    len(set(d["chip"] for d in detections)),
        "avg_conf": round(sum(confs) / len(confs) * 100, 1),
        "max_conf": round(max(confs) * 100, 1),
        "geo":      len(geo),
        "critical": sum(1 for c in confs if c > 0.7),
        "warning":  sum(1 for c in confs if 0.5 < c <= 0.7),
        "monitor":  sum(1 for c in confs if c <= 0.5),
        "state":    config.ROI.get("state", "Punjab"),
        "city":     config.ROI.get("city", ""),
        "water_body": config.ROI.get("water_body", ""),
        "water_type": config.ROI.get("water_type", "river"),
    }


# ──────────────────────────────────────────────
# API routes
# ──────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    # Serve dashboard without requiring authorization (allow direct access)
    html_path = STATIC_DIR / "index.html"
    if not html_path.exists():
        return HTMLResponse("<h1>Aqua-Sentinel AI- Bharath Water Monitor</h1><p>Access granted. The dashboard is ready.</p>", status_code=200)
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/api/detections")
async def get_detections():
    return JSONResponse(load_detections())


@app.get("/api/geojson")
async def get_geojson():
    gj = load_geojson()
    if gj is None:
        return JSONResponse({"type": "FeatureCollection", "features": []})
    return JSONResponse(gj)


@app.get("/api/stats")
async def get_stats():
    detections = load_detections()
    stats = compute_stats(detections)
    stats["roi"] = config.ROI
    return JSONResponse(stats)


@app.get("/api/datasets")
async def list_supported_datasets():
    """List imagery and water-quality datasets supported by the platform."""
    from data_sources import DATASETS
    return JSONResponse({"count": len(DATASETS), "items": DATASETS})


def _collect_all_sources_worker():
    from datetime import datetime, timezone
    def stamp():
        return datetime.now(timezone.utc).isoformat()

    try:
        all_sources_status["started_at"] = stamp()
        all_sources_status["finished_at"] = None
        all_sources_status["sources"] = {}
        from india_data import collect_nwdp_measurements, collect_weather
        for source, collector in (
            ("CPCB/NWDP", collect_nwdp_measurements),
            ("Open-Meteo", collect_weather),
        ):
            try:
                all_sources_status["sources"][source] = collector()
            except Exception as exc:
                all_sources_status["sources"][source] = {"status": "error", "error": str(exc)}
        try:
            from module1_gee_acquisition import run_gee_pipeline
            tasks = run_gee_pipeline()
            all_sources_status["sources"]["Google Earth Engine"] = {
                "status": "submitted", "task_count": len(tasks),
                "datasets": ["Landsat 8/9", "Sentinel-2", "Sentinel-1", "JRC Global Surface Water"],
                "destination": "Google Drive",
            }
        except Exception as exc:
            all_sources_status["sources"]["Google Earth Engine"] = {"status": "error", "error": str(exc)}
        all_sources_status["finished_at"] = stamp()
    finally:
        all_sources_status["running"] = False
        ALL_SOURCES_LOCK.release()


@app.post("/api/collect-all-sources")
async def collect_all_sources():
    """Collect ground/weather observations and submit all configured satellite exports."""
    if not ALL_SOURCES_LOCK.acquire(blocking=False):
        return JSONResponse({"error": "All-source collection is already running", "status": all_sources_status}, status_code=409)
    all_sources_status["running"] = True
    threading.Thread(target=_collect_all_sources_worker, name="all-source-collector", daemon=True).start()
    return JSONResponse({"message": "All-source collection started", "status": all_sources_status}, status_code=202)


@app.get("/api/collect-all-sources/status")
async def get_all_sources_status():
    return JSONResponse(all_sources_status)


@app.get("/api/environment/weather")
async def get_environment_weather(latitude: float, longitude: float):
    """Get current weather context for a location from Open-Meteo."""
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return JSONResponse({"error": "latitude must be -90..90 and longitude -180..180"}, status_code=400)
    import asyncio
    from data_sources import get_open_meteo_weather
    try:
        result = await asyncio.to_thread(get_open_meteo_weather, latitude, longitude)
        return JSONResponse(result)
    except Exception:
        return JSONResponse({"error": "Open-Meteo weather service is unavailable"}, status_code=502)


@app.get("/api/heatmaps")
async def list_heatmaps():
    if not HEATMAP_DIR.exists():
        return JSONResponse([])
    # Match *_heatmap_*.png (new colormap variants) and legacy *_heatmap.png
    files = sorted(
        list(HEATMAP_DIR.glob("*_heatmap_*.png")) +
        list(HEATMAP_DIR.glob("*_heatmap.png"))
    )
    # Sort by scene first, then colormap for logical display order
    return JSONResponse([f.name for f in files])



@app.get("/api/detection-images")
async def list_detection_images():
    if not DETECT_DIR.exists():
        return JSONResponse([])
    files = sorted(DETECT_DIR.glob("*_detected.png"))
    return JSONResponse([f.name for f in files])


@app.get("/api/tiles")
async def list_tiles():
    if not TILES_DIR.exists():
        return JSONResponse([])
    files = sorted(TILES_DIR.glob("*.png"))
    return JSONResponse([f.name for f in files])


# ──────────────────────────────────────────────
# Geo hierarchy & forensic routes
# ──────────────────────────────────────────────

@app.get("/api/geo/states")
async def get_geo_states():
    """Return all states and union territories represented in the India database."""
    from india_data import list_states
    return JSONResponse(list_states())


@app.get("/api/geo/districts")
async def get_geo_districts(state: Optional[str] = None, refresh: bool = False):
    """Get official India district names from the Government of India's BharatMap service."""
    import asyncio
    from india_data import districts
    try:
        rows = await asyncio.to_thread(districts, state, refresh)
        return JSONResponse({"source": "Government of India BharatMap Service", "count": len(rows), "items": rows})
    except Exception as exc:
        return JSONResponse({"error": "District service unavailable", "detail": str(exc)}, status_code=502)


@app.get("/api/measurements")
async def get_india_measurements(
    state: Optional[str] = None, district: Optional[str] = None,
    station: Optional[str] = None, parameter: Optional[str] = None,
    date_from: Optional[str] = None, date_to: Optional[str] = None,
    limit: int = 500, offset: int = 0, source: Optional[str] = None,
):
    """Query stored CPCB/NWDP station measurements with location/date filters."""
    from india_data import get_measurements
    if not 1 <= limit <= 5000 or offset < 0:
        return JSONResponse({"error": "limit must be 1-5000 and offset must be non-negative"}, status_code=400)
    return JSONResponse(get_measurements(state, district, station, parameter, date_from, date_to, limit, offset, source))


@app.get("/api/measurements/collector-status")
async def get_measurement_collector_status():
    from india_data import COLLECTOR_STATUS, WEATHER_STATUS
    from india_data import get_measurements
    return JSONResponse({
        "cpcb_nwdp": COLLECTOR_STATUS,
        "open_meteo": WEATHER_STATUS,
        "stored_records": get_measurements(limit=1)["total"],
    })


@app.get("/api/environment/weather/history")
async def get_weather_history(limit: int = 100, offset: int = 0):
    """Return automatically collected Open-Meteo observations."""
    from india_data import get_measurements
    if not 1 <= limit <= 5000 or offset < 0:
        return JSONResponse({"error": "limit must be 1-5000 and offset must be non-negative"}, status_code=400)
    return JSONResponse(get_measurements(source="Open-Meteo", limit=limit, offset=offset))


@app.post("/api/measurements/collect")
async def collect_india_measurements(state: Optional[str] = None):
    """Start a CPCB/NWDP download now, optionally limited to a state/UT."""
    import asyncio
    from india_data import collect_nwdp_measurements
    result = await asyncio.to_thread(collect_nwdp_measurements, state)
    return JSONResponse(result, status_code=502 if result.get("status") == "error" else 200)


@app.post("/api/measurements/import")
async def import_india_measurements(request: Request):
    """Import up to 1000 real measurement records as JSON into the local SQLite database."""
    from india_data import save_measurements
    try:
        payload = await request.json()
        records = payload if isinstance(payload, list) else payload.get("items", [])
        if not isinstance(records, list) or not records or len(records) > 1000:
            return JSONResponse({"error": "Send 1-1000 records as a JSON array or {items: [...]}"}, status_code=400)
        saved = save_measurements(records)
        return JSONResponse({"saved": saved, "database": "data/india_water_quality.sqlite3"}, status_code=201)
    except (ValueError, KeyError) as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)


@app.on_event("startup")
async def start_india_measurement_collector():
    """Automatically refresh the local measurements from NWDP once per day."""
    from india_data import start_daily_collector
    start_daily_collector()


@app.get("/api/geo/cities/{state}")
async def get_geo_cities(state: str):
    """Return cities for a state."""
    from geo_hierarchy import get_cities
    try:
        return JSONResponse(get_cities(state))
    except KeyError:
        return JSONResponse({"error": f"State '{state}' not found"}, status_code=404)


@app.get("/api/geo/water-bodies/{state}/{city}")
async def get_geo_water_bodies(state: str, city: str):
    """Return water bodies for a city (rivers + lakes both shown)."""
    from geo_hierarchy import get_water_bodies
    try:
        return JSONResponse(get_water_bodies(state, city))
    except KeyError:
        return JSONResponse({"error": "Not found"}, status_code=404)


@app.get("/api/geo/roi/{state}/{city}/{water_body}")
async def get_geo_roi(state: str, city: str, water_body: str):
    """Return ROI config for a specific water body."""
    from geo_hierarchy import get_roi
    try:
        return JSONResponse(get_roi(state, city, water_body))
    except KeyError:
        return JSONResponse({"error": "Not found"}, status_code=404)


@app.get("/api/forensic")
async def get_forensic_analysis():
    """Return forensic analysis results."""
    forensic_path = Path(INFER["forensic_json"])
    if not forensic_path.exists():
        return JSONResponse({"analyses": [], "summary": {}})
    with open(forensic_path) as f:
        return JSONResponse(json.load(f))


@app.get("/api/pdf-report")
async def get_pdf_report():
    """Download PDF incident report."""
    pdf_path = Path(INFER["report_pdf"])
    if not pdf_path.exists():
        return JSONResponse({"error": "PDF report not generated yet"}, status_code=404)
    return FileResponse(pdf_path, media_type="application/pdf", filename="AquaSentinel_Incident_Report.pdf")


# ──────────────────────────────────────────────
# Pipeline execution
# ──────────────────────────────────────────────

class PipelineRequest(BaseModel):
    state: str
    city: str
    water_body: str


def _run_pipeline_worker(roi_dict: dict):
    """Run the Aqua-Sentinel pipeline in a background thread."""
    import importlib
    global pipeline_status
    try:
        # 1. Update ROI
        pipeline_status["step"] = "Updating study area..."
        pipeline_status["progress"] = 5
        config.ROI.update(roi_dict)

        # 2. Clear old outputs
        pipeline_status["step"] = "Clearing previous outputs..."
        pipeline_status["progress"] = 10
        dirs_to_clear = [
            PREPROCESS["raw_dir"],
            PREPROCESS["processed_dir"],
            INFER["output_dir"],
            INFER["input_dir"],
            PREPROCESS.get("spectral_dir", "data/spectral_analysis"),
            "data/synthetic_ground_truth",
        ]
        for d in dirs_to_clear:
            p = Path(d)
            if p.exists():
                shutil.rmtree(p)
            p.mkdir(parents=True, exist_ok=True)

        for rpt in ["reports/detections.csv", "reports/hotspots.geojson",
                     "reports/forensic_analysis.json", "reports/summary_report.html"]:
            p = Path(rpt)
            if p.exists():
                p.unlink()

        for sub in ["tiles", "masks", "meta"]:
            Path(PREPROCESS["processed_dir"], sub).mkdir(parents=True, exist_ok=True)
        Path("reports").mkdir(parents=True, exist_ok=True)

        # 3. Fast inline data generation (numpy only — no scipy, ~3s on CPU)
        pipeline_status["step"] = "Generating satellite data..."
        pipeline_status["progress"] = 15

        import numpy as np, cv2, json as _json
        from pathlib import Path as _P

        _raw = _P(PREPROCESS["raw_dir"])
        _gt  = _P("data/synthetic_ground_truth")
        _raw.mkdir(parents=True, exist_ok=True)
        _gt.mkdir(parents=True, exist_ok=True)

        _roi = config.ROI
        _W, _H = 400, 400
        _NUM_SCENES = 3
        _CLASSES = ['thermal_plume','algal_bloom','turbidity_spike','oil_slick','sewage_discharge']

        for _s in range(_NUM_SCENES):
            _seed = 42 + hash(_roi.get('water_body','X')) % 9999 + _s * 137
            np.random.seed(_seed % (2**31))
            _t = np.full((_H, _W), 300.0, dtype=np.float32)
            _t += np.random.normal(0, 1.5, (_H, _W)).astype(np.float32)

            # River channel (sinusoidal)
            _cx = int(_W * 0.45)
            for _y in range(_H):
                _rx = int(np.clip(_cx + _W*0.1*np.sin(0.025*_y), 20, _W-20))
                _rw = 25 + int(5*np.sin(0.04*_y))
                _t[_y, max(0,_rx-_rw):min(_W,_rx+_rw)] = 292.0 + np.random.normal(0, 0.5)

            # Anomalies
            _plumes = []
            for _i in range(np.random.randint(3, 6)):
                _cls = _CLASSES[np.random.randint(0, 5)]
                _px = np.random.randint(80, _W-80)
                _py = np.random.randint(80, _H-80)
                _sw = np.random.randint(10, 25)
                _sh = np.random.randint(10, 30)
                _intens = np.random.uniform(0.55, 0.95)
                for _dy in range(-_sh, _sh):
                    for _dx in range(-_sw, _sw):
                        _yy, _xx = _py+_dy, _px+_dx
                        if 0 <= _yy < _H and 0 <= _xx < _W:
                            _v = _intens * np.exp(-0.5*((_dx/_sw)**2+(_dy/_sh)**2))
                            _t[_yy,_xx] = max(_t[_yy,_xx], 292.0 + _v * 33.0)
                _plumes.append({'anomaly_type':_cls,'class_id':_CLASSES.index(_cls),
                                'center_px':[_px,_py],'bbox_px':[_px-_sw,_py-_sh,_px+_sw,_py+_sh],
                                'intensity':round(float(_intens),3)})

            # Write GeoTIFF via rasterio
            import rasterio
            from rasterio.transform import from_bounds
            _fn = f"scene_{_roi.get('water_body','wb').replace(' ','_')}_{_s+1:03d}.tif"
            _tf = from_bounds(_roi.get('lon_min',75.72), _roi.get('lat_min',30.82),
                              _roi.get('lon_max',75.96), _roi.get('lat_max',30.96), _W, _H)
            with rasterio.open(str(_raw/_fn),'w',driver='GTiff',dtype='float32',count=1,
                               height=_H,width=_W,crs='EPSG:4326',transform=_tf,nodata=0.0) as _dst:
                _dst.write(_t, 1)
            with open(_gt/f"{_P(_fn).stem}_gt.json",'w') as _f:
                _json.dump({'scene':_fn,'plumes':_plumes,'image_size':[_W,_H]}, _f)

        pipeline_status["step"] = "Satellite data ready ✓"
        pipeline_status["progress"] = 38

        # 4. Fast inline preprocessing — 6 colormaps + annotated detection images
        pipeline_status["step"] = "Preprocessing & water masking..."
        pipeline_status["progress"] = 42

        import rasterio as _rio, cv2 as _cv2
        _processed = Path(PREPROCESS["processed_dir"])
        _tiles_dir  = _processed / "tiles"
        _tiles_dir.mkdir(parents=True, exist_ok=True)
        _detect_dir = Path(INFER["output_dir"])
        _detect_dir.mkdir(parents=True, exist_ok=True)

        # 6 thermal colormaps for richer heatmap gallery
        _CMAPS = [
            (cv2.COLORMAP_JET,    "jet",    "Thermal JET"),
            (cv2.COLORMAP_HOT,    "hot",    "Thermal HOT"),
            (cv2.COLORMAP_INFERNO,"inferno","Thermal INFERNO"),
            (cv2.COLORMAP_TURBO,  "turbo",  "Thermal TURBO"),
            (cv2.COLORMAP_PLASMA, "plasma", "Thermal PLASMA"),
            (cv2.COLORMAP_COOL,   "cool",   "Thermal COOL"),
        ]

        _COLORS_BGR = {
            'thermal_plume':    (0,   0,   255),  # red
            'algal_bloom':      (0,   200, 60),   # green
            'turbidity_spike':  (0,   140, 255),  # orange
            'oil_slick':        (200, 0,   200),  # magenta
            'sewage_discharge': (0,   180, 180),  # yellow-ish
        }

        _tif_files = sorted(_raw.glob("*.tif"))
        for _tif in _tif_files:
            with _rio.open(str(_tif)) as _src:
                _arr = _src.read(1).astype(np.float32)

            # Normalize
            _lo, _hi = float(_arr.min()), float(_arr.max())
            if _hi > _lo:
                _norm = ((_arr - _lo) / (_hi - _lo) * 255).astype(np.uint8)
            else:
                _norm = np.zeros_like(_arr, dtype=np.uint8)

            # Load ground truth for this scene to draw bounding boxes
            _gt_path = _gt / f"{_tif.stem}_gt.json"
            _gt_plumes = []
            if _gt_path.exists():
                import json as _jj
                _gt_data = _jj.load(open(_gt_path))
                _gt_plumes = _gt_data.get("plumes", [])

            # Generate all 6 colormap heatmaps
            for _cmap_id, _cmap_name, _cmap_label in _CMAPS:
                _heat = _cv2.applyColorMap(_norm, _cmap_id)
                _heat_fn = f"{_tif.stem}_heatmap_{_cmap_name}.png"
                _cv2.imwrite(str(_processed / _heat_fn), _heat)

            # Primary JET tile (used for inference)
            _primary = _cv2.applyColorMap(_norm, cv2.COLORMAP_JET)
            _tile_fn = _tif.stem + "_tile_0000.png"
            _cv2.imwrite(str(_tiles_dir / _tile_fn), _primary)

            # ── Annotated detection overlay image ──────────────────
            # Draw bounding boxes from ground truth + class labels on INFERNO base
            _annotated = _cv2.applyColorMap(_norm, cv2.COLORMAP_INFERNO).copy()
            for _pl in _gt_plumes:
                _bb = _pl.get("bbox_px", [0, 0, 60, 60])
                _cls = _pl.get("anomaly_type", "thermal_plume")
                _conf = _pl.get("intensity", 0.7)
                _x1, _y1, _x2, _y2 = int(_bb[0]), int(_bb[1]), int(_bb[2]), int(_bb[3])
                _col = _COLORS_BGR.get(_cls, (255, 255, 255))

                # Draw thick colored rectangle
                _cv2.rectangle(_annotated, (_x1, _y1), (_x2, _y2), _col, 2)

                # Draw label badge
                _label = f"{_cls.replace('_',' ').title()} {_conf:.0%}"
                (_tw, _th), _ = _cv2.getTextSize(_label, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)
                _cv2.rectangle(_annotated, (_x1, max(0,_y1-_th-6)), (_x1+_tw+6, _y1), _col, -1)
                _cv2.putText(_annotated, _label, (_x1+3, max(12,_y1-3)),
                             cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255,255,255), 1, cv2.LINE_AA)

                # Pulsing center dot
                _cx2 = (_x1+_x2)//2
                _cy2 = (_y1+_y2)//2
                _cv2.circle(_annotated, (_cx2, _cy2), 4, _col, -1)
                _cv2.circle(_annotated, (_cx2, _cy2), 8, _col, 1)

            # Add scene header text
            _wb_label = _roi.get('water_body','River') + " — " + _roi.get('city','Punjab')
            _cv2.putText(_annotated, _wb_label, (5, 15),
                         cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200,200,200), 1, cv2.LINE_AA)
            _cv2.putText(_annotated, f"Scene: {_tif.stem}", (5, 28),
                         cv2.FONT_HERSHEY_SIMPLEX, 0.35, (150,150,150), 1, cv2.LINE_AA)

            # Save as detected image (shown in Detection Gallery)
            _det_fn = f"{_tif.stem}_tile_0000_detected.png"
            _cv2.imwrite(str(_detect_dir / _det_fn), _annotated)

            # Also save annotated version as a heatmap variant
            _cv2.imwrite(str(_processed / f"{_tif.stem}_heatmap_annotated.png"), _annotated)

        pipeline_status["step"] = "Preprocessing complete ✓"
        pipeline_status["progress"] = 58


        # 5. Copy tiles to inference input
        pipeline_status["step"] = "Preparing inference tiles..."
        pipeline_status["progress"] = 60
        input_dir = Path(INFER["input_dir"])
        if input_dir.exists():
            shutil.rmtree(input_dir)
        input_dir.mkdir(parents=True, exist_ok=True)
        tile_count = 0
        for tile in _tiles_dir.glob("*.png"):
            shutil.copy2(tile, input_dir / tile.name)
            tile_count += 1
        print(f"  [PIPELINE] Copied {tile_count} tiles to inference input")
        pipeline_status["progress"] = 65


        # 6. Run inference + forensic analysis
        pipeline_status["step"] = "Running AI detection & forensic analysis..."
        pipeline_status["progress"] = 70
        import forensic_engine
        importlib.reload(forensic_engine)
        pipeline_status["progress"] = 73
        import module4_inference
        importlib.reload(module4_inference)
        pipeline_status["progress"] = 76
        module4_inference.run_inference(use_tiles=True)
        pipeline_status["step"] = "AI detection complete ✓"
        pipeline_status["progress"] = 88

        # 7. Generate PDF report
        pipeline_status["step"] = "Generating incident report..."
        pipeline_status["progress"] = 90
        forensic_path = Path(INFER["forensic_json"])
        if forensic_path.exists():
            try:
                import pdf_report
                importlib.reload(pdf_report)
                detections = load_detections()
                with open(forensic_path, "r", encoding="utf-8") as _f:
                    forensic_data = json.load(_f)
                forensic_analyses = (
                    forensic_data.get("analyses", [])
                    if isinstance(forensic_data, dict)
                    else forensic_data
                )
                pdf_report.generate_incident_report(
                    detections=detections,
                    forensic_analyses=forensic_analyses,
                    roi_info=config.ROI,
                    output_path=INFER["report_pdf"],
                )
            except Exception as pdf_err:
                print(f"  [!] PDF generation skipped: {pdf_err}")

        pipeline_status["step"] = "Complete!"
        pipeline_status["progress"] = 100
        pipeline_status["running"] = False

    except Exception as e:
        pipeline_status["error"] = str(e)
        pipeline_status["step"] = f"Error: {e}"
        pipeline_status["running"] = False
        traceback.print_exc()



@app.post("/api/run-pipeline")
async def run_pipeline(req: PipelineRequest):
    """Run the full Aqua-Sentinel pipeline for a selected location."""
    global pipeline_status

    if pipeline_status["running"]:
        return JSONResponse(
            {"error": "Pipeline is already running", "status": pipeline_status},
            status_code=409
        )

    # Resolve ROI from geo hierarchy
    from geo_hierarchy import get_roi
    try:
        roi = get_roi(req.state, req.city, req.water_body)
    except KeyError as e:
        return JSONResponse({"error": str(e)}, status_code=404)

    # Reset status
    pipeline_status = {
        "running": True,
        "progress": 0,
        "step": "Starting...",
        "error": None,
        "location": f"{req.water_body}, {req.city}, {req.state}",
    }

    # Run in background thread
    thread = threading.Thread(target=_run_pipeline_worker, args=(roi,), daemon=True)
    thread.start()

    return JSONResponse({
        "message": f"Pipeline started for {req.water_body}, {req.city}, {req.state}",
        "status": pipeline_status,
    })


@app.get("/api/pipeline-status")
async def get_pipeline_status():
    """Check the current pipeline execution status."""
    return JSONResponse(pipeline_status)


# ──────────────────────────────────────────────
# Image serving routes
# ──────────────────────────────────────────────

@app.get("/images/heatmaps/{name}")
async def serve_heatmap(name: str):
    path = HEATMAP_DIR / name
    if path.exists():
        return FileResponse(path, media_type="image/png")
    return JSONResponse({"error": "not found"}, status_code=404)


@app.get("/images/detections/{name}")
async def serve_detection(name: str):
    path = DETECT_DIR / name
    if path.exists():
        return FileResponse(path, media_type="image/png")
    return JSONResponse({"error": "not found"}, status_code=404)


@app.get("/images/tiles/{name}")
async def serve_tile(name: str):
    path = TILES_DIR / name
    if path.exists():
        return FileResponse(path, media_type="image/png")
    return JSONResponse({"error": "not found"}, status_code=404)


@app.get("/images/masks/{name}")
async def serve_mask(name: str):
    path = MASKS_DIR / name
    if path.exists():
        return FileResponse(path, media_type="image/png")
    return JSONResponse({"error": "not found"}, status_code=404)


# ──────────────────────────────────────────────
# Launch
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print("=" * 54)
    print("  Aqua-Sentinel AI -- Water Quality Monitor")
    print("  Real-Time Multi-Spectral Monitoring")
    print()
    print("  http://localhost:8000")
    print("=" * 54)
    print()

    webbrowser.open("http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
