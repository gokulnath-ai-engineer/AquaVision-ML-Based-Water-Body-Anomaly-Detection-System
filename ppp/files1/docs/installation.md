---
layout: default
title: Installation Guide
---

# Installation Guide

Complete step-by-step installation instructions for Aqua-Sentinel AI.

## Prerequisites

Before installing, ensure you have:
- **Python 3.8 or higher**
- **pip** or **conda** package manager
- **Git** for cloning the repository
- **CUDA 11.0+** (optional, for GPU acceleration)
- **At least 10GB** disk space for models and data

---

## Option 1: Standard Installation (Recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/surendra-01-yadav/aqua.git
cd aqua
```

### Step 2: Create Virtual Environment

**Using venv (Python built-in):**
```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/Mac
source venv/bin/activate
```

**Using conda:**
```bash
conda create -n aqua python=3.10
conda activate aqua
```

### Step 3: Install Dependencies

```bash
cd files
pip install -r requirements.txt
```

This installs:
- Scientific computing: NumPy, SciPy, Pandas
- Geospatial: GeoPandas, Rasterio, Shapely
- Deep Learning: PyTorch, YOLOv8 (Ultralytics)
- Web Dashboard: Streamlit, Folium
- Image Processing: OpenCV, Pillow

---

## Option 2: Conda Installation

```bash
# Create environment from file
conda env create -f environment.yml

# Activate environment
conda activate aqua

# Install additional packages if needed
conda install -c conda-forge rasterio geopandas folium
```

---

## Option 3: Docker Installation

### Build Docker Image

```bash
# Navigate to project root
cd aqua

# Build image
docker build -t aqua-sentinel:latest .
```

### Run with Docker

```bash
# Interactive mode
docker run -it aqua-sentinel:latest

# With volume mount for data
docker run -v $(pwd)/data:/app/data aqua-sentinel:latest python run_pipeline.py

# Run dashboard
docker run -p 8501:8501 -v $(pwd)/data:/app/data aqua-sentinel:latest \
  streamlit run dashboard.py --server.address=0.0.0.0
```

---

## Verifying Installation

### Check Python Version

```bash
python --version
# Should output: Python 3.8 or higher
```

### Verify Key Packages

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
python -c "import geopandas; print('GeoPandas: OK')"
python -c "from ultralytics import YOLO; print('YOLOv8: OK')"
```

### Test GPU Access (Optional)

```bash
python -c "import torch; print(f'GPU Available: {torch.cuda.is_available()}')"
```

---

## Google Earth Engine Setup

To use satellite data acquisition, set up Google Earth Engine:

### Step 1: Create GEE Account

1. Go to https://earthengine.google.com/
2. Sign in with Google account
3. Request access (takes 1-2 days)

### Step 2: Authenticate

```bash
# First time authentication
python
>>> import ee
>>> ee.Authenticate()
>>> ee.Initialize()
```

This opens browser for authentication. Follow the prompts and copy the authorization code.

### Step 3: Verify Access

```bash
python -c "import ee; ee.Initialize(); print('GEE authenticated successfully!')"
```

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure you're in the virtual environment
which python  # Should show path to venv

# Reinstall requirements
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: CUDA/GPU not detected

**Solution:**
```bash
# Install CPU version of PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Or GPU version (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Issue: GEE authentication fails

**Solution:**
```bash
# Reset authentication
rm ~/.config/earthengine/credentials
python -c "import ee; ee.Authenticate()"
```

### Issue: Rasterio installation fails on Windows

**Solution:**
```bash
# Use conda instead
conda install -c conda-forge rasterio
```

---

## Next Steps

After installation, check out:
- [Quick Start Guide](quickstart.md) - Get running in 5 minutes
- [Modules Overview](modules.md) - Understand the pipeline
- [Configuration](configuration.md) - Customize settings

---

## System Requirements

### Minimum Specifications
- **CPU:** Intel Core i5 / AMD Ryzen 5
- **RAM:** 8GB
- **Disk:** 10GB (models + data)
- **OS:** Windows 10+, Ubuntu 18.04+, macOS 10.14+

### Recommended Specifications
- **CPU:** Intel Core i7 / AMD Ryzen 7
- **RAM:** 16GB
- **GPU:** NVIDIA RTX 3060 or better
- **Disk:** 50GB SSD
- **OS:** Ubuntu 20.04 LTS

---

## Getting Help

- 📖 Check [FAQ](faq.md)
- 🐛 Report issues on [GitHub Issues](https://github.com/surendra-01-yadav/aqua/issues)
- 💬 Ask questions on [GitHub Discussions](https://github.com/surendra-01-yadav/aqua/discussions)
