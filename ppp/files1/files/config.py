"""
config.py -- Central Configuration for Aqua-Sentinel AI
========================================================
A Hierarchical Geo-Intelligent Framework for Real-Time
Multi-Spectral Water Quality Monitoring & Forensic Anomaly Reporting

All parameters for GEE, Sentinel-2, preprocessing, training,
inference, forensic reasoning, and the GIS dashboard.
"""

import os

# -----------------------------------------------------
# 0. MODE -- Demo vs Production
# -----------------------------------------------------
DEMO_MODE = True   # Set False when using real GEE credentials

# -----------------------------------------------------
# 0b. WATER BODY MODE -- Detect anomalies ONLY in water bodies
# ---------------------------------------------------------------
# When True, the entire pipeline enforces water-body-only detection:
#   - Synthetic data places ALL anomalies strictly inside water channels
#   - Water masking covers rivers, lakes, wetlands, reservoirs
#   - Inference rejects any detection NOT on a water pixel
#   - Punjab coverage: Sutlej, Beas, Ravi, Ghaggar, Buddha Dariya,
#     Harike Wetland, Kanjli Wetland, Bhakra-Nangal, Pong Dam...
#   - Training covers all 33 Punjab cities, 43 rivers + 8 lakes
RIVER_ONLY_MODE = True   # kept True for backwards compat; applies to all water bodies

# -----------------------------------------------------
# 1. DEFAULT STUDY AREA -- Buddha Dariya, Ludhiana, Punjab
#    (Overridden at runtime by hierarchical geo selection)
#    Buddha Dariya is Punjab's most polluted nullah — industrial discharge
#    flows from Ludhiana's dyeing/electroplating industries.
# -----------------------------------------------------
ROI = {
    "name": "Buddha Dariya, Ludhiana",
    "state": "Punjab",
    "city": "Ludhiana",
    "water_body": "Buddha Dariya",
    "water_type": "river",          # river | lake | wetland | reservoir
    "lon_min": 75.80,
    "lat_min": 30.88,
    "lon_max": 75.94,
    "lat_max": 30.95,
}

# -----------------------------------------------------
# 1b. SINGLE-USER ACCESS CONTROL
#     First successful login stores the approved browser fingerprint.
#     Only that one fingerprint can open the application afterwards.
# -----------------------------------------------------
APP_ACCESS = {
    "enabled": True,
    "username": "admin",
    "password": (
        os.environ.get("AQUAVISION_ADMIN_PASSWORD")
        if os.environ.get("APP_ENV", "").casefold() == "production"
        else os.environ.get("AQUAVISION_ADMIN_PASSWORD", "AquaVision@123")
    ),
    "allowed_fingerprint": None,
    "session_cookie": "aquavision_user",
    "fingerprint_file": "data/authorized_fingerprint.json",
}

# -----------------------------------------------------
# 2. GOOGLE EARTH ENGINE -- Landsat 8/9 TIRS
# -----------------------------------------------------
GEE = {
    "collection_l8": "LANDSAT/LC08/C02/T1_L2",
    "collection_l9": "LANDSAT/LC09/C02/T1_L2",
    "thermal_band": "ST_B10",
    "scale_factor": 0.00341802,
    "add_offset": 149.0,
    "cloud_cover_max": 20,
    "date_start": "2022-01-01",
    "date_end":   "2024-12-31",
    "export_scale_m": 30,
    "drive_folder": "AquaSentinel_Thermal",
}

# -----------------------------------------------------
# 3. SENTINEL-2 MSI -- Multi-Spectral Imaging
# -----------------------------------------------------
SENTINEL2 = {
    "collection": "COPERNICUS/S2_SR_HARMONIZED",
    "cloud_cover_max": 15,
    "date_start": "2022-01-01",
    "date_end":   "2024-12-31",
    "export_scale_m": 10,
    "drive_folder": "AquaSentinel_Spectral",
    # Band mappings (Sentinel-2 Level-2A)
    "bands": {
        "blue":    "B2",    # 490 nm  -- 10m
        "green":   "B3",    # 560 nm  -- 10m
        "red":     "B4",    # 665 nm  -- 10m
        "red_edge":"B5",    # 705 nm  -- 20m
        "nir":     "B8",    # 842 nm  -- 10m
        "nir_narrow": "B8A",# 865 nm  -- 20m
        "swir1":   "B11",   # 1610 nm -- 20m
        "swir2":   "B12",   # 2190 nm -- 20m
    },
}

# -----------------------------------------------------
# 4. SPECTRAL INDICES -- Water Quality Parameters
# -----------------------------------------------------
SPECTRAL = {
    # NDWI (Normalized Difference Water Index)
    # NDWI = (Green - NIR) / (Green + NIR)
    "ndwi_threshold": 0.2,         # pixels > threshold = water

    # Chlorophyll-a / Algal Bloom Proxy
    # Uses band ratio: NIR / Red
    "chlorophyll_threshold": 1.8,  # high ratio = dense algae

    # Turbidity Index (higher = murkier)
    # Uses Red band reflectance
    "turbidity_threshold": 0.15,   # reflectance threshold

    # Oil Slick Detection
    # Uses SWIR1/NIR ratio
    "oil_slick_threshold": 1.5,    # high ratio = oily surface

    # Thermal Anomaly (from Landsat TIRS)
    "thermal_anomaly_delta_k": 8.0,  # degrees above baseline
}

# -----------------------------------------------------
# 5. FORENSIC REASONING ENGINE -- Pollution Classification
# -----------------------------------------------------
FORENSIC = {
    # Scenario 1: Industrial Thermal Discharge
    "thermal_discharge": {
        "temp_delta_min": 8.0,          # deg C above baseline
        "industrial_zone_dist_m": 500,  # max distance to industrial zone
        "verdict": "Likely Untreated Industrial Coolant Discharge",
        "severity": "CRITICAL",
        "icon": "factory",
    },
    # Scenario 2: Siltation / Construction Runoff
    "siltation_runoff": {
        "turbidity_min": 0.15,
        "color_signature": "brown",     # brown/opaque water
        "verdict": "Probable Siltation or Construction Runoff",
        "severity": "WARNING",
        "icon": "construction",
    },
    # Scenario 3: Eutrophication / Algal Bloom
    "eutrophication": {
        "chlorophyll_min": 1.8,
        "water_type": "stagnant",       # lake or slow-moving
        "verdict": "Eutrophication due to Nutrient (Fertilizer) Overload",
        "severity": "WARNING",
        "icon": "algae",
    },
    # Scenario 4: Oil Slick / Chemical Spill
    "oil_spill": {
        "oil_index_min": 1.5,
        "iridescence": True,
        "verdict": "Potential Oil Slick or Chemical Spill Detected",
        "severity": "CRITICAL",
        "icon": "oil",
    },
    # Scenario 5: Sewage / Organic Waste Discharge
    "sewage_discharge": {
        "chlorophyll_min": 1.2,
        "turbidity_min": 0.10,
        "temp_delta_min": 3.0,
        "verdict": "Suspected Untreated Sewage or Organic Waste Discharge",
        "severity": "HIGH",
        "icon": "sewage",
    },
}

# -----------------------------------------------------
# 6. SYNTHETIC DATA GENERATION
# -----------------------------------------------------
SYNTHETIC = {
    "num_scenes":           3,       # WEB-INTERACTIVE: 3 scenes — completes in ~30s on CPU
    "image_width":          400,     # WEB-INTERACTIVE: 400px — fast generation
    "image_height":         400,     # WEB-INTERACTIVE: 400px
    "base_temp_k":          300.0,
    "river_temp_k":         292.0,
    "urban_temp_k":         308.0,
    "plume_temp_k":         325.0,
    "plume_count_range":    (3, 6),
    "noise_octaves":        5,
    "noise_amplitude":      4.0,
    "river_width_px":       30,
    "nodata_border_px":     10,
    "crs":                  "EPSG:32643",
    "generate_multispectral": True,
    "force_plumes_in_river": True,
    "anomaly_types": [
        "thermal_plume",
        "algal_bloom",
        "turbidity_spike",
        "oil_slick",
        "sewage_discharge",
    ],
}

# -----------------------------------------------------
# 7. PREPROCESSING
# -----------------------------------------------------
PREPROCESS = {
    "raw_dir":       "data/raw_geotiff",
    "processed_dir": "data/processed_heatmaps",
    "spectral_dir":  "data/spectral_analysis",
    "nodata_value":  0,
    "temp_min_k":    270.0,
    "temp_max_k":    330.0,
    "anomaly_delta_k": 3.0,
    "colormap":      "JET",
    "tile_size":     640,
    "tile_overlap":  64,
    # NDWI water mask settings
    "apply_water_mask": True,
    "ndwi_threshold": 0.2,
    # River-only: strict river channel masking (tighter percentile)
    "river_mask_percentile": 12,
    # Extra heatmap generation
    "generate_extra_heatmaps": True,
    "heatmap_colormaps": ["JET", "INFERNO", "HOT", "TURBO", "OCEAN"],
}

# -----------------------------------------------------
# 8. DATASET & ANNOTATION
# -----------------------------------------------------
DATASET = {
    "roboflow_workspace": "your-workspace",
    "roboflow_project":   "aqua-sentinel-water-quality",
    "roboflow_version":   1,
    "dataset_dir":        "data/dataset",
    "class_names": [
        "thermal_plume",
        "algal_bloom",
        "turbidity_spike",
        "oil_slick",
        "sewage_discharge",
    ],
    "split_ratios": {"train": 0.75, "val": 0.15, "test": 0.10},
}

# -----------------------------------------------------
# 9. YOLOV8 TRAINING
# -----------------------------------------------------
TRAIN = {
    "model_variant":  "yolov8n.pt",    # YOLOv8 Nano — optimised for water body detection
    "epochs":         100,              # Full 100-epoch training (use --quick for 30)
    "imgsz":          640,
    "batch":          8,                # batch=8 on CPU; 16 on GPU
    "lr0":            0.01,
    "lrf":            0.001,
    "patience":       20,
    "project_dir":    "runs",
    "run_name":       "punjab_water_bodies_v1",
    "device":         "",               # auto-detect GPU, fall back to CPU
    "conf_thres":     0.10,             # Low threshold to catch subtle aquatic anomalies
    "iou_thres":      0.50,
    "warmup_epochs":  5,
    "weight_decay":   0.0005,
    "optimizer":      "AdamW",
    "cos_lr":         True,
    "close_mosaic":   15,
    "multi_scale":    False,
    # Water-specific augmentation
    "mixup":          0.10,
    "copy_paste":     0.05,
    "degrees":        10.0,             # River meander variation
    "scale":          0.30,             # Zoom for different water body sizes
    "hsv_s":          0.40,             # Turbidity / clarity variation
    "hsv_v":          0.40,             # Shadow / sky reflection variation
}

# -----------------------------------------------------
# 10. INFERENCE & REPORTING
# -----------------------------------------------------
INFER = {
    "best_weights":   "runs/detect/runs/punjab_water_bodies_v1/weights/best.pt",
    "input_dir":      "data/inference_input",
    "output_dir":     "data/inference_output",
    "conf_thres":     0.10,
    "report_csv":     "reports/detections.csv",
    "report_geojson": "reports/hotspots.geojson",
    "report_html":    "reports/summary_report.html",
    "report_pdf":     "reports/incident_report.pdf",
    "forensic_json":  "reports/forensic_analysis.json",
    # STRICT water-body enforcement during inference
    # Rejects ANY detection that is not overlapping a water pixel
    "min_water_fraction": 0.40,      # 40% of bbox must be water pixels
    "river_only_filter":  True,       # Reject detections outside water body
    # Gallery settings
    "max_gallery_images": 24,
    "gallery_cols":       4,
}

# -----------------------------------------------------
# 11. DASHBOARD
# -----------------------------------------------------
DASHBOARD = {
    "title":     "Aqua-Sentinel AI- Bharath Water Monitor",
    "subtitle":  "AI-Powered Water Body Anomaly Detection — All 33 Punjab Cities | Rivers, Lakes & Wetlands",
    "port":      8000,
    "state":     "Punjab",             # Locked to Punjab
    "map_center_lat":  31.10,          # Centred on Punjab
    "map_center_lon":  75.34,
    "map_zoom":        8,              # Zoom to show all of Punjab
}
