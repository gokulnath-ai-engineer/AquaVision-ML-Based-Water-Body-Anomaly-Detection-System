"""
module1_gee_acquisition.py
━━━━━━━━━━━━━━━━━━━━━━━━━━
Module 1 · Remote Sensing Acquisition  —  Aqua-Sentinel AI
───────────────────────────────────────────────────────────
Connects to Google Earth Engine and acquires two complementary datasets:

  1. **Landsat 8/9 TIRS** — Surface Temperature (ST_B10 → Kelvin)
     for thermal anomaly detection.
  2. **Sentinel-2 MSI** — Multi-spectral bands (B2–B12) for water-quality
     spectral index computation (NDWI, turbidity, chlorophyll-a, etc.).

Both collections are cloud-masked, scaled, and exported as 32-bit
GeoTIFF files to Google Drive.

In Demo Mode, generates synthetic thermal data instead of downloading
from GEE — no authentication required.

Usage
-----
    python module1_gee_acquisition.py           # Real GEE (needs auth)
    python module1_gee_acquisition.py --demo    # Synthetic data (no auth)

Requirements
------------
    pip install earthengine-api
    earthengine authenticate        # one-time browser auth (production only)
"""

import sys
import argparse
from config import ROI, GEE, SENTINEL2, DEMO_MODE


# ──────────────────────────────────────────────
# Demo mode handler
# ──────────────────────────────────────────────

def run_demo_mode() -> None:
    """Generate synthetic satellite data instead of downloading from GEE."""
    print("\n[DEMO MODE] Generating synthetic Landsat thermal data...\n")
    from generate_synthetic_data import main as generate_data
    generate_data()


# ──────────────────────────────────────────────
# GEE Helpers (production mode)
# ──────────────────────────────────────────────

def apply_scale_factors(image):
    """
    Apply Landsat Collection 2 Level-2 scale factors to ST_B10.
    Output is Surface Temperature in Kelvin (float32).
    """
    import ee
    thermal = (
        image.select(GEE["thermal_band"])
             .multiply(GEE["scale_factor"])
             .add(GEE["add_offset"])
             .rename("ST_Kelvin")
    )
    return image.addBands(thermal)


def mask_clouds(image):
    """
    Mask cloud and cloud-shadow pixels using the QA_PIXEL band.
    Bits 3 (cloud shadow) and 5 (cloud) must be 0.
    """
    import ee
    qa = image.select("QA_PIXEL")
    cloud_shadow_bit = 1 << 3
    cloud_bit        = 1 << 5
    mask = (
        qa.bitwiseAnd(cloud_shadow_bit).eq(0)
          .And(qa.bitwiseAnd(cloud_bit).eq(0))
    )
    return image.updateMask(mask)


def build_roi():
    """Build an EE rectangle from config coordinates."""
    import ee
    r = ROI
    return ee.Geometry.Rectangle([
        r["lon_min"], r["lat_min"],
        r["lon_max"], r["lat_max"]
    ])


def build_collection(satellite: str, roi):
    """
    Load, filter, cloud-mask, and scale a Landsat collection.

    Parameters
    ----------
    satellite : 'L8' | 'L9'
    roi       : EE geometry
    """
    import ee
    collection_id = (
        GEE["collection_l8"] if satellite == "L8" else GEE["collection_l9"]
    )
    col = (
        ee.ImageCollection(collection_id)
          .filterBounds(roi)
          .filterDate(GEE["date_start"], GEE["date_end"])
          .filter(ee.Filter.lt("CLOUD_COVER", GEE["cloud_cover_max"]))
          .map(mask_clouds)
          .map(apply_scale_factors)
          .select("ST_Kelvin")
    )
    return col


def export_image(image, description: str, roi) -> None:
    """
    Submit an Export.image.toDrive task for a single image.
    """
    import ee
    task = ee.batch.Export.image.toDrive(
        image=image.clip(roi),
        description=description,
        folder=GEE["drive_folder"],
        fileNamePrefix=description,
        scale=GEE["export_scale_m"],
        region=roi,
        fileFormat="GeoTIFF",
        maxPixels=1e13,
        formatOptions={"cloudOptimized": True},
    )
    task.start()
    print(f"  [EXPORT STARTED] {description}  →  Google Drive/{GEE['drive_folder']}/")
    return task


# ──────────────────────────────────────────────
# Sentinel-2 MSI Helpers (production mode)
# ──────────────────────────────────────────────

def build_sentinel2_collection(roi):
    """
    Load, filter, and cloud-mask a Sentinel-2 SR Harmonized collection.

    Returns an ImageCollection with the multi-spectral bands defined
    in config.SENTINEL2['bands'].
    """
    import ee

    band_names = list(SENTINEL2["bands"].values())

    def _mask_s2_clouds(image):
        """Mask clouds using the SCL (Scene Classification Layer) band."""
        scl = image.select("SCL")
        # Keep vegetation (4), bare soil (5), water (6), snow/ice (11)
        mask = (scl.eq(4).Or(scl.eq(5)).Or(scl.eq(6)).Or(scl.eq(11)))
        return image.updateMask(mask)

    col = (
        ee.ImageCollection(SENTINEL2["collection"])
          .filterBounds(roi)
          .filterDate(SENTINEL2["date_start"], SENTINEL2["date_end"])
          .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE",
                               SENTINEL2["cloud_cover_max"]))
          .map(_mask_s2_clouds)
          .select(band_names)
    )
    return col


def export_sentinel2_image(image, description: str, roi) -> None:
    """
    Submit an Export.image.toDrive task for a Sentinel-2 image.
    """
    import ee
    task = ee.batch.Export.image.toDrive(
        image=image.clip(roi),
        description=description,
        folder=SENTINEL2["drive_folder"],
        fileNamePrefix=description,
        scale=SENTINEL2["export_scale_m"],
        region=roi,
        fileFormat="GeoTIFF",
        maxPixels=1e13,
        formatOptions={"cloudOptimized": True},
    )
    task.start()
    print(f"  [EXPORT STARTED] {description}  →  Google Drive/{SENTINEL2['drive_folder']}/")
    return task


# ──────────────────────────────────────────────
# GEE production pipeline
# ──────────────────────────────────────────────

def run_gee_pipeline() -> None:
    """Full GEE acquisition pipeline for production use."""
    import ee

    # Authenticate & initialise
    try:
        ee.Initialize()
        print("[OK] Earth Engine initialised.\n")
    except Exception:
        print("[AUTH] Triggering browser authentication...")
        ee.Authenticate()
        ee.Initialize()

    roi = build_roi()

    # ── Landsat thermal acquisition ──────────────────
    print("━" * 50)
    print("  Aqua-Sentinel AI · Landsat Thermal Acquisition")
    print("━" * 50)

    print("[INFO] Building Landsat 8 collection...")
    col_l8 = build_collection("L8", roi)
    print(f"       L8 scenes : {col_l8.size().getInfo()}")

    print("[INFO] Building Landsat 9 collection...")
    col_l9 = build_collection("L9", roi)
    print(f"       L9 scenes : {col_l9.size().getInfo()}")

    merged = col_l8.merge(col_l9).sort("system:time_start")
    total  = merged.size().getInfo()
    print(f"\n[INFO] Total Landsat scenes after merge + cloud filter : {total}\n")

    tasks = []

    if total == 0:
        print("[WARN] No Landsat scenes found. Relax date range or cloud-cover threshold.")
    else:
        # Export each scene individually
        images = merged.toList(total)
        for i in range(total):
            img  = ee.Image(images.get(i))
            date = img.date().format("YYYY-MM-dd").getInfo()
            desc = f"AquaSentinel_ST_{date}_scene{i+1:03d}"
            task = export_image(img, desc, roi)
            tasks.append(task)

        # Also export temporal mean composite
        mean_composite = merged.mean()
        mean_task = export_image(
            mean_composite,
            f"AquaSentinel_ST_MEAN_{GEE['date_start']}_{GEE['date_end']}",
            roi,
        )
        tasks.append(mean_task)

    # ── Sentinel-2 spectral acquisition ──────────────
    print()
    print("━" * 50)
    print("  Aqua-Sentinel AI · Sentinel-2 Spectral Acquisition")
    print("━" * 50)

    print("[INFO] Building Sentinel-2 MSI collection...")
    col_s2 = build_sentinel2_collection(roi)
    s2_total = col_s2.size().getInfo()
    print(f"       S2 scenes : {s2_total}\n")

    if s2_total == 0:
        print("[WARN] No Sentinel-2 scenes found. Relax date range or cloud-cover threshold.")
    else:
        s2_images = col_s2.toList(s2_total)
        for i in range(s2_total):
            img  = ee.Image(s2_images.get(i))
            date = img.date().format("YYYY-MM-dd").getInfo()
            desc = f"AquaSentinel_S2_{date}_scene{i+1:03d}"
            task = export_sentinel2_image(img, desc, roi)
            tasks.append(task)

        # Export temporal median composite for spectral analysis
        median_composite = col_s2.median()
        median_task = export_sentinel2_image(
            median_composite,
            f"AquaSentinel_S2_MEDIAN_{SENTINEL2['date_start']}_{SENTINEL2['date_end']}",
            roi,
        )
        tasks.append(median_task)

    # ── Summary ──────────────────────────────────────
    print(f"\n[DONE] {len(tasks)} export task(s) submitted to Google Earth Engine.")
    print("       Monitor progress at: https://code.earthengine.google.com/tasks")
    print(f"       Landsat thermal   → Google Drive/{GEE['drive_folder']}/")
    print(f"       Sentinel-2 MSI    → Google Drive/{SENTINEL2['drive_folder']}/")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Module 1 · GEE Thermal Data Acquisition"
    )
    parser.add_argument("--demo", action="store_true", default=DEMO_MODE,
                        help="Use synthetic data instead of GEE (default if DEMO_MODE=True)")
    parser.add_argument("--production", action="store_true",
                        help="Force production GEE mode")
    args = parser.parse_args()

    use_demo = args.demo and not args.production

    print("=" * 60)
    print("  Aqua-Sentinel AI · Module 1 · Data Acquisition")
    print(f"  Mode       : {'🧪 DEMO (Synthetic)' if use_demo else '🛰️ PRODUCTION (GEE)'}")
    print(f"  Study Area : {ROI['name']}")
    if not use_demo:
        print(f"  Landsat    : {GEE['date_start']}  →  {GEE['date_end']}")
        print(f"  Sentinel-2 : {SENTINEL2['date_start']}  →  {SENTINEL2['date_end']}")
    print("=" * 60)

    if use_demo:
        run_demo_mode()
    else:
        run_gee_pipeline()


if __name__ == "__main__":
    main()
