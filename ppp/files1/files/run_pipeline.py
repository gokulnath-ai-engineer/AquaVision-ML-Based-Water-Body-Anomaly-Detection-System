"""
run_pipeline.py
━━━━━━━━━━━━━━━
Aqua-Sentinel AI -- Unified Pipeline Runner
────────────────────────────────────────────
Single entry-point to run the entire Aqua-Sentinel AI pipeline for
hierarchical geo-intelligent multi-spectral water quality monitoring.

Usage
-----
    python run_pipeline.py                          # Full pipeline (demo mode)
    python run_pipeline.py --demo                   # Explicit demo mode
    python run_pipeline.py --module 2               # Run specific module only
    python run_pipeline.py --skip-training          # Skip YOLOv8 training
    python run_pipeline.py --epochs 10              # Quick training run
    python run_pipeline.py --state Punjab --city Ludhiana --water-body "Buddha Dariya"

Modules
-------
    1. Data Acquisition          (GEE + Sentinel-2 / Synthetic)
    2. Geo-Image Preprocessing   + NDWI Water Masking
    3. Auto-Annotation           (Multi-Class)
    4. YOLOv8 Multi-Class Training
    5. Inference + Forensic Analysis
    6. Report Generation         (HTML + PDF + GeoJSON)
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

from config import RIVER_ONLY_MODE, ROI
from geo_hierarchy import get_states, get_cities, get_water_bodies, get_roi


def print_banner():
    """Print a styled Aqua-Sentinel AI banner."""
    print()
    print("+" + "=" * 72 + "+")
    print("|" + " " * 72 + "|")
    print("|   Aqua-Sentinel AI -- Hierarchical Geo-Intelligent Framework" + " " * 9 + "|")
    print("|   Real-Time Multi-Spectral Water Quality Monitoring" + " " * 20 + "|")
    print("|   & Forensic Anomaly Reporting" + " " * 41 + "|")
    print("|" + " " * 72 + "|")
    print("+" + "=" * 72 + "+")
    print()


def print_step(step_num: int, total: int, title: str):
    """Print a step header."""
    print()
    print(f"+{'-'*60}+")
    print(f"|  Step {step_num}/{total}  {title:<49}|")
    print(f"+{'-'*60}+")
    print()


def run_module_1(demo: bool = True):
    """Module 1: Data Acquisition (GEE + Sentinel-2 / Synthetic)."""
    if demo:
        from generate_synthetic_data import main as gen_main
        gen_main()
    else:
        from module1_gee_acquisition import run_gee_pipeline
        run_gee_pipeline()


def run_module_2():
    """Module 2: Geo-Image Preprocessing + NDWI Water Masking."""
    from module2_preprocessing import main as preproc_main
    preproc_main()


def run_module_2b():
    """Module 3: Auto-Annotation (Multi-Class)."""
    from generate_training_dataset import main as annotate_main
    annotate_main()


def run_module_3(epochs: int = None, device: str = None):
    """Module 4: YOLOv8 Multi-Class Training."""
    from module3_train_yolov8 import main as train_main

    # Temporarily modify sys.argv for argparse in the module
    original_argv = sys.argv
    new_argv = ["module3_train_yolov8.py"]
    if epochs:
        new_argv += ["--epochs", str(epochs)]
    if device:
        new_argv += ["--device", device]
    sys.argv = new_argv

    try:
        train_main()
    finally:
        sys.argv = original_argv


def run_module_4():
    """Module 5: Inference + Forensic Analysis."""
    from module4_inference import run_inference
    run_inference(use_tiles=True)


def run_module_5():
    """Module 6: Report Generation (HTML + PDF + GeoJSON)."""
    forensic_path = Path("reports/forensic_analysis.json")
    if forensic_path.exists():
        print("  [*] Forensic results found -- generating PDF incident report ...")
        from pdf_report import generate_incident_report
        detections = []
        csv_path = Path("reports/detections.csv")
        if csv_path.exists():
            import csv
            with open(csv_path, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    detections.append({
                        "chip": row.get("chip"),
                        "confidence": float(row.get("confidence", 0.0) or 0.0),
                        "class": row.get("class"),
                        "anomaly_type": row.get("anomaly_type"),
                        "bbox_px": row.get("bbox_px"),
                        "centre_lat": float(row["centre_lat"]) if row.get("centre_lat") not in (None, "") else None,
                        "centre_lon": float(row["centre_lon"]) if row.get("centre_lon") not in (None, "") else None,
                        "timestamp": row.get("timestamp"),
                        "location_name": row.get("location_name"),
                    })

        forensic_analyses = []
        try:
            import json
            with open(forensic_path, "r", encoding="utf-8") as f:
                forensic_data = json.load(f)
            if isinstance(forensic_data, dict):
                forensic_analyses = forensic_data.get("analyses", [])
            elif isinstance(forensic_data, list):
                forensic_analyses = forensic_data
        except Exception as exc:
            print(f"  [WARN] Could not load forensic analysis data: {exc}")

        generate_incident_report(
            detections=detections,
            forensic_analyses=forensic_analyses,
            roi_info=ROI,
            output_path="reports/incident_report.pdf",
        )
    else:
        print("  [!] No forensic results at reports/forensic_analysis.json -- skipping PDF report.")


def main():
    parser = argparse.ArgumentParser(
        description="Aqua-Sentinel AI -- Unified Pipeline Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py                              # Full demo pipeline
  python run_pipeline.py --module 2                   # Only preprocessing
  python run_pipeline.py --epochs 10                  # Quick training
  python run_pipeline.py --skip-training              # Skip training step
  python run_pipeline.py --state Punjab --city Ludhiana --water-body "Buddha Dariya"
        """
    )
    parser.add_argument("--demo", action="store_true", default=True,
                        help="Use synthetic data (default: True)")
    parser.add_argument("--production", action="store_true",
                        help="Use real GEE data (requires authentication)")
    parser.add_argument("--module", type=int, choices=[1, 2, 3, 4, 5, 6],
                        help="Run a specific module only (1-6)")
    parser.add_argument("--skip-training", action="store_true",
                        help="Skip the training step (use existing weights)")
    parser.add_argument("--epochs", type=int, default=None,
                        help="Override training epochs")
    parser.add_argument("--device", type=str, default=None,
                        help="Force device: '0' for GPU, 'cpu' for CPU")
    parser.add_argument("--state", type=str, default=None,
                        help="Select state for geo hierarchy (e.g. Punjab)")
    parser.add_argument("--city", type=str, default=None,
                        help="Select city for geo hierarchy (e.g. Ludhiana)")
    parser.add_argument("--water-body", type=str, default=None,
                        help="Select water body for geo hierarchy (e.g. Buddha Dariya)")

    args = parser.parse_args()
    demo = not args.production

    print_banner()

    # ── Geo Hierarchy Selection ──────────────────
    if args.state or args.city or args.water_body:
        print("  --- Study Area Selection (Geo Hierarchy) ---")
        if args.state:
            print(f"  State      : {args.state}")
            available_cities = get_cities(args.state)
            print(f"  Available  : {len(available_cities)} cities in {args.state}")
        if args.city:
            print(f"  City       : {args.city}")
            available_bodies = get_water_bodies(args.state, args.city) if args.state else []
            print(f"  Available  : {len(available_bodies)} water bodies in {args.city}")
        if args.water_body:
            print(f"  Water Body : {args.water_body}")

        # Override ROI in config at runtime
        if args.state and args.city and args.water_body:
            roi = get_roi(args.state, args.city, args.water_body)
            if roi:
                os.environ["AQUA_SENTINEL_ROI"] = str(roi)
                print(f"  ROI        : {roi}")
            else:
                print("  [!] Could not resolve ROI for the given geo hierarchy selection.")
        print()

    start_time = time.time()
    print(f"  Started    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Mode       : {'DEMO (Synthetic Data)' if demo else 'PRODUCTION (GEE + Sentinel-2)'}")
    print(f"  River-Only : {RIVER_ONLY_MODE} — anomalies detected ONLY in rivers")
    print(f"  Water Body : {ROI.get('water_body', 'Buddha Dariya')}, {ROI.get('city', 'Ludhiana')}")
    print(f"  Training   : {'Skipped' if args.skip_training else f'{args.epochs or 200} epochs'}")
    print()

    # Determine which steps to run
    if args.module:
        modules_to_run = [args.module]
    elif args.skip_training:
        modules_to_run = [1, 2, 3, 5, 6]  # Skip module 4 (training)
    else:
        modules_to_run = [1, 2, 3, 4, 5, 6]

    total_steps = len(modules_to_run)
    step_counter = 0

    # ── Step 1: Data Acquisition ─────────────────
    if 1 in modules_to_run:
        step_counter += 1
        print_step(step_counter, total_steps, "Data Acquisition (GEE + Sentinel-2 / Synthetic)")
        run_module_1(demo=demo)

    # ── Step 2: Preprocessing + NDWI ─────────────
    if 2 in modules_to_run:
        step_counter += 1
        print_step(step_counter, total_steps, "Geo-Image Preprocessing + NDWI Water Masking")
        run_module_2()

    # ── Step 3: Auto-Annotation (Multi-Class) ────
    if 3 in modules_to_run:
        step_counter += 1
        print_step(step_counter, total_steps, "Auto-Annotation (Multi-Class)")
        run_module_2b()

    # ── Step 4: YOLOv8 Multi-Class Training ──────
    if 4 in modules_to_run:
        step_counter += 1
        print_step(step_counter, total_steps, "YOLOv8 Multi-Class Training")
        run_module_3(epochs=args.epochs, device=args.device)

    # ── Step 5: Inference + Forensic Analysis ────
    if 5 in modules_to_run:
        step_counter += 1
        print_step(step_counter, total_steps, "Inference + Forensic Analysis")
        run_module_4()

    # ── Step 6: Report Generation (HTML+PDF+GeoJSON)
    if 6 in modules_to_run:
        step_counter += 1
        print_step(step_counter, total_steps, "Report Generation (HTML + PDF + GeoJSON)")
        run_module_5()

    # ── Summary ──────────────────────────────────
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    print()
    print("+" + "=" * 72 + "+")
    print("|" + " " * 72 + "|")
    river_tag = " (RIVER-ONLY)" if RIVER_ONLY_MODE else ""
    print(f"|   AQUA-SENTINEL AI PIPELINE COMPLETE{river_tag}" + " " * max(0, 35 - len(river_tag)) + "|")
    print(f"|   Elapsed: {minutes}m {seconds}s" + " " * (59 - len(f"{minutes}m {seconds}s")) + "|")
    print("|" + " " * 72 + "|")

    # Show output locations
    outputs = [
        ("Heatmaps",          "data/processed_heatmaps/"),
        ("Dataset",           "data/dataset/"),
        ("Detections",        "reports/detections.csv"),
        ("Hotspots",          "reports/hotspots.geojson"),
        ("HTML Report",       "reports/summary_report.html"),
        ("Forensic Analysis", "reports/forensic_analysis.json"),
        ("PDF Report",        "reports/incident_report.pdf"),
    ]

    for name, path in outputs:
        if Path(path).exists():
            print(f"|   {name:20s} -> {path:<47}|")

    print("|" + " " * 72 + "|")
    print("|   Launch dashboard:  streamlit run dashboard.py" + " " * 24 + "|")
    print("|" + " " * 72 + "|")
    print("+" + "=" * 72 + "+")
    print()


if __name__ == "__main__":
    main()
