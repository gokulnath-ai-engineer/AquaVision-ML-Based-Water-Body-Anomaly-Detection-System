---
layout: default
title: Configuration Guide
---

# Configuration Guide

Customize Aqua-Sentinel AI for your specific needs.

---

## Main Configuration File

**Location:** `files/config.py`

### Geographic Settings

```python
# Enable river-only detection (ignore lakes)
RIVER_ONLY_MODE = True

# Region of Interest
ROI = {
    'state': 'Punjab',
    'city': 'Ludhiana',
    'water_body': 'Buddha Dariya'
}

# Bounding coordinates
BOUNDS = {
    'north': 32.5,
    'south': 30.5,
    'east': 76.5,
    'west': 74.5
}
```

### Data Acquisition

```python
# Date range for satellite data
DATE_RANGE = ('2023-01-01', '2023-12-31')

# Cloud cover threshold (0-100)
CLOUD_PERCENT = 20

# Sentinel-2 bands to use
BANDS = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']

# Resampling resolution (meters)
RESOLUTION = 10
```

### Preprocessing

```python
# Image tile size
TILE_SIZE = 256  # or 512, 1024

# Normalization method
NORMALIZE = 'minmax'  # or 'standard', 'zscore'

# Data augmentation
AUGMENT = True
AUGMENTATION_FACTOR = 3  # Create 3x more augmented samples

# NDWI threshold for water masking
NDWI_THRESHOLD = 0.3
```

### Model Training

```python
# Training parameters
EPOCHS = 100
BATCH_SIZE = 16
LEARNING_RATE = 0.001
LEARNING_RATE_DECAY = 0.1
MOMENTUM = 0.937
WEIGHT_DECAY = 0.0005

# Image size for training
IMG_SIZE = 640

# YOLOv8 model variant
MODEL_VARIANT = 'n'  # nano, small, medium, large, xlarge
# nano (smallest, fastest)
# small
# medium (balanced)
# large
# xlarge (largest, slowest)

# Augmentation during training
AUGMENT_TRAINING = True

# Early stopping
PATIENCE = 20  # Stop if no improvement for N epochs
```

### Inference

```python
# Detection thresholds
CONF_THRESHOLD = 0.5
IOU_THRESHOLD = 0.45

# Maximum detections per image
MAX_DETECTIONS = 300

# Filter by class
CLASSES_TO_DETECT = [0, 1, 2]  # water, land, cloud

# Output formats
OUTPUT_FORMATS = ['yolo', 'geojson', 'csv', 'image']
```

### Forensic Analysis

```python
# Anomaly detection sensitivity
ANOMALY_THRESHOLD = 2.5  # Standard deviations from mean

# Time-series analysis window
TIME_WINDOW_DAYS = 30

# Report generation
REPORT_FORMATS = ['html', 'pdf', 'json', 'geojson']
REPORT_INCLUDE_MAPS = True
```

### File Paths

```python
# Data directories
DATA_DIR = 'data/'
RAW_DIR = 'data/raw_geotiff/'
PROCESSED_DIR = 'data/processed_heatmaps/'
DATASET_DIR = 'data/dataset/'
OUTPUT_DIR = 'data/inference_output/'

# Model paths
MODEL_PATH = 'yolov8n.pt'
WEIGHTS_DIR = 'runs/aqua_sentinel_v1/weights/'

# Report output
REPORTS_DIR = 'data/reports/'
```

---

## Command-Line Arguments

Override config settings via command line:

```bash
python run_pipeline.py \
    --state "Haryana" \
    --city "Faridabad" \
    --epochs 50 \
    --batch_size 32 \
    --conf_threshold 0.6 \
    --img_size 512
```

---

## Environment Variables

Create `.env` file for sensitive data:

```bash
# Google Earth Engine
GEE_PROJECT_ID=your-project-id
GEE_CREDENTIALS=path/to/credentials.json

# API Keys (if using external services)
MAPBOX_TOKEN=your-mapbox-token

# Output paths
OUTPUT_BUCKET=gs://your-gcs-bucket

# Debug mode
DEBUG=False
LOG_LEVEL=INFO
```

---

## Module-Specific Configuration

### Module 1 (GEE Acquisition)

```python
# config.py - GEE settings
GEE_CONFIG = {
    'project_id': 'your-ee-project',
    'export_scale': 10,
    'export_format': 'GeoTIFF',
    'export_bucket': 'your-bucket',
}
```

### Module 2 (Preprocessing)

```python
PREPROCESS_CONFIG = {
    'tile_size': 256,
    'overlap': 32,
    'normalize': 'minmax',
    'compute_indices': ['NDWI', 'NDVI', 'MNDWI'],
}
```

### Module 3 (Training)

```python
TRAIN_CONFIG = {
    'model': 'yolov8n',
    'epochs': 100,
    'imgsz': 640,
    'batch': 16,
    'optimizer': 'SGD',
    'patience': 20,
}
```

### Module 4 (Inference)

```python
INFER_CONFIG = {
    'conf': 0.5,
    'iou': 0.45,
    'max_det': 300,
    'save_conf': True,
    'save_txt': True,
}
```

---

## Logging Configuration

```python
# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/aqua_sentinel.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

---

## Docker Configuration

Customize via environment variables:

```bash
docker run \
    -e EPOCHS=50 \
    -e BATCH_SIZE=32 \
    -e CONF_THRESHOLD=0.6 \
    aqua-sentinel:latest
```

---

## Performance Tuning

### For Faster Training
```python
BATCH_SIZE = 32  # Increase (if GPU memory allows)
IMG_SIZE = 512   # Reduce from 640
EPOCHS = 50      # Reduce
```

### For Better Accuracy
```python
BATCH_SIZE = 8   # Decrease
IMG_SIZE = 640   # Keep high
EPOCHS = 200     # Increase
AUGMENT_TRAINING = True
```

### For GPU Memory Issues
```python
BATCH_SIZE = 4   # Reduce batch size
IMG_SIZE = 416   # Reduce image size
ACCUMULATE_GRAD_BATCHES = 4  # Gradient accumulation
```

---

## Geo-Hierarchy Configuration

**File:** `geo_hierarchy.py`

```python
# State-City-Water Body mapping
GEO_HIERARCHY = {
    'Punjab': {
        'Amritsar': ['Amrit Sarovar', 'Katra Akal'],
        'Ludhiana': ['Buddha Dariya'],
    },
    'Haryana': {
        'Faridabad': ['Yamuna River'],
    }
}
```

---

## Example Configurations

### Quick Testing (Low Resource)
```python
EPOCHS = 10
BATCH_SIZE = 4
IMG_SIZE = 416
TILE_SIZE = 128
AUGMENT = False
```

### Production (High Quality)
```python
EPOCHS = 200
BATCH_SIZE = 32
IMG_SIZE = 640
TILE_SIZE = 512
AUGMENT = True
AUGMENTATION_FACTOR = 5
```

### Research (Maximum Accuracy)
```python
EPOCHS = 500
BATCH_SIZE = 16
IMG_SIZE = 1024
AUGMENT = True
AUGMENTATION_FACTOR = 10
ENSEMBLE = True  # Use model ensembles
```

---

## Validation & Testing

Verify configuration:

```bash
python -c "from config import *; print(ROI); print(EPOCHS)"
```

---

## Next Steps

- [Quick Start](quickstart.md) - Get running with defaults
- [Installation](installation.md) - Full setup guide
- [Modules](modules.md) - Understand each module
