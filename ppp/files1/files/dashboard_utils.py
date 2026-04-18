"""
dashboard_utils.py
━━━━━━━━━━━━━━━━━━
Utility functions for the Aqua-Sentinel AI Streamlit dashboard.
Handles data loading, caching, and formatting.
"""

import json
import csv
from pathlib import Path
from typing import Optional

import numpy as np

from config import INFER, PREPROCESS, ROI, DASHBOARD


# ──────────────────────────────────────────────
# Data loading
# ──────────────────────────────────────────────

def load_detections_csv() -> list[dict]:
    """Load detections from CSV report."""
    csv_path = Path(INFER["report_csv"])
    if not csv_path.exists():
        return []

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            # Convert numeric fields
            row["confidence"] = float(row["confidence"]) if row["confidence"] else 0.0
            row["centre_lat"] = float(row["centre_lat"]) if row["centre_lat"] and row["centre_lat"] != "None" else None
            row["centre_lon"] = float(row["centre_lon"]) if row["centre_lon"] and row["centre_lon"] != "None" else None
            rows.append(row)
    return rows


def load_geojson() -> Optional[dict]:
    """Load GeoJSON hotspots file."""
    gj_path = Path(INFER["report_geojson"])
    if not gj_path.exists():
        return None
    with open(gj_path) as f:
        return json.load(f)


def get_heatmap_files() -> list[Path]:
    """Get all processed heatmap PNG files."""
    proc_dir = Path(PREPROCESS["processed_dir"])
    return sorted(proc_dir.glob("*_heatmap.png"))


def get_detection_images() -> list[Path]:
    """Get all annotated detection images."""
    out_dir = Path(INFER["output_dir"])
    if not out_dir.exists():
        return []
    return sorted(out_dir.glob("*_detected.png"))


def get_tile_images() -> list[Path]:
    """Get all preprocessed tile images."""
    tiles_dir = Path(PREPROCESS["processed_dir"]) / "tiles"
    if not tiles_dir.exists():
        return []
    return sorted(tiles_dir.glob("*.png"))


def get_mask_images() -> list[Path]:
    """Get all anomaly mask images."""
    masks_dir = Path(PREPROCESS["processed_dir"]) / "masks"
    if not masks_dir.exists():
        return []
    return sorted(masks_dir.glob("*.png"))


# ──────────────────────────────────────────────
# Statistics
# ──────────────────────────────────────────────

def compute_statistics(detections: list[dict]) -> dict:
    """Compute summary statistics from detections."""
    if not detections:
        return {
            "total_detections": 0,
            "unique_chips": 0,
            "avg_confidence": 0.0,
            "max_confidence": 0.0,
            "min_confidence": 0.0,
            "geo_located": 0,
            "high_conf": 0,
            "med_conf": 0,
            "low_conf": 0,
        }

    confs = [d["confidence"] for d in detections]
    geo_dets = [d for d in detections if d["centre_lat"] is not None]

    return {
        "total_detections": len(detections),
        "unique_chips": len(set(d["chip"] for d in detections)),
        "avg_confidence": np.mean(confs),
        "max_confidence": max(confs),
        "min_confidence": min(confs),
        "geo_located": len(geo_dets),
        "high_conf": sum(1 for c in confs if c > 0.7),
        "med_conf": sum(1 for c in confs if 0.5 < c <= 0.7),
        "low_conf": sum(1 for c in confs if c <= 0.5),
    }


def get_severity_color(confidence: float) -> str:
    """Return a hex colour based on detection confidence."""
    if confidence > 0.7:
        return "#ff4444"   # Red — high severity
    elif confidence > 0.5:
        return "#ffaa00"   # Orange — medium
    else:
        return "#44aaff"   # Blue — low


def get_severity_label(confidence: float) -> str:
    """Return a severity label."""
    if confidence > 0.7:
        return "🔴 Critical"
    elif confidence > 0.5:
        return "🟡 Warning"
    else:
        return "🔵 Monitor"


# ──────────────────────────────────────────────
# Forensic analysis
# ──────────────────────────────────────────────

def load_forensic_analysis() -> list[dict]:
    """Load forensic analysis from JSON report."""
    fa_path = Path("reports/forensic_analysis.json")
    if not fa_path.exists():
        return []
    with open(fa_path, "r") as f:
        data = json.load(f)
    # Accept both a raw list and a dict with an "analyses" key
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "analyses" in data:
        return data["analyses"]
    return []


def get_anomaly_type_color(anomaly_type: str) -> str:
    """Return hex colour for a given anomaly type."""
    colors = {
        "thermal_plume":    "#ff4444",
        "algal_bloom":      "#44ff44",
        "turbidity_spike":  "#aa8844",
        "oil_slick":        "#8844aa",
        "sewage_discharge": "#ff8844",
    }
    return colors.get(anomaly_type, "#888888")


def get_anomaly_type_icon(anomaly_type: str) -> str:
    """Return an emoji icon for a given anomaly type."""
    icons = {
        "thermal_plume":    "🌡️",
        "algal_bloom":      "🟢",
        "turbidity_spike":  "🟤",
        "oil_slick":        "🛢️",
        "sewage_discharge": "🚰",
    }
    return icons.get(anomaly_type, "🔵")


def compute_forensic_summary(analyses: list[dict]) -> dict:
    """Compute severity breakdown from forensic analyses."""
    summary = {
        "total": len(analyses),
        "CRITICAL": 0,
        "HIGH": 0,
        "WARNING": 0,
        "LOW": 0,
        "UNKNOWN": 0,
    }
    for a in analyses:
        sev = a.get("severity", "UNKNOWN").upper()
        if sev in summary:
            summary[sev] += 1
        else:
            summary["UNKNOWN"] += 1
    return summary
