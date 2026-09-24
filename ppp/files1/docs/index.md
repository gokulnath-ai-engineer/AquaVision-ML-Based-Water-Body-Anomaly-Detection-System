---
layout: default
title: Aqua-Sentinel AI- Bharath Water Monitor
---

# 🌊 Aqua-Sentinel AI- Bharath Water Monitor

**Hierarchical Geo-Intelligent Framework for Real-Time Multi-Spectral Water Quality Monitoring & Forensic Anomaly Reporting**

## What is Aqua-Sentinel?

Aqua-Sentinel AI is a comprehensive geospatial intelligence system that leverages:
- 🛰️ **Satellite imagery** (Sentinel-2, Google Earth Engine)
- 🤖 **Advanced AI** (YOLOv8 deep learning)
- 📊 **Spectral analysis** (NDWI water masking)
- 🔍 **Forensic reporting** (Anomaly detection)

Monitor water bodies across India with real-time detection, quality assessment, and detailed analysis.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🛰️ **Multi-Spectral Data** | Sentinel-2 satellite data via Google Earth Engine |
| 🎯 **AI Detection** | YOLOv8-based multi-class water body detection |
| 📊 **Spectral Analysis** | NDWI and advanced spectral indices |
| 🔍 **Forensic Reports** | Detailed anomaly detection and reporting |
| 🗺️ **Geo-Hierarchy** | State → City → Water Body organization |
| 📈 **Dashboard** | Streamlit-based interactive visualization |
| 📄 **Multi-Format Reports** | HTML, PDF, and GeoJSON outputs |
| 🐳 **Docker Support** | Containerized deployment |

---

## 🚀 Quick Start

### Installation (5 minutes)

```bash
# Clone repository
git clone https://github.com/surendra-01-yadav/aqua.git
cd aqua/files

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Pipeline

```bash
# Full pipeline
python run_pipeline.py

# Dashboard
streamlit run dashboard.py

# Specific module
python run_pipeline.py --module 2
```

---

## 📚 Documentation

- [Installation Guide](installation.md) - Detailed setup instructions
- [Quick Start Guide](quickstart.md) - Get started in 5 minutes
- [Modules Overview](modules.md) - Understanding each pipeline module
- [API Reference](api.md) - Function and class documentation
- [Configuration](configuration.md) - Customize your setup
- [FAQ](faq.md) - Common questions answered

---

## 🔗 Links

| Link | URL |
|------|-----|
| **GitHub** | https://github.com/surendra-01-yadav/aqua |
| **Issues** | https://github.com/surendra-01-yadav/aqua/issues |
| **Releases** | https://github.com/surendra-01-yadav/aqua/releases |

---

## 📊 Project Structure

```
aqua/
├── files/                    # Main application
│   ├── module1_gee_acquisition.py
│   ├── module2_preprocessing.py
│   ├── module3_train_yolov8.py
│   ├── module4_inference.py
│   ├── forensic_engine.py
│   ├── dashboard.py
│   ├── run_pipeline.py      # Main entry point
│   └── requirements.txt
├── docs/                    # This documentation
└── data/                    # Data, models, and reports
```

---

## 🛠️ Technology Stack

**Backend:**
- Python 3.8+
- PyTorch / YOLOv8
- GeoPandas, Rasterio
- Google Earth Engine

**Frontend:**
- Streamlit
- Folium
- React/Node.js (optional)

**Deployment:**
- Docker
- GitHub Pages (documentation)

---

## 👨‍💻 Author

**Surendra Yadav**
- GitHub: [@surendra-01-yadav](https://github.com/surendra-01-yadav)
- Email: surendra.01.yadav@example.com

---

## 📄 License

MIT License - See [LICENSE](https://github.com/surendra-01-yadav/aqua/blob/main/LICENSE) for details.

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](https://github.com/surendra-01-yadav/aqua/blob/main/CONTRIBUTING.md)

---

**Last Updated:** April 2026  
**Status:** Active Development ✅
