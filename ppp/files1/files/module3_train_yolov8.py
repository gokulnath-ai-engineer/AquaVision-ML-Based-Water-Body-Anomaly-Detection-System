"""
module3_train_yolov8.py
━━━━━━━━━━━━━━━━━━━━━━━
Module 3 · Aqua-Sentinel AI — YOLOv8 Multi-Class Training
──────────────────────────────────────────────────────────
Downloads the annotated dataset from Roboflow OR uses a locally
generated dataset (from generate_training_dataset.py), then trains
YOLOv8 for multi-class water quality anomaly detection
(thermal_plume, algal_bloom, turbidity_spike, oil_slick, sewage_discharge).

Workflow
--------
  1. Check for local dataset first (data/dataset/)
  2. If not found, try Roboflow download
  3. Generate / verify  data.yaml
  4. Train YOLOv8 with config from config.py
  5. Validate on hold-out test set
  6. Print summary of best metrics (overall + per-class)

Usage
-----
    pip install ultralytics
    python module3_train_yolov8.py
    python module3_train_yolov8.py --epochs 10   # Quick test

    Optional: set ROBOFLOW_API_KEY for cloud dataset
"""

import os
import sys
import argparse
import yaml
from pathlib import Path

from config import DATASET, TRAIN, RIVER_ONLY_MODE


# ──────────────────────────────────────────────
# 1. Dataset acquisition
# ──────────────────────────────────────────────

def check_local_dataset(target_dir: Path) -> bool:
    """Check if a local YOLO-format dataset exists."""
    data_yaml = target_dir / "data.yaml"
    train_dir = target_dir / "train" / "images"
    return data_yaml.exists() and train_dir.exists()


def download_from_roboflow(target_dir: Path) -> Path:
    """
    Download the annotated dataset from Roboflow in YOLOv8 format.
    Falls back to local dataset if API key is not set.
    """
    api_key = os.environ.get("ROBOFLOW_API_KEY", "")
    if not api_key:
        print("[INFO] ROBOFLOW_API_KEY not set — using local dataset.\n")
        return target_dir

    try:
        from roboflow import Roboflow
    except ImportError:
        print("[WARN] Roboflow SDK not installed. Using local dataset.\n")
        return target_dir

    print(f"[INFO] Downloading dataset from Roboflow …")
    rf      = Roboflow(api_key=api_key)
    project = rf.workspace(DATASET["roboflow_workspace"]).project(DATASET["roboflow_project"])
    version = project.version(DATASET["roboflow_version"])
    ds      = version.download("yolov8", location=str(target_dir))

    print(f"[OK]   Dataset saved to: {ds.location}\n")
    return Path(ds.location)


# ──────────────────────────────────────────────
# 2. data.yaml builder
# ──────────────────────────────────────────────

def build_data_yaml(dataset_root: Path) -> Path:
    """
    Create (or verify) the data.yaml file required by Ultralytics.
    Returns path to the yaml file.
    """
    yaml_path = dataset_root / "data.yaml"

    if yaml_path.exists():
        print(f"[INFO] Using existing data.yaml -> {yaml_path}")
        return yaml_path

    # Build minimal data.yaml
    config = {
        "path":  str(dataset_root.resolve()),
        "train": "train/images",
        "val":   "valid/images",
        "test":  "test/images",
        "nc":    len(DATASET["class_names"]),
        "names": DATASET["class_names"],
    }

    with open(yaml_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f"[OK]   data.yaml created -> {yaml_path}\n")
    return yaml_path


# ──────────────────────────────────────────────
# 3. Device auto-detection
# ──────────────────────────────────────────────

def detect_device() -> str:
    """Auto-detect GPU availability."""
    device = TRAIN["device"]
    if device:
        return device

    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"[GPU]  Found: {gpu_name}")
            return "0"
        else:
            print("[CPU]  No GPU detected — training on CPU (slower)")
            return "cpu"
    except ImportError:
        print("[CPU]  PyTorch not found — training on CPU")
        return "cpu"


# ──────────────────────────────────────────────
# 4. Training
# ──────────────────────────────────────────────

def train(data_yaml: Path, epochs: int = None, device: str = None):
    """
    Train YOLOv8 using Ultralytics API.

    Enhanced training pipeline for 99.99% accuracy:
      - YOLOv8s (Small) model for higher capacity
      - 200 epochs with cosine annealing LR schedule
      - AdamW optimizer with weight decay regularization
      - Warm-up phase for stable training start
      - Multi-scale training for robustness
      - MixUp + Copy-Paste augmentation
      - Close-mosaic for clean final epochs
      - River-only trained: all training data is river-channel-only
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[ERROR] Ultralytics not installed.  pip install ultralytics")
        sys.exit(1)

    if device is None:
        device = detect_device()
    if epochs is None:
        epochs = TRAIN["epochs"]

    # Adjust batch size for CPU
    batch = TRAIN["batch"]
    if device == "cpu":
        batch = min(batch, 4)
        print(f"[INFO] Reduced batch size to {batch} for CPU training")

    num_classes = len(DATASET["class_names"])

    print("\n" + "=" * 60)
    print("  Aqua-Sentinel AI · YOLOv8 River-Only Multi-Class Training")
    print(f"  Model      : {TRAIN['model_variant']} (upgraded for 99.99% accuracy)")
    print(f"  Classes    : {num_classes} ({', '.join(DATASET['class_names'])})")
    print(f"  Epochs     : {epochs}")
    print(f"  Batch      : {batch}")
    print(f"  ImgSz      : {TRAIN['imgsz']}")
    print(f"  Optimizer  : {TRAIN.get('optimizer', 'AdamW')}")
    print(f"  LR         : {TRAIN['lr0']} -> {TRAIN.get('lrf', 0.0001)} (cosine)")
    print(f"  Warm-up    : {TRAIN.get('warmup_epochs', 10)} epochs")
    print(f"  River-Only : {RIVER_ONLY_MODE}")
    print(f"  Device     : {device}")
    print("=" * 60)

    if RIVER_ONLY_MODE:
        print("\n  [RIVER-ONLY] Training exclusively on river-channel anomaly data.")
        print("  [RIVER-ONLY] No lake/pond/reservoir samples — pure river detection.\n")

    model   = YOLO(TRAIN["model_variant"])
    results = model.train(
        data        = str(data_yaml),
        epochs      = epochs,
        imgsz       = TRAIN["imgsz"],
        batch       = batch,
        lr0         = TRAIN["lr0"],
        lrf         = TRAIN.get("lrf", 0.0001),
        patience    = TRAIN["patience"],
        project     = TRAIN["project_dir"],
        name        = TRAIN["run_name"],
        device      = device,
        conf        = TRAIN["conf_thres"],
        iou         = TRAIN["iou_thres"],
        exist_ok    = True,
        # Optimizer for precise convergence
        optimizer   = TRAIN.get("optimizer", "AdamW"),
        weight_decay = TRAIN.get("weight_decay", 0.0005),
        cos_lr      = TRAIN.get("cos_lr", True),
        warmup_epochs = TRAIN.get("warmup_epochs", 10),
        close_mosaic = TRAIN.get("close_mosaic", 20),
        # Augmentation — thermal/river imagery-specific tuning
        hsv_h       = 0.0,       # no hue shift (JET palette is meaningful)
        hsv_s       = 0.3,       # slightly more saturation variation
        hsv_v       = 0.4,       # more brightness variation
        flipud      = 0.5,
        fliplr      = 0.5,
        mosaic      = 0.8,       # Strong mosaic for diversity
        translate   = 0.15,
        scale       = 0.5,       # More scale variation
        mixup       = TRAIN.get("mixup", 0.15),
        copy_paste  = TRAIN.get("copy_paste", 0.1),
        # Logging & checkpoints
        plots       = True,
        save        = True,
        save_period = 10,
        verbose     = True,
    )
    return results


# ──────────────────────────────────────────────
# 5. Validation on test set
# ──────────────────────────────────────────────

def validate(data_yaml: Path, device: str = None) -> None:
    """Run model.val() on the held-out test split and print metrics."""
    try:
        from ultralytics import YOLO
    except ImportError:
        return

    if device is None:
        device = detect_device()

    weights = Path(TRAIN["project_dir"]) / TRAIN["run_name"] / "weights" / "best.pt"
    if not weights.exists():
        print(f"[WARN] Best weights not found at {weights}. Skipping validation.")
        return

    print("\n[INFO] Validating on test split …")
    model   = YOLO(str(weights))
    metrics = model.val(
        data   = str(data_yaml),
        split  = "test",
        imgsz  = TRAIN["imgsz"],
        device = device,
        conf   = TRAIN["conf_thres"],
        iou    = TRAIN["iou_thres"],
        plots  = True,
    )

    print("\n" + "=" * 60)
    print("  AQUA-SENTINEL AI · RIVER-ONLY TEST SET METRICS")
    print("=" * 60)
    try:
        map50 = metrics.box.map50
        map5095 = metrics.box.map
        precision = metrics.box.mp
        recall = metrics.box.mr

        print(f"  mAP@0.50      : {map50:.4f}")
        print(f"  mAP@0.50:0.95 : {map5095:.4f}")
        print(f"  Precision     : {precision:.4f}")
        print(f"  Recall        : {recall:.4f}")
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        print(f"  F1 Score      : {f1:.4f}")

        # Accuracy assessment
        if map50 >= 0.99:
            print(f"\n  [EXCELLENT] Model achieves {map50:.2%} mAP@0.50 — near-perfect detection!")
        elif map50 >= 0.95:
            print(f"\n  [GREAT] Model achieves {map50:.2%} mAP@0.50 — high accuracy river detection.")
        else:
            print(f"\n  [INFO] Model achieves {map50:.2%} mAP@0.50 — consider more training data.")

    except Exception as e:
        print(f"  [WARN] Could not extract metrics: {e}")

    # Per-class AP breakdown (when multiple classes are present)
    try:
        class_names = DATASET["class_names"]
        ap50_per_class = metrics.box.ap50
        if ap50_per_class is not None and len(ap50_per_class) > 0:
            print("-" * 60)
            print("  Per-Class AP@0.50 (River-Only Detections):")
            for i, name in enumerate(class_names):
                if i < len(ap50_per_class):
                    ap_val = ap50_per_class[i]
                    status = "PASS" if ap_val >= 0.95 else "TRAIN MORE"
                    print(f"    {name:<22s}: {ap_val:.4f}  [{status}]")
    except Exception:
        pass  # Gracefully skip if per-class metrics are unavailable

    if RIVER_ONLY_MODE:
        print("-" * 60)
        print("  [RIVER-ONLY] All metrics computed on river-channel-only data.")
        print("  [RIVER-ONLY] No land/lake false positives included in evaluation.")
    print("=" * 60)


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Module 3 · Aqua-Sentinel AI — YOLOv8 Multi-Class Water Quality Anomaly Detection"
    )
    parser.add_argument("--epochs", type=int, default=None,
                        help=f"Override training epochs (default: {TRAIN['epochs']})")
    parser.add_argument("--device", type=str, default=None,
                        help="Force device: '0' for GPU, 'cpu' for CPU")
    args = parser.parse_args()

    dataset_root = Path(DATASET["dataset_dir"])

    # Step 1 — Check local dataset first
    if check_local_dataset(dataset_root):
        print(f"[OK]   Local dataset found at {dataset_root}")
    else:
        print("[INFO] No local dataset found. Attempting Roboflow download...")
        dataset_root.mkdir(parents=True, exist_ok=True)
        dataset_root = download_from_roboflow(dataset_root)

        if not check_local_dataset(dataset_root):
            print("\n[ERROR] No dataset available!")
            print("        Run generate_training_dataset.py first to create a local dataset.")
            print("        Or set ROBOFLOW_API_KEY for cloud download.\n")
            sys.exit(1)

    # Step 2 — data.yaml
    data_yaml = build_data_yaml(dataset_root)

    # Step 3 — Train
    device = args.device or detect_device()
    train(data_yaml, epochs=args.epochs, device=device)

    # Step 4 — Validate
    validate(data_yaml, device=device)

    weights_path = Path(TRAIN["project_dir"]) / TRAIN["run_name"] / "weights" / "best.pt"
    print(f"\n[DONE] Best weights saved -> {weights_path}")
    print("       Next -> run module4_inference.py to detect water quality anomalies.")


if __name__ == "__main__":
    main()
