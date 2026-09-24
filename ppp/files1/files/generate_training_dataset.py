"""
generate_training_dataset.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Aqua-Sentinel AI — Multi-Class Auto-Annotation Module
─────────────────────────────────────────────────────
Converts the binary anomaly masks produced by Module 2 into
YOLOv8-format bounding box annotations with multi-class labels,
creating a complete training dataset without needing Roboflow.

Supported anomaly classes (from config.DATASET["class_names"]):
  0: thermal_plume
  1: algal_bloom
  2: turbidity_spike
  3: oil_slick
  4: sewage_discharge

Ground truth JSON files from data/synthetic_ground_truth/ are used
to assign the correct class_id to each detected plume region based
on spatial overlap between mask contour bounding boxes and the
per-plume bounding boxes recorded during synthetic data generation.

Pipeline
--------
  1. Load ground truth plume metadata (class labels + bboxes)
  2. Read tiles and corresponding masks from data/processed_heatmaps/
  3. Find contours in each mask
  4. Match each contour bbox to the nearest ground truth plume
  5. Compute bounding boxes and convert to YOLO normalised format
  6. Split into train/valid/test directories
  7. Generate data.yaml for Ultralytics

Usage
-----
    python generate_training_dataset.py

Output
------
    data/dataset/
    ├── data.yaml
    ├── train/
    │   ├── images/
    │   └── labels/
    ├── valid/
    │   ├── images/
    │   └── labels/
    └── test/
        ├── images/
        └── labels/
"""

import os
import json
import re
import shutil
import random
from pathlib import Path

import cv2
import numpy as np

from config import PREPROCESS, DATASET


# ──────────────────────────────────────────────
# Directories
# ──────────────────────────────────────────────
TILES_DIR   = Path(PREPROCESS["processed_dir"]) / "tiles"
MASKS_DIR   = Path(PREPROCESS["processed_dir"]) / "masks"
DATASET_DIR = Path(DATASET["dataset_dir"])
GT_DIR      = Path("data/synthetic_ground_truth")

# Multi-class names (from config)
CLASS_NAMES = DATASET["class_names"]
NUM_CLASSES = len(CLASS_NAMES)


# ──────────────────────────────────────────────
# Ground truth loading
# ──────────────────────────────────────────────

def load_ground_truth() -> dict:
    """
    Load all ground truth JSON files from data/synthetic_ground_truth/.

    Returns a dict keyed by scene stem (e.g. 'BuddhaDariya_ST_2023-01-15_scene001')
    mapping to a list of plume records.  Each plume record contains at minimum:
        - bbox_px: [x1, y1, x2, y2] in full-scene pixel coordinates
        - class_id: int (anomaly class index)
        - anomaly_type: str
    For legacy GT files that lack class_id/anomaly_type fields, class_id
    defaults to 0 (thermal_plume).
    """
    ground_truth = {}

    if not GT_DIR.exists():
        print(f"  [WARN] Ground truth directory not found: {GT_DIR}")
        return ground_truth

    gt_files = sorted(GT_DIR.glob("*_gt.json"))
    if not gt_files:
        print(f"  [WARN] No *_gt.json files found in {GT_DIR}")
        return ground_truth

    for gt_path in gt_files:
        with open(gt_path, "r") as f:
            data = json.load(f)

        # Derive scene stem from the "scene" field (drop .tif extension)
        scene_file = data.get("scene", gt_path.stem.replace("_gt", ".tif"))
        scene_stem = Path(scene_file).stem

        plumes = data.get("plumes", [])
        image_size = data.get("image_size", [2000, 2000])

        enriched_plumes = []
        for p in plumes:
            enriched_plumes.append({
                "bbox_px":      p["bbox_px"],               # [x1, y1, x2, y2]
                "center_px":    p.get("center_px", [0, 0]),
                "class_id":     p.get("class_id", 0),       # default: thermal_plume
                "anomaly_type": p.get("anomaly_type", "thermal_plume"),
                "intensity":    p.get("intensity", 0.0),
            })

        ground_truth[scene_stem] = {
            "plumes":     enriched_plumes,
            "image_size": image_size,
        }

    print(f"  [GT]  Loaded {len(ground_truth)} scene ground truth files "
          f"({sum(len(v['plumes']) for v in ground_truth.values())} total plumes)")

    return ground_truth


def _bbox_intersection_area(box_a: list, box_b: list) -> float:
    """
    Compute the intersection area of two bounding boxes.
    Each box is [x1, y1, x2, y2].
    """
    x1 = max(box_a[0], box_b[0])
    y1 = max(box_a[1], box_b[1])
    x2 = min(box_a[2], box_b[2])
    y2 = min(box_a[3], box_b[3])

    if x2 <= x1 or y2 <= y1:
        return 0.0
    return float((x2 - x1) * (y2 - y1))


def _tile_offset_from_stem(tile_stem: str, tile_size: int, overlap: int,
                           scene_width: int) -> tuple[int, int]:
    """
    Compute the (row_start, col_start) pixel offset of a tile within
    the full scene, based on its tile index embedded in the name.

    Tile names follow the pattern: {scene_stem}_tile{NNNN}
    Tiles are generated in row-major order with stride = tile_size - overlap.
    """
    m = re.search(r"_tile(\d+)$", tile_stem)
    if not m:
        return (0, 0)

    tile_idx = int(m.group(1))
    stride = tile_size - overlap

    # Number of tiles per row in the scene
    cols_per_row = max(1, (scene_width - tile_size) // stride + 1)

    row_idx = tile_idx // cols_per_row
    col_idx = tile_idx % cols_per_row

    row_start = row_idx * stride
    col_start = col_idx * stride

    return (row_start, col_start)


def _scene_stem_from_tile(tile_stem: str) -> str:
    """
    Extract the scene stem from a tile stem.
    E.g. 'BuddhaDariya_ST_2023-01-15_scene001_tile0003' -> 'BuddhaDariya_ST_2023-01-15_scene001'
    """
    m = re.search(r"^(.+)_tile\d+$", tile_stem)
    return m.group(1) if m else tile_stem


def match_class_id_for_contour(contour_bbox: list, tile_row: int, tile_col: int,
                               gt_plumes: list) -> int:
    """
    Given a contour bounding box [x, y, w, h] in tile-local coordinates and
    the tile's offset within the scene, find the best-matching ground truth
    plume and return its class_id.

    The contour bbox is converted to scene-level coordinates and compared
    against each GT plume's bbox_px using intersection area.

    Returns the class_id of the best-matching plume, or 0 if no match found.
    """
    # Convert tile-local contour bbox to scene-level [x1, y1, x2, y2]
    cx1 = tile_col + contour_bbox[0]
    cy1 = tile_row + contour_bbox[1]
    cx2 = cx1 + contour_bbox[2]
    cy2 = cy1 + contour_bbox[3]
    scene_bbox = [cx1, cy1, cx2, cy2]

    best_class_id = 0
    best_overlap = 0.0

    for plume in gt_plumes:
        gt_bbox = plume["bbox_px"]  # [x1, y1, x2, y2]
        overlap = _bbox_intersection_area(scene_bbox, gt_bbox)
        if overlap > best_overlap:
            best_overlap = overlap
            best_class_id = plume["class_id"]

    return best_class_id


# ──────────────────────────────────────────────
# Mask → YOLO bounding boxes
# ──────────────────────────────────────────────

def mask_to_yolo_labels(mask_path: Path, img_size: int, class_id: int = 0) -> list[str]:
    """
    Extract bounding boxes from a binary mask and convert to YOLO format.

    YOLO format: class_id  cx  cy  w  h  (all normalised to [0, 1])

    Parameters
    ----------
    mask_path : Path to the binary mask image.
    img_size  : Tile dimension in pixels (assumes square tiles).
    class_id  : Default class ID to assign to all detections in this mask.
                Used when no ground truth matching is available.

    Returns list of label strings (one per detected plume region).
    """
    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
    if mask is None:
        return []

    # Threshold to binary
    _, binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

    # Morphological cleanup — merge nearby regions, remove tiny specks
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)

    labels = []
    min_area = 100   # Ignore tiny noise regions (< 10×10 px)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue

        x, y, w, h = cv2.boundingRect(contour)

        # Skip if bbox is too thin (likely noise)
        if w < 8 or h < 8:
            continue

        # Add small padding (5% of size)
        pad_x = int(w * 0.05)
        pad_y = int(h * 0.05)
        x = max(0, x - pad_x)
        y = max(0, y - pad_y)
        w = min(img_size - x, w + 2 * pad_x)
        h = min(img_size - y, h + 2 * pad_y)

        # Convert to YOLO format (normalised centre x, centre y, width, height)
        cx = (x + w / 2) / img_size
        cy = (y + h / 2) / img_size
        nw = w / img_size
        nh = h / img_size

        labels.append(f"{class_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")

    return labels


def mask_to_yolo_labels_multiclass(
    mask_path: Path,
    img_size: int,
    tile_stem: str,
    gt_plumes: list,
    tile_row: int,
    tile_col: int,
) -> list[str]:
    """
    Extract bounding boxes from a binary mask and convert to YOLO format,
    assigning per-contour class IDs by matching against ground truth plumes.

    For each detected contour, the bounding box is mapped back to scene
    coordinates and compared against all GT plumes for the scene.  The
    plume with the largest bbox intersection determines the class_id.

    Falls back to class_id=0 when no GT plume overlaps a contour.
    """
    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
    if mask is None:
        return []

    # Threshold to binary
    _, binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

    # Morphological cleanup
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)

    labels = []
    min_area = 100

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue

        x, y, w, h = cv2.boundingRect(contour)

        if w < 8 or h < 8:
            continue

        # Match this contour to a GT plume to get the class_id
        cid = match_class_id_for_contour([x, y, w, h], tile_row, tile_col,
                                         gt_plumes)

        # Add small padding (5% of size)
        pad_x = int(w * 0.05)
        pad_y = int(h * 0.05)
        x = max(0, x - pad_x)
        y = max(0, y - pad_y)
        w = min(img_size - x, w + 2 * pad_x)
        h = min(img_size - y, h + 2 * pad_y)

        # Convert to YOLO format (normalised centre x, centre y, width, height)
        cx = (x + w / 2) / img_size
        cy = (y + h / 2) / img_size
        nw = w / img_size
        nh = h / img_size

        labels.append(f"{cid} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")

    return labels


# ──────────────────────────────────────────────
# Dataset splitter
# ──────────────────────────────────────────────

def split_tiles(tile_names: list[str], ratios: dict) -> dict[str, list[str]]:
    """
    Split tile names into train/valid/test sets.

    The dataset may be small in demo mode, so we enforce non-empty validation
    data when possible to avoid Ultralytics failing on an empty val directory.
    """
    random.seed(42)
    shuffled = tile_names.copy()
    random.shuffle(shuffled)

    n = len(shuffled)
    if n == 0:
        return {"train": [], "valid": [], "test": []}

    # Compute target counts from configured ratios, but guarantee at least one
    # sample in each non-empty split when the dataset is large enough.
    n_train = max(1, int(round(n * ratios["train"])))
    n_val = max(1, int(round(n * ratios["val"])))
    n_test = n - n_train - n_val

    if n >= 3 and n_test <= 0:
        # Keep validation non-empty and shrink training to preserve a test split
        # only if there are enough samples left after reserving val.
        n_val = max(1, min(n - 2, n_val))
        n_train = max(1, n - n_val - 1)
        n_test = n - n_train - n_val

    if n >= 2 and n_train + n_val > n:
        n_train = max(1, n - n_val)

    if n >= 2 and n_val > n - 1:
        n_val = n - 1
        n_train = 1

    # If the dataset is tiny, allow fewer splits to exist.
    if n == 1:
        return {"train": shuffled[:1], "valid": [], "test": []}
    if n == 2:
        return {"train": shuffled[:1], "valid": shuffled[1:], "test": []}

    n_train = min(n_train, n - 1)
    n_val = min(max(1, n_val), n - n_train)
    n_test = n - n_train - n_val

    if n_test < 0:
        n_test = 0

    splits = {
        "train": shuffled[:n_train],
        "valid": shuffled[n_train:n_train + n_val],
        "test": shuffled[n_train + n_val:n_train + n_val + n_test],
    }

    # Final safety: if validation is empty on a small but non-trivial set, move one
    # item from training into validation while preserving at least one training item.
    if not splits["valid"] and len(shuffled) >= 2:
        splits["valid"] = [shuffled[-1]]
        splits["train"] = shuffled[:-1]
        if not splits["train"]:
            splits["train"] = [shuffled[0]]
            splits["valid"] = [shuffled[1]]

    return splits


# ──────────────────────────────────────────────
# data.yaml generator
# ──────────────────────────────────────────────

def create_data_yaml(dataset_root: Path) -> None:
    """Create Ultralytics-compatible data.yaml."""
    import yaml

    config = {
        "path":  str(dataset_root.resolve()),
        "train": "train/images",
        "val":   "valid/images",
        "test":  "test/images",
        "nc":    len(DATASET["class_names"]),
        "names": DATASET["class_names"],
    }

    yaml_path = dataset_root / "data.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f"  [YAML] data.yaml -> {yaml_path}")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("  Aqua-Sentinel AI · Multi-Class Auto-Annotation")
    print(f"  Classes: {', '.join(CLASS_NAMES)}")
    print(f"  Tiles  : {TILES_DIR}")
    print(f"  Masks  : {MASKS_DIR}")
    print(f"  GT Dir : {GT_DIR}")
    print(f"  Output : {DATASET_DIR}")
    print("=" * 60)

    # Load ground truth for multi-class labelling
    ground_truth = load_ground_truth()

    # Collect all tile files
    tile_files = sorted(TILES_DIR.glob("*.png"))
    if not tile_files:
        print(f"\n[WARN] No tiles found in {TILES_DIR}.")
        print("       Run module2_preprocessing.py first.\n")
        return

    tile_size = PREPROCESS["tile_size"]
    tile_overlap = PREPROCESS["tile_overlap"]
    print(f"\n[INFO] Found {len(tile_files)} tiles. Processing labels...\n")

    # Process each tile
    tile_names = []
    label_data = {}    # tile_stem -> list of YOLO label strings
    stats = {
        "total": 0,
        "with_labels": 0,
        "total_boxes": 0,
        "per_class": {name: 0 for name in CLASS_NAMES},
    }

    for tile_path in tile_files:
        stem = tile_path.stem
        mask_path = MASKS_DIR / f"{stem}_mask.png"

        if not mask_path.exists():
            # Create empty label (negative sample)
            labels = []
        else:
            # Try multi-class labelling via ground truth
            scene_stem = _scene_stem_from_tile(stem)
            gt_entry = ground_truth.get(scene_stem)

            if gt_entry is not None:
                scene_width = gt_entry["image_size"][0]
                gt_plumes = gt_entry["plumes"]
                tile_row, tile_col = _tile_offset_from_stem(
                    stem, tile_size, tile_overlap, scene_width
                )
                labels = mask_to_yolo_labels_multiclass(
                    mask_path, tile_size, stem, gt_plumes,
                    tile_row, tile_col,
                )
            else:
                # No GT available — fall back to single-class (class 0)
                labels = mask_to_yolo_labels(mask_path, tile_size, class_id=0)

        tile_names.append(stem)
        label_data[stem] = labels
        stats["total"] += 1

        if labels:
            stats["with_labels"] += 1
            stats["total_boxes"] += len(labels)
            # Count per-class boxes
            for lbl in labels:
                cid = int(lbl.split()[0])
                if 0 <= cid < NUM_CLASSES:
                    stats["per_class"][CLASS_NAMES[cid]] += 1

    # Split
    splits = split_tiles(tile_names, DATASET["split_ratios"])

    print(f"  [SPLIT] train: {len(splits['train'])}  |  "
          f"valid: {len(splits['valid'])}  |  test: {len(splits['test'])}")

    # Create directory structure and copy files
    for split_name, names in splits.items():
        img_dir = DATASET_DIR / split_name / "images"
        lbl_dir = DATASET_DIR / split_name / "labels"
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)

        for stem in names:
            # Copy image
            src_img = TILES_DIR / f"{stem}.png"
            dst_img = img_dir / f"{stem}.png"
            shutil.copy2(src_img, dst_img)

            # Write label file
            dst_lbl = lbl_dir / f"{stem}.txt"
            labels = label_data.get(stem, [])
            with open(dst_lbl, "w") as f:
                f.write("\n".join(labels))

    # Generate data.yaml
    create_data_yaml(DATASET_DIR)

    print(f"\n{'='*60}")
    print(f"  DONE · Aqua-Sentinel AI Multi-Class Auto-Annotation Complete")
    print(f"         Total tiles      : {stats['total']}")
    print(f"         Tiles with labels: {stats['with_labels']}")
    print(f"         Total bboxes     : {stats['total_boxes']}")
    print(f"         Per-class breakdown:")
    for cls_name in CLASS_NAMES:
        count = stats['per_class'][cls_name]
        print(f"           {cls_name:20s}: {count}")
    print(f"         Dataset          : {DATASET_DIR}")
    print(f"  Next  -> Run module3_train_yolov8.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
