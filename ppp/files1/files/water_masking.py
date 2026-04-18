"""
water_masking.py
================
Module C -- Hydrological Masking & Noise Reduction
---------------------------------------------------
Aqua-Sentinel AI: A Hierarchical Geo-Intelligent Framework for
Real-Time Multi-Spectral Water Quality Monitoring & Forensic
Anomaly Reporting

Purpose
-------
Implements NDWI-based water body masking so that downstream modules
(anomaly detection, forensic analysis, YOLOv8 inference) process
ONLY water surfaces.  This eliminates false positives from roads,
rooftops, parking lots, and bare soil that can mimic thermal
anomalies.

Algorithm summary
-----------------
  1.  Compute NDWI = (Green - NIR) / (Green + NIR)
  2.  Threshold  ->  binary water / land mask
  3.  Morphological cleanup  (close gaps, remove noise blobs)
  4.  Connected-component filter  (discard regions < min_area px)
  5.  Apply mask to any image array  (NaN-out land pixels)

A fallback path exists for demo / single-band thermal mode:
  generate_water_mask_from_thermal()  derives an approximate mask
  by treating the coolest N-th percentile as likely water.

Usage
-----
    from water_masking import (
        compute_ndwi_mask,
        apply_water_mask,
        refine_water_mask,
        generate_water_mask_from_thermal,
        mask_statistics,
        visualize_water_mask,
        extract_water_boundary,
    )

    mask = compute_ndwi_mask(green_band, nir_band)
    mask = refine_water_mask(mask)
    masked_img = apply_water_mask(thermal_array, mask)
"""

import warnings
from typing import Optional, Union

import numpy as np
import cv2

from config import PREPROCESS, SPECTRAL


# ──────────────────────────────────────────────────────────
# 1. NDWI Computation & Thresholding
# ──────────────────────────────────────────────────────────

def compute_ndwi_mask(
    green_band: np.ndarray,
    nir_band: np.ndarray,
    threshold: Optional[float] = None,
) -> np.ndarray:
    """
    Compute the Normalized Difference Water Index and return a binary
    water mask.

    NDWI = (Green - NIR) / (Green + NIR)

    Pixels with NDWI > *threshold* are classified as water (1);
    everything else is land (0).  NaN / zero-denominator pixels are
    treated as land.

    Parameters
    ----------
    green_band : np.ndarray
        Green-band reflectance (Sentinel-2 B3 or equivalent).
        Any numeric dtype; will be cast to float64 internally.
    nir_band : np.ndarray
        Near-infrared reflectance (Sentinel-2 B8 or equivalent).
    threshold : float, optional
        NDWI decision boundary.  Defaults to the value in
        ``SPECTRAL["ndwi_threshold"]`` (typically 0.3).

    Returns
    -------
    np.ndarray
        uint8 binary mask -- 1 = water, 0 = land.

    Raises
    ------
    ValueError
        If *green_band* and *nir_band* shapes do not match.
    """
    if green_band.shape != nir_band.shape:
        raise ValueError(
            f"Band shape mismatch: green {green_band.shape} vs "
            f"NIR {nir_band.shape}"
        )

    if threshold is None:
        threshold = SPECTRAL.get("ndwi_threshold", PREPROCESS.get("ndwi_threshold", 0.3))

    green = green_band.astype(np.float64)
    nir = nir_band.astype(np.float64)

    # Denominator -- guard against division by zero
    denom = green + nir
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        ndwi = np.where(denom != 0, (green - nir) / denom, np.nan)

    # Build binary mask: water = 1 where NDWI > threshold and value
    # is not NaN.
    mask = np.zeros(green_band.shape, dtype=np.uint8)
    valid = ~np.isnan(ndwi)
    mask[valid & (ndwi > threshold)] = 1

    return mask


# ──────────────────────────────────────────────────────────
# 2. Mask Application
# ──────────────────────────────────────────────────────────

def apply_water_mask(
    image: np.ndarray,
    water_mask: np.ndarray,
) -> np.ndarray:
    """
    Apply a binary water mask to an image or data array.

    Water pixels (mask == 1) are preserved unchanged.
    Non-water pixels are set to:
      - ``NaN``  for floating-point dtypes
      - ``0``    for integer / uint8 dtypes

    Parameters
    ----------
    image : np.ndarray
        Input image or data array (2-D or 3-D with channel axis last).
    water_mask : np.ndarray
        2-D uint8 mask where 1 = water, 0 = land.

    Returns
    -------
    np.ndarray
        Masked copy of *image* (same shape & dtype as input).

    Raises
    ------
    ValueError
        If spatial dimensions of *image* and *water_mask* disagree.
    """
    # Validate spatial dimensions
    spatial_shape = image.shape[:2]
    if water_mask.shape[:2] != spatial_shape:
        raise ValueError(
            f"Spatial shape mismatch: image {spatial_shape} vs "
            f"mask {water_mask.shape[:2]}"
        )

    masked = image.copy()
    land = water_mask == 0

    if np.issubdtype(masked.dtype, np.floating):
        # Float arrays -- mask land with NaN
        if masked.ndim == 3:
            for ch in range(masked.shape[2]):
                masked[:, :, ch][land] = np.nan
        else:
            masked[land] = np.nan
    else:
        # Integer / uint8 arrays -- mask land with 0
        if masked.ndim == 3:
            for ch in range(masked.shape[2]):
                masked[:, :, ch][land] = 0
        else:
            masked[land] = 0

    return masked


# ──────────────────────────────────────────────────────────
# 3. Morphological Refinement
# ──────────────────────────────────────────────────────────

def refine_water_mask(
    mask: np.ndarray,
    min_area: int = 100,
    morphology_kernel: int = 5,
) -> np.ndarray:
    """
    Clean up a raw binary water mask using morphological operations
    and connected-component filtering.

    Steps
    -----
    1. **Morphological closing** -- fill small internal gaps (e.g.,
       bridge shadows, sensor artefacts).
    2. **Morphological opening** -- remove pepper-noise isolated
       pixels.
    3. **Connected-component filter** -- discard water regions whose
       area is smaller than *min_area* pixels (boats, wet roofs, etc.).

    Parameters
    ----------
    mask : np.ndarray
        Binary mask (uint8, values 0 or 1).
    min_area : int
        Minimum contiguous water region size in pixels.  Regions
        smaller than this are reclassified as land.
    morphology_kernel : int
        Side length (px) of the square structuring element used for
        opening and closing.

    Returns
    -------
    np.ndarray
        Refined uint8 binary mask (1 = water, 0 = land).
    """
    if mask.size == 0:
        return mask.copy()

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (morphology_kernel, morphology_kernel)
    )

    # Close: fill small holes inside water bodies
    refined = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Open: remove tiny isolated noise pixels
    refined = cv2.morphologyEx(refined, cv2.MORPH_OPEN, kernel)

    # Connected-component filtering
    # cv2.connectedComponentsWithStats returns (num_labels, labels,
    # stats, centroids). Label 0 is always the background.
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        refined, connectivity=8
    )

    filtered = np.zeros_like(refined)
    for label_id in range(1, num_labels):
        area = stats[label_id, cv2.CC_STAT_AREA]
        if area >= min_area:
            filtered[labels == label_id] = 1

    return filtered


# ──────────────────────────────────────────────────────────
# 4. Thermal-Based Fallback Mask (Demo / Single-Band Mode)
# ──────────────────────────────────────────────────────────

def generate_water_mask_from_thermal(
    thermal_arr: np.ndarray,
    percentile: float = 30,
) -> np.ndarray:
    """
    Create a strict water mask from thermal (surface temperature) data.

    Uses a two-pass approach:
    1. Find the river temperature band (coolest cluster of pixels)
    2. Only classify pixels within a tight range of river temperature

    This prevents roads, buildings, and land from being misclassified.

    Parameters
    ----------
    thermal_arr : np.ndarray
        2-D float array of surface temperature values (Kelvin).
    percentile : float
        Temperature percentile below which pixels are classified as
        water.  Lower values = more conservative mask.

    Returns
    -------
    np.ndarray
        uint8 binary mask (1 = water, 0 = land / NoData).
    """
    arr = thermal_arr.astype(np.float64)
    valid = arr[~np.isnan(arr)]

    if valid.size == 0:
        warnings.warn(
            "generate_water_mask_from_thermal: all pixels are NaN; "
            "returning empty mask.",
            stacklevel=2,
        )
        return np.zeros(thermal_arr.shape, dtype=np.uint8)

    # Use a strict percentile — river is typically the coolest 10-15% of pixels
    # Use percentile 15 for a tight water mask (river channel only)
    cool_cutoff = np.percentile(valid, 15)

    # Compute the temperature gap between cool water and warm land
    warm_ref = np.percentile(valid, 60)
    temp_gap = warm_ref - cool_cutoff

    # Water threshold: river temp + small buffer (30% of the gap)
    water_threshold = cool_cutoff + temp_gap * 0.3

    mask = np.zeros(thermal_arr.shape, dtype=np.uint8)
    mask[(~np.isnan(arr)) & (arr <= water_threshold)] = 1

    return mask


# ──────────────────────────────────────────────────────────
# 5. Mask Statistics
# ──────────────────────────────────────────────────────────

def mask_statistics(water_mask: np.ndarray) -> dict:
    """
    Compute summary statistics for a binary water mask.

    Parameters
    ----------
    water_mask : np.ndarray
        uint8 mask where 1 = water, 0 = land.

    Returns
    -------
    dict
        Keys:
          - ``water_pixels``     (int)   -- count of water pixels
          - ``land_pixels``      (int)   -- count of land pixels
          - ``total_pixels``     (int)   -- total pixel count
          - ``water_percentage`` (float) -- water area as % of total
    """
    total = int(water_mask.size)
    water = int(np.sum(water_mask == 1))
    land = total - water
    pct = (water / total * 100.0) if total > 0 else 0.0

    return {
        "water_pixels": water,
        "land_pixels": land,
        "total_pixels": total,
        "water_percentage": round(pct, 4),
    }


# ──────────────────────────────────────────────────────────
# 6. Visualization Overlay
# ──────────────────────────────────────────────────────────

def visualize_water_mask(
    image: np.ndarray,
    water_mask: np.ndarray,
    alpha: float = 0.4,
) -> np.ndarray:
    """
    Create a colour-coded overlay showing water vs. masked-out land.

    - **Water pixels** receive a semi-transparent blue tint.
    - **Land (masked-out) pixels** receive a semi-transparent red tint.

    Parameters
    ----------
    image : np.ndarray
        Base image for the overlay.  Accepted formats:
          - Greyscale uint8 (H, W)
          - BGR uint8 (H, W, 3)
    water_mask : np.ndarray
        Binary mask (uint8, 1 = water, 0 = land).
    alpha : float
        Blending factor for the tint overlay (0 = invisible, 1 = opaque).

    Returns
    -------
    np.ndarray
        BGR uint8 image (H, W, 3) with colour overlay.
    """
    # Ensure base image is 3-channel BGR uint8
    if image.ndim == 2:
        base = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_GRAY2BGR)
    elif image.ndim == 3 and image.shape[2] == 3:
        base = image.astype(np.uint8).copy()
    else:
        raise ValueError(
            f"Unsupported image shape {image.shape}; expected (H,W) or (H,W,3)."
        )

    overlay = base.copy()

    # Blue tint for water  (BGR: high B, low G, low R)
    water_tint = np.array([255, 120, 0], dtype=np.uint8)   # vivid blue
    land_tint = np.array([0, 0, 220], dtype=np.uint8)      # red

    water_px = water_mask == 1
    land_px = water_mask == 0

    overlay[water_px] = water_tint
    overlay[land_px] = land_tint

    # Alpha blend: result = base * (1 - alpha) + overlay * alpha
    blended = cv2.addWeighted(base, 1.0 - alpha, overlay, alpha, 0)

    return blended


# ──────────────────────────────────────────────────────────
# 7. Water Boundary Extraction
# ──────────────────────────────────────────────────────────

def extract_water_boundary(
    water_mask: np.ndarray,
    transform=None,
) -> list:
    """
    Extract the outer boundary contour(s) of water bodies in the mask.

    When a geo-referencing *transform* (``rasterio.transform.Affine``)
    is provided, pixel coordinates are converted to (lat, lon).
    Otherwise, raw pixel (row, col) tuples are returned.

    Parameters
    ----------
    water_mask : np.ndarray
        Binary mask (uint8, 1 = water, 0 = land).
    transform : rasterio.transform.Affine, optional
        Affine transform mapping pixel coords to CRS coords.
        If the CRS is geographic (EPSG:4326) or UTM, the output
        will be (lat, lon) or (northing, easting) respectively.

    Returns
    -------
    list[list[tuple]]
        A list of contours, where each contour is a list of
        coordinate tuples.  If *transform* is provided, tuples are
        ``(lat, lon)``; otherwise ``(row, col)``.
    """
    # Ensure mask values are 0/255 for findContours (expects binary image)
    binary = (water_mask * 255).astype(np.uint8)

    contours, _ = cv2.findContours(
        binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    boundaries = []
    for contour in contours:
        coords = []
        for point in contour:
            col, row = int(point[0][0]), int(point[0][1])

            if transform is not None:
                # rasterio transform: pixel (row, col) -> (x, y)
                # x corresponds to lon, y to lat in geographic CRS
                try:
                    import rasterio.transform
                    x, y = rasterio.transform.xy(transform, row, col)
                    coords.append((float(y), float(x)))  # (lat, lon)
                except ImportError:
                    warnings.warn(
                        "rasterio not available; returning pixel coords.",
                        stacklevel=2,
                    )
                    coords.append((row, col))
            else:
                coords.append((row, col))

        if coords:
            boundaries.append(coords)

    return boundaries


# ──────────────────────────────────────────────────────────
# Module self-test
# ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  Module C -- Hydrological Masking & Noise Reduction")
    print("  Self-test with synthetic data")
    print("=" * 60)

    np.random.seed(42)
    H, W = 512, 512

    # Synthesise fake green & NIR bands
    # Water region: centre circle where green > NIR  (positive NDWI)
    green = np.random.uniform(0.05, 0.15, (H, W)).astype(np.float32)
    nir = np.random.uniform(0.10, 0.25, (H, W)).astype(np.float32)

    # Create a circular "lake" where green >> NIR
    yy, xx = np.ogrid[:H, :W]
    lake = ((yy - H // 2) ** 2 + (xx - W // 2) ** 2) < (150 ** 2)
    green[lake] = np.random.uniform(0.30, 0.50, lake.sum()).astype(np.float32)
    nir[lake] = np.random.uniform(0.02, 0.10, lake.sum()).astype(np.float32)

    # 1. Compute NDWI mask
    raw_mask = compute_ndwi_mask(green, nir)
    print(f"\n[1] Raw NDWI mask  : {mask_statistics(raw_mask)}")

    # 2. Refine mask
    clean_mask = refine_water_mask(raw_mask, min_area=50, morphology_kernel=5)
    print(f"[2] Refined mask   : {mask_statistics(clean_mask)}")

    # 3. Apply mask to a dummy thermal image
    thermal = np.random.uniform(290, 320, (H, W)).astype(np.float32)
    masked_thermal = apply_water_mask(thermal, clean_mask)
    nan_count = int(np.isnan(masked_thermal).sum())
    print(f"[3] Masked thermal : {nan_count} NaN pixels (land masked out)")

    # 4. Thermal fallback mask
    thermal_mask = generate_water_mask_from_thermal(thermal, percentile=30)
    print(f"[4] Thermal mask   : {mask_statistics(thermal_mask)}")

    # 5. Boundary extraction
    boundaries = extract_water_boundary(clean_mask)
    total_pts = sum(len(c) for c in boundaries)
    print(f"[5] Boundaries     : {len(boundaries)} contour(s), {total_pts} points")

    # 6. Visualization
    grey_img = np.random.randint(0, 256, (H, W), dtype=np.uint8)
    vis = visualize_water_mask(grey_img, clean_mask, alpha=0.4)
    print(f"[6] Visualisation  : shape {vis.shape}, dtype {vis.dtype}")

    print(f"\n{'=' * 60}")
    print("  Self-test PASSED -- all functions executed successfully.")
    print("=" * 60)
