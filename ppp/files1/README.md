# Aqua-Sentinel AI 🌊

**Hierarchical Geo-Intelligent Framework for Real-Time Multi-Spectral Water Quality Monitoring & Forensic Anomaly Reporting**

---

## 🎯 Overview

Aqua-Sentinel AI is a comprehensive geospatial intelligence system that leverages satellite imagery (Sentinel-2), advanced computer vision (YOLOv8), and machine learning to monitor water bodies across India. The system provides real-time water quality assessment, anomaly detection, and forensic analysis capabilities.

### Key Features

- 🛰️ **Multi-Spectral Satellite Data Acquisition** - Integrates with Google Earth Engine and Sentinel-2
- 🎯 **AI-Powered Water Detection** - YOLOv8-based multi-class water body detection
- 📊 **Spectral Analysis** - Advanced NDWI (Normalized Difference Water Index) masking
- 🔍 **Forensic Reporting** - Detailed anomaly detection and anomaly reporting
- 🗺️ **Geo-Hierarchical Organization** - State → City → Water Body organization
- 📈 **Interactive Dashboard** - Streamlit-based visualization and analysis
- 📄 **Multi-Format Reports** - HTML, PDF, and GeoJSON outputs

---

## 📁 Project Structure

```
aqua/
├── files/                              # Main application
│   ├── config.py                       # Configuration settings
│   ├── requirements.txt                # Python dependencies
│   ├── run_pipeline.py                 # Unified pipeline entry point
│   │
│   ├── Module 1: Data Acquisition
│   │   └── module1_gee_acquisition.py  # Sentinel-2 data from GEE
│   │
│   ├── Module 2: Preprocessing
│   │   ├── module2_preprocessing.py    # Normalization, tiling, masking
│   │   ├── water_masking.py            # NDWI-based water masking
│   │   └── spectral_indices.py         # Spectral indices computation
│   │
│   ├── Module 3: Training
│   │   ├── module3_train_yolov8.py     # YOLOv8 model training
│   │   ├── train_punjab.py             # Punjab-specific training
│   │   └── generate_training_dataset.py # Dataset generation
│   │
│   ├── Module 4: Inference
│   │   └── module4_inference.py        # Model inference & detection
│   │
│   ├── Analysis & Reporting
│   │   ├── forensic_engine.py          # Anomaly detection engine
│   │   ├── pdf_report.py               # PDF report generation
│   │   └── dashboard.py                # Streamlit dashboard
│   │
│   ├── Data
│   │   ├── dataset/                    # Training/validation data
│   │   ├── punjab_training/            # Punjab region data
│   │   ├── processed_heatmaps/         # Heatmap outputs
│   │   ├── inference_input/            # Input for inference
│   │   └── inference_output/           # Inference results
│   │
│   └── Utilities
│       ├── geo_hierarchy.py            # Geographic hierarchy
│       ├── generate_geo_hierarchy.py   # Hierarchy generation
│       ├── generate_synthetic_data.py  # Synthetic data generation
│       ├── dashboard_utils.py          # Dashboard utilities
│       ├── punjab_sites.json           # Punjab water body data
│       └── India_Cities_Rivers_Lakes.md # Reference data
│
├── india-rivers-lakes/                 # React/Node.js frontend
│   ├── client/                         # React frontend
│   └── server/                         # Node.js backend
│
└── data/                               # Large data files
    ├── reports/                        # Generated reports
    ├── runs/                           # Training runs
    └── static/                         # Static assets
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- CUDA 11.0+ (optional, for GPU acceleration)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/surendra-01-yadav/aqua.git
   cd aqua/files
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Usage

#### Run Full Pipeline
```bash
python run_pipeline.py
```

#### Run Specific Module
```bash
python run_pipeline.py --module 2        # Run Module 2 (Preprocessing)
python run_pipeline.py --module 3 --epochs 10  # Run Module 3 with 10 epochs
```

#### Run Dashboard
```bash
streamlit run dashboard.py
```

#### Run Server
```bash
python server.py
```

---

## 📊 Pipeline Modules

### Module 1: Data Acquisition
- Downloads multi-spectral satellite data from Google Earth Engine
- Supports Sentinel-2 Level-2A imagery
- Geographic filtering by state, city, and water body
- Date range selection for temporal analysis

```bash
python module1_gee_acquisition.py
```

### Module 2: Preprocessing
- Image normalization and standardization
- NDWI (Normalized Difference Water Index) water masking
- Tile generation for training
- Spectral index computation

```bash
python module2_preprocessing.py
```

### Module 3: YOLOv8 Training
- Multi-class water body detection model training
- Auto-annotation with synthetic ground truth
- Hyperparameter optimization
- Model validation and testing

```bash
python module3_train_yolov8.py
```

### Module 4: Inference
- Real-time detection on new satellite imagery
- Confidence scoring and filtering
- Geo-spatial coordinate mapping
- Output in multiple formats

```bash
python module4_inference.py
```

### Forensic Analysis
- Anomaly detection using spectral signatures
- Water quality assessment
- Time-series analysis and change detection
- Detailed forensic reports

---

## 📈 Dashboard Features

The Streamlit dashboard provides:
- **Interactive Map Visualization** - Folium-based maps with detection overlays
- **State/City/Water Body Hierarchy** - Easy navigation through geographic levels
- **Detection Results** - View detected water bodies with confidence scores
- **Forensic Reports** - Access detailed analysis and anomaly reports
- **Data Download** - Export results in CSV, GeoJSON, or PDF formats

```bash
streamlit run dashboard.py
```

---

## 🛠️ Configuration

Edit `files/config.py` to customize:

```python
# Enable river-only detection mode
RIVER_ONLY_MODE = True

# Region of Interest (ROI)
ROI = {
    'state': 'Punjab',
    'city': 'Ludhiana',
    'water_body': 'Buddha Dariya'
}

# Model settings
MODEL_CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.45
```

---

## 📦 Dependencies

### Key Libraries
- **Geospatial**: rasterio, geopandas, shapely, pyproj
- **Remote Sensing**: Google Earth Engine (ee)
- **Deep Learning**: YOLOv8 (ultralytics), PyTorch
- **Image Processing**: OpenCV, Pillow
- **Web Dashboard**: Streamlit, Folium
- **Data Processing**: pandas, NumPy, SciPy

See `files/requirements.txt` for complete dependency list.

---

## 📊 Data Sources

- **Satellite Imagery**: Sentinel-2 (via Google Earth Engine)
- **Reference Data**: Punjab water bodies and geographic hierarchy
- **Ground Truth**: Synthetic data generation with geographic validation

---

## 🔄 Model Training

The system uses YOLOv8 for water body detection:

```bash
# Full training pipeline
python module3_train_yolov8.py --epochs 100 --batch_size 16

# Resume training
python module3_train_yolov8.py --resume
```

**Trained Models**: Available in `runs/aqua_sentinel_v1/weights/`

---

## 📝 Output Formats

The system generates reports in multiple formats:

- **HTML Reports** - Interactive reports with statistics
- **PDF Reports** - Printable forensic analysis reports
- **GeoJSON** - Geographic features for mapping software
- **CSV** - Tabular detection results
- **JSON** - Detailed metadata and analysis

---

## 🔐 Environment Variables

Create a `.env` file for sensitive configuration:

```bash
# Google Earth Engine credentials
GEE_PROJECT_ID=your-project-id

# Database credentials (if using)
DB_HOST=localhost
DB_USER=admin
DB_PASSWORD=password
```

---

## 📚 Documentation

- **Pipeline Documentation**: See inline docstrings in each module
- **Geo Hierarchy**: Check `India_Cities_Rivers_Lakes.md`
- **Training Details**: Review `generate_training_dataset.py`
- **Forensic Engine**: Understand anomaly detection in `forensic_engine.py`

---

## 🧪 Testing

```bash
# Run with demo/synthetic data (no real GEE access needed)
python run_pipeline.py --demo

# Test specific region
python run_pipeline.py --state Punjab --city Amritsar
```

---

## 🐳 Docker Support

Build and run in Docker:

```bash
docker build -t aqua-sentinel .
docker run -v $(pwd)/data:/app/data aqua-sentinel python run_pipeline.py
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Surendra Yadav**  
- GitHub: [@surendra-01-yadav](https://github.com/surendra-01-yadav)

---

## 🙏 Acknowledgments

- Google Earth Engine for satellite data access
- Ultralytics for YOLOv8 framework
- Sentinel-2 mission for multi-spectral imagery
- Open-source GIS community

---

## 📞 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/surendra-01-yadav/aqua/issues)
- Check [Discussions](https://github.com/surendra-01-yadav/aqua/discussions)
- Email: surendra.01.yadav@example.com (update with your email)

---

## 🔗 Links

- **Repository**: https://github.com/surendra-01-yadav/aqua
- **Issues**: https://github.com/surendra-01-yadav/aqua/issues
- **Releases**: https://github.com/surendra-01-yadav/aqua/releases

---

**Last Updated**: April 2026  
**Status**: Active Development ✅
