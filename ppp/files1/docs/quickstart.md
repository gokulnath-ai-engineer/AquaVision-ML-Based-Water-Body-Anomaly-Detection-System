---
layout: default
title: Quick Start Guide
---

# Quick Start Guide

Get Aqua-Sentinel AI running in 5 minutes!

---

## Installation (2 minutes)

```bash
# Clone and navigate
git clone https://github.com/surendra-01-yadav/aqua.git
cd aqua/files

# Create environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install
pip install -r requirements.txt
```

---

## Run Pipeline (1 minute)

### Demo Mode (No GEE Access Needed)

```bash
python run_pipeline.py --demo
```

This runs with synthetic data to test the entire pipeline.

### Full Pipeline

```bash
python run_pipeline.py
```

### Run Specific Module

```bash
# Module 1: Data Acquisition
python module1_gee_acquisition.py

# Module 2: Preprocessing
python module2_preprocessing.py

# Module 3: Training
python module3_train_yolov8.py --epochs 10

# Module 4: Inference
python module4_inference.py
```

---

## Launch Dashboard (1 minute)

```bash
streamlit run dashboard.py
```

Opens interactive dashboard at `http://localhost:8501`

---

## Run Web Server

```bash
python server.py
```

API server runs at `http://localhost:5000`

---

## Common Commands

### Train Model
```bash
python module3_train_yolov8.py --epochs 100 --batch_size 16
```

### Run Inference
```bash
python module4_inference.py --model yolov8n.pt --input images/
```

### Generate Report
```bash
python pdf_report.py --detections data/detections.csv
```

### Test Region
```bash
python run_pipeline.py --state Punjab --city Amritsar
```

---

## Project Structure

```
aqua/
├── files/
│   ├── run_pipeline.py              ← Start here
│   ├── dashboard.py                 ← Web interface
│   ├── module1_gee_acquisition.py   ← Satellite data
│   ├── module2_preprocessing.py     ← Image processing
│   ├── module3_train_yolov8.py      ← Model training
│   ├── module4_inference.py         ← Detection
│   └── requirements.txt              ← Dependencies
└── data/                            ← Models, data, outputs
```

---

## Next Steps

- ✅ [Full Installation Guide](installation.md)
- ✅ [Modules Overview](modules.md)
- ✅ [API Reference](api.md)
- ✅ [Configuration](configuration.md)
- ✅ [FAQ](faq.md)

---

## Troubleshooting

**Issue:** Module import errors
```bash
pip install -r requirements.txt --upgrade
```

**Issue:** GPU not detected
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

**Issue:** Dashboard won't start
```bash
pip install streamlit --upgrade
streamlit run dashboard.py --logger.level=debug
```

---

## Support

- 📚 [Full Documentation](index.md)
- 🐛 [Report Issues](https://github.com/surendra-01-yadav/aqua/issues)
- 💬 [Discussions](https://github.com/surendra-01-yadav/aqua/discussions)
