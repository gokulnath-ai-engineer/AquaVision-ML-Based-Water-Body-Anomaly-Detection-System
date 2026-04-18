---
layout: default
title: Pipeline Modules
---

# Pipeline Modules Overview

Aqua-Sentinel AI consists of 4 main modules plus analysis tools.

---

## Module 1: Data Acquisition 🛰️

**File:** `module1_gee_acquisition.py`

Acquires multi-spectral satellite data from Google Earth Engine.

### Features
- Sentinel-2 Level-2A imagery download
- Atmospheric correction included
- Geographic filtering (state, city, water body)
- Date range selection
- Cloud filtering and masking

### Usage

```bash
python module1_gee_acquisition.py
```

### Configuration

```python
# config.py
ROI = {
    'state': 'Punjab',
    'city': 'Ludhiana',
    'water_body': 'Buddha Dariya'
}

DATE_RANGE = ('2023-03-01', '2023-09-30')
CLOUD_PERCENT = 20
```

### Output
- GeoTIFF files with 11 spectral bands
- Metadata JSON files
- Location: `data/raw_geotiff/`

---

## Module 2: Preprocessing 🎨

**File:** `module2_preprocessing.py`

Processes raw satellite imagery for training.

### Features
- Normalization (0-1 or -1 to 1)
- Tile generation (256x256, 512x512)
- NDWI water masking
- Spectral indices computation
- Data augmentation

### Spectral Indices

| Index | Formula | Use |
|-------|---------|-----|
| **NDWI** | (B03-B08)/(B03+B08) | Water detection |
| **NDVI** | (B08-B04)/(B08+B04) | Vegetation |
| **MNDWI** | (B03-B11)/(B03+B11) | Built-up areas |

### Usage

```bash
python module2_preprocessing.py

# With custom settings
python module2_preprocessing.py --tile_size 512 --normalize minmax
```

### Output
- Processed image tiles
- Water mask GeoTIFFs
- Location: `data/processed_heatmaps/`

---

## Module 3: Model Training 🤖

**File:** `module3_train_yolov8.py`

Trains YOLOv8 model for water body detection.

### Features
- Multi-class detection (water, land, cloud)
- Auto-annotation with synthetic ground truth
- Hyperparameter optimization
- Model validation and testing
- Training metrics logging

### Usage

```bash
# Standard training (100 epochs)
python module3_train_yolov8.py

# Custom parameters
python module3_train_yolov8.py --epochs 50 --batch_size 32 --img_size 640

# Resume training
python module3_train_yolov8.py --resume

# With specific dataset
python module3_train_yolov8.py --dataset data/punjab_training
```

### Hyperparameters

```python
EPOCHS = 100
BATCH_SIZE = 16
IMG_SIZE = 640
LEARNING_RATE = 0.001
CONF_THRESHOLD = 0.5
IOU_THRESHOLD = 0.45
```

### Output
- Trained weights: `runs/aqua_sentinel_v1/weights/best.pt`
- Training logs and metrics
- Validation results

---

## Module 4: Inference 🎯

**File:** `module4_inference.py`

Runs detection on new satellite imagery.

### Features
- Batch inference
- Confidence filtering
- Non-maximum suppression
- Geo-spatial coordinate mapping
- Multiple output formats

### Usage

```bash
# Inference on test images
python module4_inference.py

# Custom input directory
python module4_inference.py --input data/test_images

# With confidence threshold
python module4_inference.py --conf 0.6

# Generate GeoJSON output
python module4_inference.py --output geojson
```

### Output Formats
- **YOLO Format**: Detection coordinates
- **GeoJSON**: Geographic features
- **CSV**: Tabular results
- **Visualizations**: Annotated images

---

## Analysis Tools 🔍

### Forensic Engine
**File:** `forensic_engine.py`

Detects anomalies and generates detailed reports.

```python
from forensic_engine import ForensicAnalyzer

analyzer = ForensicAnalyzer()
report = analyzer.analyze(detections, satellite_data)
```

### PDF Report Generation
**File:** `pdf_report.py`

Creates professional PDF reports.

```bash
python pdf_report.py --detections data/detections.csv
```

### Dashboard
**File:** `dashboard.py`

Interactive Streamlit interface.

```bash
streamlit run dashboard.py
```

---

## Unified Pipeline Runner

**File:** `run_pipeline.py`

Runs all modules sequentially or individually.

### Usage

```bash
# Full pipeline
python run_pipeline.py

# Specific modules
python run_pipeline.py --module 2,3,4

# Skip training
python run_pipeline.py --skip-training

# With parameters
python run_pipeline.py --state Punjab --city Amritsar --epochs 50
```

### Options

```
--demo              Run with synthetic data
--module N          Run specific module (1-4)
--skip-training     Skip Module 3 (training)
--epochs N          Training epochs
--batch_size N      Batch size
--state NAME        Geographic state
--city NAME         City name
--water-body NAME   Water body name
```

---

## Data Flow

```
Module 1 (Acquisition)
    ↓
Raw GeoTIFF files
    ↓
Module 2 (Preprocessing)
    ↓
Processed tiles + masks
    ↓
Module 3 (Training)
    ↓
Trained model weights
    ↓
Module 4 (Inference)
    ↓
Detections + coordinates
    ↓
Forensic Engine
    ↓
Final Reports (PDF, JSON, GeoJSON)
```

---

## Performance Metrics

### Training Metrics
- **mAP@0.5**: Mean Average Precision at IoU=0.5
- **Precision**: True positives / predicted positives
- **Recall**: True positives / actual positives
- **F1-Score**: Harmonic mean of precision and recall

### Typical Results
- **Accuracy**: 92-95% on test set
- **Inference Speed**: 30-50 FPS (GPU)
- **Model Size**: 5-100 MB depending on variant

---

## Next Steps

- [Installation Guide](installation.md) - Set up Aqua-Sentinel
- [Configuration](configuration.md) - Customize settings
- [API Reference](api.md) - Function documentation
