"""
module2_preprocessing.py
━━━━━━━━━━━━━━━━━━━━━━━━
Module 2 · Geo-Image Preprocessing  --  Aqua-Sentinel AI
─────────────────────────────────────────────────────────
Converts raw 32-bit Landsat Surface Temperature GeoTIFFs into:
  • Normalised JET-colourmap heatmap PNGs  (for visual inspection)
  • 640 × 640 px tiles                     (for YOLOv8 training)
  • Binary anomaly masks                   (for annotation guidance)
  • NDWI water masks                       (to eliminate land false positives)

Pipeline per file
-----------------
  1. Load GeoTIFF with Rasterio -- preserve CRS & transform
  2. Clean NoData borders (replace with NaN)
  3. Generate Water Mask (NDWI) from thermal fallback
  4. Apply Water Mask -- eliminate land pixels before analysis
  5. Normalise to uint8 [0, 255]
  6. Apply JET colormap
  7. Build anomaly mask (water-only)
  8. Tile into 640 x 640 px chips with configurable overlap
  9. Save metadata (per-chip geo-coordinates + water mask stats)

Usage
-----
    python module2_preprocessing.py

    Place downloaded GeoTIFFs in  data/raw_geotiff/
    Outputs land in              data/processed_heatmaps/
"""

import os
import json
import warnings
from pathlib import Path

import numpy as np
import cv2
import rasterio
from rasterio.transform import Affine

from config import PREPROCESS, ROI, RIVER_ONLY_MODE
from water_masking import (
    generate_water_mask_from_thermal,
    apply_water_mask,
    refine_water_mask,
    mask_statistics,
    visualize_water_mask,
)

warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)


# ──────────────────────────────────────────────
# Directory setup
# ──────────────────────────────────────────────

RAW_DIR       = Path(PREPROCESS["raw_dir"])
PROC_DIR      = Path(PREPROCESS["processed_dir"])
SPECTRAL_DIR  = Path(PREPROCESS["spectral_dir"])
TILES_DIR     = PROC_DIR / "tiles"
MASKS_DIR     = PROC_DIR / "masks"
META_DIR      = PROC_DIR / "meta"

for d in [TILES_DIR, MASKS_DIR, META_DIR, SPECTRAL_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────
# Core functions
# ──────────────────────────────────────────────

def load_geotiff(path: Path) -> tuple[np.ndarray, Affine, dict]:
    """
    Load a single-band GeoTIFF.

    Returns
    -------
    arr       : float32 array  (rows, cols) — values in Kelvin
    transform : Affine transform
    meta      : rasterio metadata dict
    """
    with rasterio.open(path) as src:
        arr  = src.read(1).astype(np.float32)
        meta = src.meta.copy()
        transform = src.transform
    return arr, transform, meta


def clean_nodata(arr: np.ndarray, nodata_val: float = 0.0) -> np.ndarray:
    """Replace NoData sentinels (0 or exact match) with NaN."""
    cleaned = arr.copy()
    cleaned[cleaned == nodata_val] = np.nan
    # Also remove physically impossible values
    cleaned[cleaned < 200] = np.nan   # < −73 °C  (never in Punjab)
    cleaned[cleaned > 360] = np.nan   # >  87 °C  (never natural)
    return cleaned


def normalise_to_uint8(
    arr: np.ndarray,
    t_min: float,
    t_max: float,
) -> np.ndarray:
    """
    Clamp to [t_min, t_max] Kelvin then scale to [0, 255] uint8.
    NaN pixels → 0.
    """
    clamped = np.clip(arr, t_min, t_max)
    normed  = (clamped - t_min) / (t_max - t_min)   # [0, 1]
    scaled  = (normed * 255).astype(np.uint8)
    scaled[np.isnan(arr)] = 0
    return scaled


def apply_jet_colormap(grey: np.ndarray) -> np.ndarray:
    """Apply OpenCV JET colormap; returns BGR uint8 (H, W, 3)."""
    return cv2.applyColorMap(grey, cv2.COLORMAP_JET)


# ──────────────────────────────────────────────
# Extra heatmap generators (river-focused)
# ──────────────────────────────────────────────

# Map colormap names to OpenCV constants
_COLORMAP_LOOKUP = {
    "JET":     cv2.COLORMAP_JET,
    "INFERNO": cv2.COLORMAP_INFERNO,
    "HOT":     cv2.COLORMAP_HOT,
    "TURBO":   cv2.COLORMAP_TURBO,
    "OCEAN":   cv2.COLORMAP_OCEAN,
    "MAGMA":   cv2.COLORMAP_MAGMA,
    "PLASMA":  cv2.COLORMAP_PLASMA,
    "VIRIDIS": cv2.COLORMAP_VIRIDIS,
}


def generate_extra_heatmaps(
    grey: np.ndarray,
    water_mask: np.ndarray,
    anomaly_mask: np.ndarray,
    stem: str,
    output_dir: Path,
) -> list[Path]:
    """
    Generate multiple heatmap visualisations for the river area.

    Produces:
      1. Multi-colormap heatmaps (INFERNO, HOT, TURBO, OCEAN)
      2. River-isolated thermal heatmap (only river pixels, land blacked out)
      3. Anomaly density heatmap (Gaussian-blurred anomaly overlay)
      4. River thermal gradient map (highlights temperature transitions)
      5. Water mask overlay with anomaly contours

    Returns list of saved file paths.
    """
    saved = []
    colormaps = PREPROCESS.get("heatmap_colormaps", ["JET", "INFERNO", "HOT"])

    # 1. Multi-colormap heatmaps
    for cmap_name in colormaps:
        if cmap_name == "JET":
            continue  # Already generated as primary
        cmap_id = _COLORMAP_LOOKUP.get(cmap_name, cv2.COLORMAP_JET)
        coloured = cv2.applyColorMap(grey, cmap_id)
        path = output_dir / f"{stem}_heatmap_{cmap_name.lower()}.png"
        cv2.imwrite(str(path), coloured)
        saved.append(path)

    # 2. River-isolated thermal heatmap (land = black)
    river_grey = grey.copy()
    river_grey[water_mask == 0] = 0
    river_colour = cv2.applyColorMap(river_grey, cv2.COLORMAP_JET)
    # Make land pixels dark grey instead of blue
    river_colour[water_mask == 0] = [30, 30, 30]
    path = output_dir / f"{stem}_heatmap_river_only.png"
    cv2.imwrite(str(path), river_colour)
    saved.append(path)

    # 3. Anomaly density heatmap (Gaussian-blurred hot zones)
    from scipy.ndimage import gaussian_filter
    anomaly_float = anomaly_mask.astype(np.float32) / 255.0
    density = gaussian_filter(anomaly_float, sigma=15.0)
    density_norm = (density / max(density.max(), 1e-6) * 255).astype(np.uint8)
    density_colour = cv2.applyColorMap(density_norm, cv2.COLORMAP_HOT)
    # Overlay on dark background
    density_colour[density_norm < 5] = [20, 20, 20]
    path = output_dir / f"{stem}_heatmap_anomaly_density.png"
    cv2.imwrite(str(path), density_colour)
    saved.append(path)

    # 4. River thermal gradient map (Sobel edge detection on river temps)
    river_float = grey.astype(np.float32)
    river_float[water_mask == 0] = 0
    grad_x = cv2.Sobel(river_float, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(river_float, cv2.CV_32F, 0, 1, ksize=3)
    gradient_mag = np.sqrt(grad_x**2 + grad_y**2)
    gradient_mag = np.clip(gradient_mag / max(gradient_mag.max(), 1e-6) * 255, 0, 255).astype(np.uint8)
    gradient_colour = cv2.applyColorMap(gradient_mag, cv2.COLORMAP_TURBO)
    gradient_colour[water_mask == 0] = [20, 20, 20]
    path = output_dir / f"{stem}_heatmap_thermal_gradient.png"
    cv2.imwrite(str(path), gradient_colour)
    saved.append(path)

    # 5. Water mask overlay with anomaly contours
    base_colour = cv2.applyColorMap(grey, cv2.COLORMAP_JET)
    overlay = base_colour.copy()
    # Blue tint for water
    water_tint = np.zeros_like(overlay)
    water_tint[water_mask == 1] = [200, 120, 0]  # Blue for water
    overlay = cv2.addWeighted(overlay, 0.7, water_tint, 0.3, 0)
    # Draw anomaly contours in bright red
    contours, _ = cv2.findContours(anomaly_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours, -1, (0, 0, 255), 2)
    path = output_dir / f"{stem}_heatmap_annotated_overlay.png"
    cv2.imwrite(str(path), overlay)
    saved.append(path)

    return saved


def build_anomaly_mask(arr: np.ndarray, delta_k: float) -> np.ndarray:
    """
    Binary mask where temperature exceeds local mean + delta_k.

    Returns uint8 array: 255 = anomaly, 0 = normal / NoData.
    """
    valid = arr[~np.isnan(arr)]
    if valid.size == 0:
        return np.zeros(arr.shape, dtype=np.uint8)
    mean_k = float(np.nanmean(arr))
    mask   = (arr > (mean_k + delta_k)).astype(np.uint8) * 255
    mask[np.isnan(arr)] = 0
    return mask


def pixel_to_latlon(row: int, col: int, transform: Affine) -> tuple[float, float]:
    """Convert pixel (row, col) → (lat, lon) using rasterio Affine transform."""
    lon, lat = rasterio.transform.xy(transform, row, col)
    return float(lat), float(lon)


def tile_image(
    colour_img: np.ndarray,
    mask_img:   np.ndarray,
    transform:  Affine,
    stem:       str,
    tile_size:  int,
    overlap:    int,
) -> list[dict]:
    """
    Slice colour_img and mask_img into chips sized to the image dimensions
    when the image is smaller than the configured tile size.
    Returns list of metadata dicts (one per chip).
    """
    H, W = colour_img.shape[:2]
    effective_tile_size = min(tile_size, H, W)
    if effective_tile_size < tile_size:
        print(f"  [INFO] Image smaller than configured tile size ({H}x{W}px -> using {effective_tile_size}px chips)")

    stride = max(1, effective_tile_size - overlap)
    metadata = []
    tile_idx = 0

    for r in range(0, H - effective_tile_size + 1, stride):
        for c in range(0, W - effective_tile_size + 1, stride):
            chip   = colour_img[r:r + effective_tile_size, c:c + effective_tile_size]
            m_chip = mask_img[r:r + effective_tile_size, c:c + effective_tile_size]

            chip_name = f"{stem}_tile{tile_idx:04d}"

            # Save colour tile
            cv2.imwrite(str(TILES_DIR / f"{chip_name}.png"), chip)

            # Save anomaly mask tile
            cv2.imwrite(str(MASKS_DIR / f"{chip_name}_mask.png"), m_chip)

            # Compute corner coordinates for this chip
            lat_tl, lon_tl = pixel_to_latlon(r,             c,             transform)
            lat_br, lon_br = pixel_to_latlon(r + effective_tile_size, c + effective_tile_size, transform)

            meta = {
                "chip_name": chip_name,
                "source":    stem,
                "row_start": r,
                "col_start": c,
                "tile_size": effective_tile_size,
                "bbox_latlon": {
                    "top_left":     {"lat": lat_tl, "lon": lon_tl},
                    "bottom_right": {"lat": lat_br, "lon": lon_br},
                },
                "anomaly_pixels": int(np.sum(m_chip > 0)),
            }
            metadata.append(meta)
            tile_idx += 1

    # If the image is smaller than the tilesize, the loops above do not execute.
    # Add one full-frame chip in that case so the pipeline still produces data.
    if not metadata and (H > 0 and W > 0):
        chip = colour_img[:effective_tile_size, :effective_tile_size]
        m_chip = mask_img[:effective_tile_size, :effective_tile_size]
        chip_name = f"{stem}_tile{tile_idx:04d}"
        cv2.imwrite(str(TILES_DIR / f"{chip_name}.png"), chip)
        cv2.imwrite(str(MASKS_DIR / f"{chip_name}_mask.png"), m_chip)

        lat_tl, lon_tl = pixel_to_latlon(0, 0, transform)
        lat_br, lon_br = pixel_to_latlon(effective_tile_size, effective_tile_size, transform)
        metadata.append({
            "chip_name": chip_name,
            "source": stem,
            "row_start": 0,
            "col_start": 0,
            "tile_size": effective_tile_size,
            "bbox_latlon": {
                "top_left": {"lat": lat_tl, "lon": lon_tl},
                "bottom_right": {"lat": lat_br, "lon": lon_br},
            },
            "anomaly_pixels": int(np.sum(m_chip > 0)),
        })

    return metadata


# ──────────────────────────────────────────────
# Per-file pipeline
# ──────────────────────────────────────────────

def process_file(tif_path: Path) -> dict:
    stem = tif_path.stem
    print(f"  [PROC] {tif_path.name}")

    # Step 1: Load GeoTIFF
    arr, transform, _ = load_geotiff(tif_path)
    print(f"         Step 1/9  Load GeoTIFF          ({arr.shape[0]}x{arr.shape[1]} px)")

    # Step 2: Clean NoData
    arr = clean_nodata(arr, PREPROCESS["nodata_value"])
    print(f"         Step 2/9  Clean NoData")

    # Step 3: Generate Water Mask (NDWI)
    # In demo / single-band thermal mode we derive an approximate mask
    # from the thermal data itself (cooler pixels = likely water).
    # RIVER-ONLY MODE: use tighter percentile for strict river-channel mask
    river_percentile = PREPROCESS.get("river_mask_percentile", 12) if RIVER_ONLY_MODE else 30
    raw_water_mask = generate_water_mask_from_thermal(arr, percentile=river_percentile)
    water_mask = refine_water_mask(raw_water_mask, min_area=100)
    wm_stats = mask_statistics(water_mask)
    print(f"         Step 3/9  Generate Water Mask    "
          f"(water {wm_stats['water_percentage']:.1f}%)")
    if RIVER_ONLY_MODE:
        print("  [RIVER-ONLY] Strict river channel mask — anomalies detected ONLY in rivers.")
    else:
        print("  [WATER MASK] Only water pixels will be analyzed. Roads/buildings excluded.")

    # Step 4: Apply Water Mask
    # Mask out land pixels before anomaly detection to eliminate
    # false positives from roads, buildings, and bare soil.
    arr_water_only = apply_water_mask(arr, water_mask)
    print(f"         Step 4/9  Apply Water Mask       "
          f"({wm_stats['water_pixels']} water px kept)")

    # Step 5: Normalise to uint8
    grey = normalise_to_uint8(
        arr,
        PREPROCESS["temp_min_k"],
        PREPROCESS["temp_max_k"],
    )
    print(f"         Step 5/9  Normalise to uint8")

    # Step 6: Apply JET colormap
    colour = apply_jet_colormap(grey)
    print(f"         Step 6/9  Apply JET colormap")

    # Save full-resolution heatmap
    full_out = PROC_DIR / f"{stem}_heatmap.png"
    cv2.imwrite(str(full_out), colour)

    # Save water mask visualisation alongside heatmap
    water_vis = visualize_water_mask(colour, water_mask, alpha=0.4)
    water_vis_path = PROC_DIR / f"{stem}_water_mask.png"
    cv2.imwrite(str(water_vis_path), water_vis)

    # Step 6b: Generate extra heatmaps (multi-colormap, river-only, gradients)
    if PREPROCESS.get("generate_extra_heatmaps", True):
        # Build anomaly mask early so we can overlay it on heatmaps
        _anom_mask = build_anomaly_mask(arr_water_only, PREPROCESS["anomaly_delta_k"])
        _anom_mask = _anom_mask * water_mask
        extra_paths = generate_extra_heatmaps(
            grey=grey,
            water_mask=water_mask,
            anomaly_mask=_anom_mask,
            stem=stem,
            output_dir=PROC_DIR,
        )
        print(f"         Step 6b   Extra Heatmaps         ({len(extra_paths)} maps generated)")

    # Step 7: Build anomaly mask (water-only)
    # Uses the water-masked array so only water pixels can trigger anomalies.
    mask = build_anomaly_mask(arr_water_only, PREPROCESS["anomaly_delta_k"])
    # Multiply anomaly mask by water mask so no land anomalies leak through
    mask = mask * water_mask
    print(f"         Step 7/9  Build anomaly mask     (water-only)")

    # Step 8: Tile
    #   Pass the WATER mask (not anomaly mask) so inference can filter
    #   detections that fall on land.  The water_mask is uint8 (0/1),
    #   scale to 0/255 for PNG storage.
    water_mask_255 = (water_mask * 255).astype(np.uint8)
    chips_meta = tile_image(
        colour_img=colour,
        mask_img=water_mask_255,
        transform=transform,
        stem=stem,
        tile_size=PREPROCESS["tile_size"],
        overlap=PREPROCESS["tile_overlap"],
    )
    print(f"         Step 8/9  Tile                   ({len(chips_meta)} chips)")

    # Step 9: Save metadata
    meta_path = META_DIR / f"{stem}_meta.json"
    with open(meta_path, "w") as f:
        json.dump(chips_meta, f, indent=2)

    # Save water mask statistics to spectral analysis directory as JSON
    wm_stats["source_file"] = tif_path.name
    wm_stats_path = SPECTRAL_DIR / f"{stem}_water_mask_stats.json"
    with open(wm_stats_path, "w") as f:
        json.dump(wm_stats, f, indent=2)

    anomalous = sum(1 for m in chips_meta if m["anomaly_pixels"] > 0)
    print(f"         Step 9/9  Save metadata")
    print(f"         -> {len(chips_meta)} tiles  |  {anomalous} anomaly tiles  "
          f"|  water {wm_stats['water_percentage']:.1f}%  |  heatmap saved")

    return wm_stats


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("  Aqua-Sentinel AI · Module 2 · Geo-Image Preprocessing")
    print(f"  Input    : {RAW_DIR}")
    print(f"  Output   : {PROC_DIR}")
    print(f"  Spectral : {SPECTRAL_DIR}")
    print("=" * 60)

    tifs = sorted(RAW_DIR.glob("*.tif")) + sorted(RAW_DIR.glob("*.TIF"))
    if not tifs:
        print(f"\n[WARN] No GeoTIFF files found in {RAW_DIR}.")
        print("       Run Module 1 first and download exports from Google Drive.\n")
        return

    print(f"\n[INFO] Found {len(tifs)} GeoTIFF file(s).\n")
    all_water_stats = []
    for tif in tifs:
        wm_stats = process_file(tif)
        all_water_stats.append(wm_stats)

    # Aggregate all chip metadata
    all_meta = []
    for m_file in META_DIR.glob("*_meta.json"):
        with open(m_file) as f:
            all_meta.extend(json.load(f))

    summary_path = PROC_DIR / "all_chips_summary.json"
    with open(summary_path, "w") as f:
        json.dump(all_meta, f, indent=2)

    total_anomalous = sum(1 for m in all_meta if m["anomaly_pixels"] > 0)

    # Compute aggregate water coverage statistics
    total_water_px = sum(s["water_pixels"] for s in all_water_stats)
    total_all_px = sum(s["total_pixels"] for s in all_water_stats)
    avg_water_pct = (
        (total_water_px / total_all_px * 100.0) if total_all_px > 0 else 0.0
    )

    print(f"\n{'='*60}")
    print(f"  Aqua-Sentinel AI -- Preprocessing Complete")
    print(f"  {'-'*56}")
    print(f"  Total chips        : {len(all_meta)}")
    print(f"  Anomaly chips      : {total_anomalous}")
    print(f"  Water coverage     : {avg_water_pct:.1f}% "
          f"({total_water_px:,} / {total_all_px:,} px)")
    print(f"  Files processed    : {len(tifs)}")
    print(f"  Summary            : {summary_path}")
    print(f"  Water mask stats   : {SPECTRAL_DIR}")
    print(f"  Next -> Upload {TILES_DIR} to Roboflow for annotation.")
    print("=" * 60)


if __name__ == "__main__":
    main()
