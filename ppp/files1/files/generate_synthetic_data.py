"""
generate_synthetic_data.py
━━━━━━━━━━━━━━━━━━━━━━━━━━
Aqua-Sentinel AI — Synthetic Multi-Spectral Satellite Data Generator
─────────────────────────────────────────────────────────────────────
Creates realistic 32-bit GeoTIFF files mimicking Landsat 8/9 TIRS data
over the Buddha Dariya study area.  Each scene contains:

  • River channel          — cooler water body (~292 K)
  • Urban heat islands     — warm built-up areas (~308 K)
  • Agricultural backdrop  — moderate temperatures (~300 K)
  • Multi-class anomalies  — thermal plumes, algal blooms,
                             turbidity spikes, oil slicks,
                             and sewage discharge events
  • Perlin-style terrain noise for realism
  • NoData borders mimicking satellite swath edges

The ground-truth anomaly locations (with class labels) are saved
alongside each GeoTIFF so that the auto-annotation module can
produce perfect multi-class labels.

Usage
-----
    python generate_synthetic_data.py

Output
------
    data/raw_geotiff/             ← Synthetic GeoTIFFs
    data/synthetic_ground_truth/  ← JSON files with anomaly locations
"""

import json
import random
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np

from config import ROI, SYNTHETIC, PREPROCESS, RIVER_ONLY_MODE


# ──────────────────────────────────────────────
# Directories
# ──────────────────────────────────────────────
RAW_DIR = Path(PREPROCESS["raw_dir"])
GT_DIR  = Path("data/synthetic_ground_truth")
RAW_DIR.mkdir(parents=True, exist_ok=True)
GT_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────
# Perlin-style noise using multi-octave Gaussian
# ──────────────────────────────────────────────

def generate_smooth_noise(height: int, width: int, octaves: int = 5,
                          amplitude: float = 4.0, seed: int = None) -> np.ndarray:
    """
    Generate realistic terrain-like temperature noise using
    multi-octave smoothed random fields (fractional Brownian motion).

    This approximates Perlin noise without external dependencies.
    Each octave adds detail at a finer scale with reduced amplitude.
    """
    if seed is not None:
        np.random.seed(seed)

    from scipy.ndimage import gaussian_filter

    noise = np.zeros((height, width), dtype=np.float64)
    current_amp = amplitude
    current_freq = 1.0

    for octave in range(octaves):
        # Generate random field and smooth it
        sigma = max(height, width) / (4.0 * current_freq)
        raw = np.random.randn(height, width)
        smoothed = gaussian_filter(raw, sigma=sigma, mode='wrap')

        # Normalise to [-1, 1] then scale by amplitude
        if smoothed.max() != smoothed.min():
            smoothed = (smoothed - smoothed.min()) / (smoothed.max() - smoothed.min())
            smoothed = smoothed * 2 - 1

        noise += current_amp * smoothed

        current_amp *= 0.5       # Halve amplitude each octave
        current_freq *= 2.0      # Double frequency each octave

    return noise


# ──────────────────────────────────────────────
# River channel mask
# ──────────────────────────────────────────────

def generate_river_mask(height: int, width: int, river_width: int,
                        seed: int = None) -> np.ndarray:
    """
    Generate a meandering river channel mask.
    Uses sinusoidal curves with noise for natural meandering.
    """
    if seed is not None:
        np.random.seed(seed + 1000)

    mask = np.zeros((height, width), dtype=np.float32)

    # River flows roughly top-to-bottom with meandering
    base_x = width * 0.45
    freq1, freq2 = 0.008 + random.random() * 0.004, 0.015 + random.random() * 0.008
    amp1, amp2 = width * 0.12, width * 0.05

    for y in range(height):
        # Meandering centreline
        cx = base_x + amp1 * np.sin(freq1 * y) + amp2 * np.sin(freq2 * y + 1.5)
        cx = int(np.clip(cx, river_width, width - river_width))

        # Variable width
        w = river_width + int(3 * np.sin(0.02 * y))

        x_start = max(0, cx - w)
        x_end = min(width, cx + w)
        mask[y, x_start:x_end] = 1.0

    # Smooth edges
    from scipy.ndimage import gaussian_filter
    mask = gaussian_filter(mask, sigma=3.0)
    mask = np.clip(mask, 0, 1)

    return mask


# ──────────────────────────────────────────────
# Urban heat island mask
# ──────────────────────────────────────────────

def generate_urban_mask(height: int, width: int, seed: int = None) -> np.ndarray:
    """
    Generate urban heat island regions — clustered rectangular zones
    mimicking industrial and residential areas near the river.
    """
    if seed is not None:
        np.random.seed(seed + 2000)

    from scipy.ndimage import gaussian_filter

    mask = np.zeros((height, width), dtype=np.float32)

    # Create 4-8 urban clusters
    n_clusters = random.randint(4, 8)
    for _ in range(n_clusters):
        cx = random.randint(width // 5, 4 * width // 5)
        cy = random.randint(height // 5, 4 * height // 5)
        w = random.randint(40, 120)
        h = random.randint(40, 120)

        y1, y2 = max(0, cy - h // 2), min(height, cy + h // 2)
        x1, x2 = max(0, cx - w // 2), min(width, cx + w // 2)
        mask[y1:y2, x1:x2] = random.uniform(0.4, 1.0)

    mask = gaussian_filter(mask, sigma=12.0)
    mask = np.clip(mask, 0, 1)

    return mask


# ──────────────────────────────────────────────
# Anomaly shape profiles
# ──────────────────────────────────────────────
# Each anomaly type defines its own sigma ranges, intensity range,
# and Gaussian smoothing to produce a distinctive spatial signature.

ANOMALY_PROFILES = {
    "thermal_plume": {
        # Hot discharge — round-ish, high intensity
        "sigma_x_range": (10, 25),
        "sigma_y_range": (10, 30),
        "intensity_range": (0.7, 1.0),
        "smooth_sigma": 5.0,
    },
    "algal_bloom": {
        # Large area, lower intensity, irregular (big sigma, heavy blur)
        "sigma_x_range": (25, 55),
        "sigma_y_range": (25, 55),
        "intensity_range": (0.3, 0.6),
        "smooth_sigma": 12.0,
    },
    "turbidity_spike": {
        # Elongated along water flow (large sigma_y, narrow sigma_x)
        "sigma_x_range": (6, 15),
        "sigma_y_range": (30, 70),
        "intensity_range": (0.4, 0.7),
        "smooth_sigma": 7.0,
    },
    "oil_slick": {
        # Thin elongated surface film
        "sigma_x_range": (4, 10),
        "sigma_y_range": (35, 75),
        "intensity_range": (0.3, 0.6),
        "smooth_sigma": 4.0,
    },
    "sewage_discharge": {
        # Moderate temperature + moderate spread
        "sigma_x_range": (12, 30),
        "sigma_y_range": (15, 40),
        "intensity_range": (0.5, 0.8),
        "smooth_sigma": 8.0,
    },
}


# ──────────────────────────────────────────────
# Multi-class anomaly plume generator
# ──────────────────────────────────────────────

def _find_river_pixels(river_mask: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    """Return (N, 2) array of [row, col] coordinates of river pixels."""
    river_binary = (river_mask > threshold).astype(np.uint8)
    rows, cols = np.where(river_binary > 0)
    return np.column_stack([rows, cols]) if len(rows) > 0 else np.empty((0, 2), dtype=int)


def generate_plumes(height: int, width: int, river_mask: np.ndarray,
                    count_range: tuple, seed: int = None) -> tuple:
    """
    Generate multi-class anomaly plumes STRICTLY INSIDE the river channel.

    RIVER-ONLY ENFORCEMENT:
      - Every plume centre is placed on a confirmed river pixel
      - Plume spread is clipped to the river mask boundary
      - No anomalies leak onto roads, buildings, or land areas
      - This ensures the model learns to detect ONLY river anomalies

    Returns
    -------
    plume_field : float32 array — additive temperature field
    plume_records : list of dicts with plume metadata (incl. class info)
    """
    if seed is not None:
        np.random.seed(seed + 3000)

    from scipy.ndimage import gaussian_filter

    anomaly_types = SYNTHETIC.get("anomaly_types", ["thermal_plume"])
    class_id_map = {name: idx for idx, name in enumerate(anomaly_types)}
    force_in_river = SYNTHETIC.get("force_plumes_in_river", True) or RIVER_ONLY_MODE

    plume_field = np.zeros((height, width), dtype=np.float32)
    plume_records = []

    n_plumes = random.randint(*count_range)

    # Get all river pixel locations for strict placement
    river_binary = (river_mask > 0.3).astype(np.float32)
    river_pixels = _find_river_pixels(river_mask, threshold=0.3)

    if len(river_pixels) == 0:
        print("  [WARN] No river pixels found — cannot place plumes")
        return plume_field, plume_records

    for i in range(n_plumes):
        anomaly_type = random.choice(anomaly_types)
        profile = ANOMALY_PROFILES[anomaly_type]

        if force_in_river:
            # STRICT RIVER PLACEMENT: pick a random pixel ON the river
            margin = 60
            valid_river = river_pixels[
                (river_pixels[:, 0] > margin) &
                (river_pixels[:, 0] < height - margin) &
                (river_pixels[:, 1] > margin) &
                (river_pixels[:, 1] < width - margin)
            ]
            if len(valid_river) == 0:
                valid_river = river_pixels

            idx = random.randint(0, len(valid_river) - 1)
            py, px = int(valid_river[idx, 0]), int(valid_river[idx, 1])
        else:
            # Legacy: place near river (not strictly inside)
            attempts = 0
            while attempts < 100:
                py = random.randint(50, height - 50)
                px = random.randint(50, width - 50)
                local = river_binary[max(0, py-80):min(height, py+80),
                                     max(0, px-80):min(width, px+80)]
                if local.sum() > 10:
                    break
                attempts += 1

        # Shape parameters from anomaly profile
        plume = np.zeros((height, width), dtype=np.float32)

        sigma_x = random.randint(*profile["sigma_x_range"])
        sigma_y = random.randint(*profile["sigma_y_range"])
        intensity = random.uniform(*profile["intensity_range"])

        for dy in range(-sigma_y * 3, sigma_y * 3):
            for dx in range(-sigma_x * 3, sigma_x * 3):
                yy, xx = py + dy, px + dx
                if 0 <= yy < height and 0 <= xx < width:
                    val = intensity * np.exp(
                        -0.5 * ((dx / sigma_x) ** 2 + (dy / sigma_y) ** 2)
                    )
                    plume[yy, xx] = max(plume[yy, xx], val)

        # Smooth for natural diffusion
        plume = gaussian_filter(plume, sigma=profile["smooth_sigma"])

        # RIVER-ONLY: clip plume to river channel so no anomaly leaks onto land
        if force_in_river:
            river_clip = gaussian_filter(river_binary, sigma=3.0)
            plume = plume * river_clip

        plume_field += plume

        # Record ground truth (bounding box in pixels + class info)
        # Compute tight bounding box from actual non-zero plume pixels
        plume_nonzero = plume > 0.01
        if np.any(plume_nonzero):
            rows_nz, cols_nz = np.where(plume_nonzero)
            bbox_x1 = int(np.min(cols_nz))
            bbox_y1 = int(np.min(rows_nz))
            bbox_x2 = int(np.max(cols_nz))
            bbox_y2 = int(np.max(rows_nz))
        else:
            bbox_x1 = max(0, px - sigma_x * 3)
            bbox_y1 = max(0, py - sigma_y * 3)
            bbox_x2 = min(width, px + sigma_x * 3)
            bbox_y2 = min(height, py + sigma_y * 3)

        plume_records.append({
            "id": i,
            "anomaly_type": anomaly_type,
            "class_id": class_id_map[anomaly_type],
            "center_px": [int(px), int(py)],
            "bbox_px": [int(bbox_x1), int(bbox_y1), int(bbox_x2), int(bbox_y2)],
            "sigma": [int(sigma_x), int(sigma_y)],
            "intensity": round(float(intensity), 3),
            "river_only": force_in_river,
        })

    plume_field = np.clip(plume_field, 0, 1)
    return plume_field, plume_records


# ──────────────────────────────────────────────
# NoData border (satellite swath edge)
# ──────────────────────────────────────────────

def apply_nodata_border(arr: np.ndarray, border_px: int,
                        seed: int = None) -> np.ndarray:
    """Add irregular NoData borders mimicking satellite swath edges."""
    if seed is not None:
        np.random.seed(seed + 4000)

    result = arr.copy()
    h, w = result.shape

    # Irregular top/bottom/left/right borders
    for col in range(w):
        top_depth = border_px + random.randint(-5, 5)
        bot_depth = border_px + random.randint(-5, 5)
        result[:max(0, top_depth), col] = 0
        result[max(0, h - bot_depth):, col] = 0

    for row in range(h):
        left_depth = border_px + random.randint(-5, 5)
        right_depth = border_px + random.randint(-5, 5)
        result[row, :max(0, left_depth)] = 0
        result[row, max(0, w - right_depth):] = 0

    return result


# ──────────────────────────────────────────────
# Scene composer
# ──────────────────────────────────────────────

def compose_scene(scene_idx: int) -> tuple:
    """
    Compose a complete synthetic thermal scene.

    Returns
    -------
    temperature_array : float32 (H, W) — temperature in Kelvin
    plume_records     : list of dicts — ground truth plume locations
    """
    S = SYNTHETIC
    H, W = S["image_height"], S["image_width"]
    seed = 42 + scene_idx * 137

    print(f"  [GEN] Scene {scene_idx + 1}/{S['num_scenes']}  (seed={seed})")

    # 1. Base temperature field with terrain noise
    terrain_noise = generate_smooth_noise(
        H, W, octaves=S["noise_octaves"],
        amplitude=S["noise_amplitude"], seed=seed
    )
    temp_field = S["base_temp_k"] + terrain_noise

    # 2. River channel (cooler)
    river_mask = generate_river_mask(H, W, S["river_width_px"], seed=seed)
    temp_field = temp_field * (1 - river_mask) + S["river_temp_k"] * river_mask
    # Add slight variation within river
    river_noise = generate_smooth_noise(H, W, octaves=3, amplitude=1.5, seed=seed + 500)
    temp_field += river_noise * river_mask

    # 3. Urban heat islands (warmer)
    urban_mask = generate_urban_mask(H, W, seed=seed)
    urban_boost = (S["urban_temp_k"] - S["base_temp_k"]) * urban_mask
    temp_field += urban_boost

    # 4. Industrial thermal plumes (hot spots)
    plume_field, plume_records = generate_plumes(
        H, W, river_mask, S["plume_count_range"], seed=seed
    )
    plume_temps = (S["plume_temp_k"] - S["base_temp_k"]) * plume_field
    temp_field += plume_temps

    # 5. Add sensor noise (subtle)
    np.random.seed(seed + 9000)
    sensor_noise = np.random.normal(0, 0.3, (H, W)).astype(np.float32)
    temp_field += sensor_noise

    # 6. NoData border
    temp_field = apply_nodata_border(
        temp_field.astype(np.float32), S["nodata_border_px"], seed=seed
    )

    return temp_field.astype(np.float32), plume_records


# ──────────────────────────────────────────────
# GeoTIFF writer
# ──────────────────────────────────────────────

def save_geotiff(arr: np.ndarray, path: Path, scene_idx: int) -> None:
    """Save a float32 array as a GeoTIFF with proper CRS and transform."""
    try:
        import rasterio
        from rasterio.transform import from_bounds
    except ImportError:
        print("[ERROR] rasterio not installed.  pip install rasterio")
        return

    H, W = arr.shape
    transform = from_bounds(
        ROI["lon_min"], ROI["lat_min"],
        ROI["lon_max"], ROI["lat_max"],
        W, H,
    )

    meta = {
        "driver":   "GTiff",
        "dtype":    "float32",
        "count":    1,
        "height":   H,
        "width":    W,
        "crs":      "EPSG:4326",   # Geographic coords for simplicity
        "transform": transform,
        "nodata":   0.0,
    }

    with rasterio.open(str(path), "w", **meta) as dst:
        dst.write(arr, 1)


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main() -> None:
    S = SYNTHETIC
    anomaly_types = S.get("anomaly_types", ["thermal_plume"])
    print("=" * 60)
    print("  Aqua-Sentinel AI — Synthetic Multi-Spectral Data Generator")
    print(f"  Study Area      : {ROI['name']}")
    print(f"  Scenes          : {S['num_scenes']}")
    print(f"  Image Size      : {S['image_width']} x {S['image_height']} px")
    print(f"  Anomaly Classes : {', '.join(anomaly_types)}")
    print("=" * 60)

    base_date = datetime(2023, 1, 15)

    all_ground_truth = {}

    for i in range(S["num_scenes"]):
        # Generate scene
        temp_arr, plumes = compose_scene(i)

        # Create realistic filename with location prefix
        scene_date = base_date + timedelta(days=i * 45)
        date_str = scene_date.strftime("%Y-%m-%d")
        # Sanitize location name for filename
        import re
        loc_tag = re.sub(r'[^A-Za-z0-9]+', '_', ROI.get('water_body', 'Unknown')).strip('_')[:30]
        filename = f"{loc_tag}_ST_{date_str}_scene{i+1:03d}.tif"

        # Save GeoTIFF
        tif_path = RAW_DIR / filename
        save_geotiff(temp_arr, tif_path, i)

        # Save ground truth (with multi-class anomaly info)
        # Build per-class summary counts
        class_counts = {}
        for p in plumes:
            atype = p.get("anomaly_type", "thermal_plume")
            class_counts[atype] = class_counts.get(atype, 0) + 1

        gt = {
            "scene": filename,
            "date": date_str,
            "study_area": ROI.get("name", "Unknown"),
            "state": ROI.get("state", ""),
            "city": ROI.get("city", ""),
            "water_body": ROI.get("water_body", ""),
            "water_type": ROI.get("water_type", ""),
            "bbox": [ROI.get("lon_min"), ROI.get("lat_min"), ROI.get("lon_max"), ROI.get("lat_max")],
            "num_plumes": len(plumes),
            "class_counts": class_counts,
            "anomaly_types": anomaly_types,
            "plumes": plumes,
            "image_size": [S["image_width"], S["image_height"]],
        }
        gt_path = GT_DIR / f"{Path(filename).stem}_gt.json"
        with open(gt_path, "w") as f:
            json.dump(gt, f, indent=2)

        all_ground_truth[filename] = gt

        valid_pixels = np.sum(temp_arr > 0)
        total_pixels = temp_arr.size
        class_summary = ", ".join(f"{k}:{v}" for k, v in sorted(class_counts.items()))
        print(f"         -> {filename}  |  {len(plumes)} anomalies  |  "
              f"{class_summary}  |  {valid_pixels}/{total_pixels} valid px")

    # Summary
    total_plumes = sum(gt["num_plumes"] for gt in all_ground_truth.values())
    # Aggregate class counts across all scenes
    total_class_counts = {}
    for gt in all_ground_truth.values():
        for atype, cnt in gt.get("class_counts", {}).items():
            total_class_counts[atype] = total_class_counts.get(atype, 0) + cnt

    print(f"\n{'='*60}")
    print(f"  DONE  {S['num_scenes']} scenes generated -> {RAW_DIR}")
    print(f"         {total_plumes} total anomalies across {len(anomaly_types)} classes")
    for atype, cnt in sorted(total_class_counts.items()):
        print(f"           - {atype}: {cnt}")
    print(f"         Ground truth -> {GT_DIR}")
    print(f"  Next -> Run module2_preprocessing.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
