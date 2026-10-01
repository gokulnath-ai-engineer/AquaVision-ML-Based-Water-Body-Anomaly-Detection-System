---
layout: default
title: API Reference
---

# API Reference

Complete API documentation for Aqua-Sentinel AI.

---

## Main Entry Point

### `run_pipeline.py`

```python
python run_pipeline.py [OPTIONS]
```

**Options:**
- `--demo` - Run with synthetic data
- `--module {1,2,3,4}` - Run specific module
- `--skip-training` - Skip Module 3
- `--epochs N` - Number of training epochs
- `--batch_size N` - Batch size
- `--state NAME` - Geographic state
- `--city NAME` - City name
- `--water-body NAME` - Water body name

## Dataset and environmental data APIs

The FastAPI server exposes a catalogue of the imagery and in-situ datasets
that the project can use:

```http
GET /api/datasets
```

The catalogue includes Sentinel-2 surface reflectance, Landsat 8/9 Level-2,
Sentinel-1 GRD, JRC Global Surface Water, and CPCB/NWDP station measurements.
Earth Engine imagery exports require Earth Engine authentication. Sentinel-1
and JRC exports are started with the existing Module 1 GEE acquisition run.
CPCB/NWDP measurements continue to be queried through `/api/measurements`.

Current weather context is available from Open-Meteo (no API key required):

```http
GET /api/environment/weather?latitude=30.9&longitude=75.8
```

The response contains the provider, returned coordinates, UTC timezone,
current temperature, humidity, precipitation, wind speed, and their units.
The external service must be reachable by the server.

On server startup, a background collector also stores Open-Meteo observations
for the configured ROI and refreshes them daily. CPCB/NWDP collection runs on
the same daily schedule. Read stored weather using
`GET /api/environment/weather/history`; check both collectors at
`GET /api/measurements/collector-status`. General measurement queries accept
`source=Open-Meteo` or `source=CPCB/NWDP`.

To start a one-time collection across the listed sources:

```http
POST /api/collect-all-sources
GET  /api/collect-all-sources/status
```

This refreshes CPCB/NWDP and Open-Meteo observations and submits Landsat,
Sentinel-2, Sentinel-1, and JRC Global Surface Water exports to Google Earth
Engine. Imagery exports require a configured Earth Engine account and are
submitted as asynchronous tasks to Google Drive; use the status endpoint to
check submission results.

---

## Module 1: Data Acquisition

**File:** `module1_gee_acquisition.py`

### Main Classes

#### `GEEAcquisition`

Handles satellite data download from Google Earth Engine.

```python
from module1_gee_acquisition import GEEAcquisition

# Initialize
acq = GEEAcquisition(
    roi_bounds={'north': 32.5, 'south': 30.5, 'east': 76.5, 'west': 74.5},
    start_date='2023-01-01',
    end_date='2023-12-31',
    cloud_percent=20
)

# Download data
images = acq.download_sentinel2()

# Get specific bands
rgb = acq.get_rgb()
```

### Key Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `download_sentinel2()` | None | `ee.ImageCollection` | Download Sentinel-2 data |
| `get_rgb()` | None | `np.ndarray` | Get RGB composite |
| `get_band()` | `band_name` | `np.ndarray` | Get specific band |
| `export_geotiff()` | `filename` | `str` | Export as GeoTIFF |

---

## Module 2: Preprocessing

**File:** `module2_preprocessing.py`

### Main Classes

#### `Preprocessor`

Handles image preprocessing and normalization.

```python
from module2_preprocessing import Preprocessor

# Initialize
prep = Preprocessor(
    tile_size=256,
    normalize='minmax',
    augment=True
)

# Process image
tiles = prep.process_image(image)

# Compute spectral indices
ndwi = prep.compute_ndwi(image)
```

### Key Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `process_image()` | `image` | `List[np.ndarray]` | Generate tiles |
| `compute_ndwi()` | `image` | `np.ndarray` | Compute NDWI |
| `compute_ndvi()` | `image` | `np.ndarray` | Compute NDVI |
| `normalize()` | `image`, `method` | `np.ndarray` | Normalize image |
| `augment()` | `image` | `List[np.ndarray]` | Data augmentation |

---

## Module 3: Training

**File:** `module3_train_yolov8.py`

### Main Classes

#### `YOLOTrainer`

Handles model training with YOLOv8.

```python
from module3_train_yolov8 import YOLOTrainer

# Initialize trainer
trainer = YOLOTrainer(
    model_variant='n',
    epochs=100,
    batch_size=16
)

# Train model
results = trainer.train(
    dataset_path='data/dataset/',
    img_size=640
)

# Get metrics
metrics = trainer.get_metrics()
```

### Key Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `train()` | `dataset_path`, `img_size` | `dict` | Train model |
| `evaluate()` | `test_data` | `dict` | Evaluate on test set |
| `get_metrics()` | None | `dict` | Get training metrics |
| `save_model()` | `path` | `str` | Save trained model |
| `resume_training()` | `checkpoint_path` | `dict` | Resume from checkpoint |

---

## Module 4: Inference

**File:** `module4_inference.py`

### Main Classes

#### `Inferencer`

Handles model inference and detection.

```python
from module4_inference import Inferencer

# Initialize
inferencer = Inferencer(
    model_path='runs/aqua_sentinel_v1/weights/best.pt',
    conf_threshold=0.5,
    iou_threshold=0.45
)

# Run inference
detections = inferencer.infer(image)

# Save results
inferencer.save_detections(detections, format='geojson')
```

### Key Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `infer()` | `image` | `List[Detection]` | Run inference |
| `infer_batch()` | `images` | `List[List[Detection]]` | Batch inference |
| `post_process()` | `detections` | `List[Detection]` | Post-process results |
| `save_detections()` | `detections`, `format` | `str` | Save to file |
| `visualize()` | `image`, `detections` | `np.ndarray` | Visualize detections |

---

## Forensic Engine

**File:** `forensic_engine.py`

### Main Classes

#### `ForensicAnalyzer`

Detects anomalies and generates reports.

```python
from forensic_engine import ForensicAnalyzer

# Initialize
analyzer = ForensicAnalyzer(
    anomaly_threshold=2.5,
    time_window=30
)

# Analyze detections
report = analyzer.analyze(
    detections=detections,
    satellite_data=sat_data
)

# Get anomalies
anomalies = analyzer.get_anomalies()
```

### Key Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `analyze()` | `detections`, `sat_data` | `dict` | Generate analysis |
| `get_anomalies()` | None | `List[Anomaly]` | Get detected anomalies |
| `time_series_analysis()` | `time_series` | `dict` | Analyze temporal changes |
| `generate_report()` | `format` | `str` | Generate report |

---

## Report Generation

**File:** `pdf_report.py`

### Main Classes

#### `PDFReporter`

Generates PDF reports.

```python
from pdf_report import PDFReporter

# Initialize
reporter = PDFReporter(
    title='Aqua-Sentinel Analysis Report'
)

# Add content
reporter.add_detections(detections)
reporter.add_maps(geojson_data)
reporter.add_statistics(stats)

# Generate report
reporter.save('report.pdf')
```

### Key Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_title()` | `title` | None | Add title page |
| `add_detections()` | `detections` | None | Add detection section |
| `add_maps()` | `geojson` | None | Add map visualizations |
| `add_statistics()` | `stats` | None | Add statistics section |
| `save()` | `filename` | `str` | Save PDF |

---

## Dashboard

**File:** `dashboard.py`

Streamlit-based web interface.

```bash
streamlit run dashboard.py
```

### Features
- Interactive maps with Folium
- Geographic hierarchy navigation
- Detection visualization
- Report download
- Real-time analysis

---

## Utility Functions

### `geo_hierarchy.py`

Geographic data organization.

```python
from geo_hierarchy import (
    get_states,
    get_cities,
    get_water_bodies,
    get_roi
)

# Get geographic data
states = get_states()
cities = get_cities('Punjab')
water_bodies = get_water_bodies('Punjab', 'Amritsar')
```

### `spectral_indices.py`

Spectral index computation.

```python
from spectral_indices import SpectralIndices

si = SpectralIndices(image_data)
ndwi = si.calculate_ndwi()
ndvi = si.calculate_ndvi()
mndwi = si.calculate_mndwi()
```

---

## Data Structures

### Detection

```python
{
    'class': int,          # Class ID (0=water, 1=land, 2=cloud)
    'confidence': float,   # 0-1
    'bbox': [x, y, w, h], # Bounding box
    'coords': {            # Geographic coordinates
        'lat': float,
        'lon': float
    }
}
```

### Anomaly

```python
{
    'type': str,           # Anomaly type
    'severity': float,     # 0-1
    'location': {lat, lon},
    'timestamp': datetime,
    'description': str
}
```

---

## Configuration Objects

### ROI Configuration

```python
ROI = {
    'state': str,
    'city': str,
    'water_body': str,
    'bounds': {
        'north': float,
        'south': float,
        'east': float,
        'west': float
    }
}
```

### Model Configuration

```python
MODEL_CONFIG = {
    'variant': str,        # n, s, m, l, x
    'img_size': int,       # 416, 512, 640
    'conf_threshold': float,
    'iou_threshold': float,
    'max_detections': int
}
```

---

## Error Handling

### Custom Exceptions

```python
from aqua_sentinel import (
    GEEAuthenticationError,
    DataAcquisitionError,
    ModelTrainingError,
    InferenceError
)
```

---

## Example Usage

### Complete Pipeline

```python
from module1_gee_acquisition import GEEAcquisition
from module2_preprocessing import Preprocessor
from module4_inference import Inferencer

# Acquire data
acq = GEEAcquisition(roi_bounds={...})
image = acq.download_sentinel2()

# Preprocess
prep = Preprocessor()
tiles = prep.process_image(image)

# Infer
inferencer = Inferencer()
detections = inferencer.infer(tiles[0])

# Save results
inferencer.save_detections(detections, format='geojson')
```

---

## Performance Considerations

### Memory Usage
- **Image Size 640x640**: ~500MB
- **Batch Size 16**: ~8GB GPU memory
- **Model Size**: 5-100MB depending on variant

### Speed
- **Inference**: 30-50 FPS (GPU)
- **Preprocessing**: 10-30 FPS
- **Training**: 100 epochs ≈ 2-4 hours (GPU)

---

## Next Steps

- [Installation](installation.md)
- [Quick Start](quickstart.md)
- [Modules](modules.md)
