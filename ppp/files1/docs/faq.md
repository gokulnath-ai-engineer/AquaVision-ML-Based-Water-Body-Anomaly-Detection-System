---
layout: default
title: Frequently Asked Questions
---

# Frequently Asked Questions (FAQ)

Common questions about Aqua-Sentinel AI.

---

## Installation & Setup

### Q: What are the system requirements?

**A:** Minimum:
- Python 3.8+
- 8GB RAM
- 10GB disk space
- Windows, Linux, or macOS

Recommended:
- Python 3.10+
- 16GB+ RAM
- NVIDIA GPU (RTX 3060 or better)
- 50GB+ SSD

### Q: Can I run this on Windows?

**A:** Yes! Windows 10+ is fully supported. Use:
```bash
venv\Scripts\activate  # Instead of source venv/bin/activate
```

### Q: Do I need a GPU?

**A:** No, but it's highly recommended for training (50-100x faster). CPU works but slower.

### Q: How do I install on Mac?

**A:** Same as Linux:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Google Earth Engine

### Q: Do I need GEE access?

**A:** For Module 1 (data acquisition), yes. It's free but requires registration at https://earthengine.google.com/

### Q: How long does authentication take?

**A:** Usually 1-2 days to get approved. You can test with demo mode meanwhile:
```bash
python run_pipeline.py --demo
```

### Q: How much does GEE data cost?

**A:** Free! Google provides free Sentinel-2 data through Earth Engine.

### Q: Can I use other satellite data sources?

**A:** The system is designed for Sentinel-2, but you can modify Module 1 to use other sources like Landsat, MODIS, etc.

---

## Training & Models

### Q: How long does training take?

**A:** 
- GPU (RTX 3060): 2-4 hours for 100 epochs
- GPU (RTX 4090): 30 minutes
- CPU: 10+ hours

### Q: How much training data do I need?

**A:** 
- Minimum: 100 images
- Recommended: 1000+ images
- Best: 5000+ images for production

### Q: Can I use pre-trained weights?

**A:** Yes! The system includes `yolov8n.pt`. Start training with:
```bash
python module3_train_yolov8.py --pretrained
```

### Q: How do I improve model accuracy?

**A:** 
1. Increase training data (quantity & diversity)
2. Increase epochs (100 → 200)
3. Use larger model variant (nano → small → medium)
4. Enable augmentation in config
5. Reduce learning rate

### Q: Can I use my own trained model?

**A:** Yes! Replace `yolov8n.pt` and update `config.py`:
```python
MODEL_PATH = 'path/to/your/model.pt'
```

---

## Inference & Detection

### Q: How fast is inference?

**A:** 
- GPU: 30-50 FPS (frames per second)
- CPU: 2-5 FPS

### Q: How accurate is the detection?

**A:** Typically 92-95% mAP on test set. Varies by:
- Training data quality
- Regional variations
- Cloud cover
- Water body types

### Q: What's the difference between confidence score and IoU?

**A:** 
- **Confidence**: Model's certainty (0-1). Higher = more confident.
- **IoU**: Intersection over Union. How well bounding box matches object.

### Q: How do I filter low-quality detections?

**A:** Adjust thresholds:
```python
CONF_THRESHOLD = 0.7  # Higher = fewer, better quality
IOU_THRESHOLD = 0.5
```

---

## Dashboard

### Q: Dashboard won't load?

**A:** 
```bash
pip install streamlit --upgrade
streamlit run dashboard.py --logger.level=debug
```

### Q: How do I access dashboard from another computer?

**A:** Run with server address:
```bash
streamlit run dashboard.py --server.address=0.0.0.0 --server.port=8501
```
Then access at: `http://your-ip:8501`

### Q: Can I customize the dashboard?

**A:** Yes! Edit `dashboard.py` to add/remove features, change colors, add maps, etc.

---

## Performance & Optimization

### Q: How do I speed up training?

**A:** 
1. Use GPU
2. Reduce image size: `IMG_SIZE = 416` (vs 640)
3. Reduce batch size: `BATCH_SIZE = 32` (vs 16) - if GPU memory allows
4. Use smaller model: `yolov8n` (nano, fastest)

### Q: How do I reduce memory usage?

**A:** 
```python
BATCH_SIZE = 4  # Smaller batches
IMG_SIZE = 416  # Smaller images
ACCUMULATE_GRAD_BATCHES = 4  # Gradient accumulation
```

### Q: Can I use multiple GPUs?

**A:** Yes, if you have multiple GPUs:
```python
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2'  # Use GPUs 0, 1, 2
```

---

## Reports & Output

### Q: What output formats are supported?

**A:** 
- GeoJSON (geographic features)
- CSV (tabular data)
- JSON (structured data)
- PDF (reports)
- PNG/JPG (visualizations)

### Q: How do I generate PDF reports?

**A:** 
```bash
python pdf_report.py --detections data/detections.csv
```

### Q: Can I customize reports?

**A:** Yes! Edit `pdf_report.py` to change formatting, add logos, change colors, etc.

---

## Troubleshooting

### Q: ImportError for specific modules?

**A:** Reinstall dependencies:
```bash
pip install -r requirements.txt --upgrade --force-reinstall
```

### Q: Out of memory error?

**A:** Reduce batch size or image size in config.py

### Q: CUDA out of memory?

**A:** 
```bash
# Use CPU instead
os.environ['CUDA_VISIBLE_DEVICES'] = ''

# Or reduce batch size
BATCH_SIZE = 4
```

### Q: File not found errors?

**A:** Verify paths in `config.py` are correct:
```bash
pwd  # Print working directory
ls -la data/  # List data folder
```

### Q: GEE authentication fails?

**A:** Reset and re-authenticate:
```bash
rm ~/.config/earthengine/credentials
python -c "import ee; ee.Authenticate()"
```

---

## Advanced Topics

### Q: Can I use this for other water bodies (lakes, oceans)?

**A:** Yes! Retrain the model on your target water bodies:
```bash
python module3_train_yolov8.py --dataset your_data_folder
```

### Q: Can I detect other features besides water?

**A:** Yes! Modify training data and model classes in config.

### Q: How do I deploy to cloud?

**A:** 
- **Google Cloud**: Use Cloud Run or Compute Engine
- **AWS**: Use EC2 or SageMaker
- **Azure**: Use Azure ML or Container Instances

### Q: Can I use this in production?

**A:** Yes! Considerations:
- Use ensemble models for higher accuracy
- Implement error handling
- Monitor model performance
- Plan for model retraining
- Secure API endpoints

---

## Getting Help

Still have questions?
- 📖 Check [Documentation](index.md)
- 🐛 [Report Issues](https://github.com/surendra-01-yadav/aqua/issues)
- 💬 [GitHub Discussions](https://github.com/surendra-01-yadav/aqua/discussions)
- 📧 Email: surendra.01.yadav@example.com

---

**Last Updated:** April 2026
