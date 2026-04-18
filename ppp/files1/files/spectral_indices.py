"""
spectral_indices.py -- Spectral Index Calculations for Water Quality Analysis
==============================================================================
Part of Aqua-Sentinel AI: A Hierarchical Geo-Intelligent Framework for
Real-Time Multi-Spectral Water Quality Monitoring & Forensic Anomaly Reporting

This module implements spectral index computations used to assess water quality
from Sentinel-2 MSI and Landsat satellite imagery.  Each function accepts
numpy arrays (single-band rasters) and returns numpy arrays of the same shape.

Supported Indices
-----------------
- NDWI   -- Normalized Difference Water Index (water/land discrimination)
- Chl-a  -- Chlorophyll-a proxy via band ratio & NDCI (algal bloom detection)
- Turb   -- Turbidity index from Red-band reflectance (suspended sediments)
- Oil    -- Oil Slick Index via SWIR1/NIR ratio (oil spill / chemical slick)
- Therm  -- Thermal anomaly detection from Landsat TIRS (industrial discharge)
- WQS    -- Composite Water Quality Score (0-100, 100 = pristine)

Thresholds are imported from ``config.SPECTRAL`` so that a single source of
truth governs both this module and the forensic reasoning engine.
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

from config import SPECTRAL

# ---------------------------------------------------------------------------
# Constants pulled from the central configuration
# ---------------------------------------------------------------------------
NDWI_THRESHOLD: float = SPECTRAL["ndwi_threshold"]
CHLOROPHYLL_THRESHOLD: float = SPECTRAL["chlorophyll_threshold"]
TURBIDITY_THRESHOLD: float = SPECTRAL["turbidity_threshold"]
OIL_SLICK_THRESHOLD: float = SPECTRAL["oil_slick_threshold"]
THERMAL_ANOMALY_DELTA_K: float = SPECTRAL["thermal_anomaly_delta_k"]

# Small constant to prevent division by zero in normalized-difference indices.
_EPSILON: float = 1e-10


# ===================================================================
# Helper Functions
# ===================================================================

def safe_divide(
    numerator: np.ndarray,
    denominator: np.ndarray,
    epsilon: float = _EPSILON,
) -> np.ndarray:
    """Element-wise division that avoids division-by-zero artifacts.

    Where ``|denominator| < epsilon`` the result is set to **0.0** rather than
    ``inf`` or ``nan``, keeping downstream statistics stable.

    Parameters
    ----------
    numerator : np.ndarray
        Numerator array (any shape).
    denominator : np.ndarray
        Denominator array (must be broadcastable to *numerator*).
    epsilon : float, optional
        Absolute threshold below which a denominator element is treated as
        zero.  Defaults to ``1e-10``.

    Returns
    -------
    np.ndarray
        Quotient array with the same shape as *numerator*, dtype ``float64``.
    """
    numerator = np.asarray(numerator, dtype=np.float64)
    denominator = np.asarray(denominator, dtype=np.float64)

    # Mask positions where the denominator is essentially zero.
    safe_denom = np.where(np.abs(denominator) < epsilon, epsilon, denominator)
    result = numerator / safe_denom

    # Force exact zero where denominator was degenerate to avoid misleading
    # near-zero / near-epsilon ratios.
    result[np.abs(denominator) < epsilon] = 0.0
    return result


def classify_water_quality(score: float) -> str:
    """Map a composite Water Quality Score to a human-readable label.

    The classification bins are:

    +-----------+--------------+
    | Score     | Category     |
    +===========+==============+
    | 80 -- 100 | Excellent    |
    | 60 --  79 | Good         |
    | 40 --  59 | Moderate     |
    | 20 --  39 | Poor         |
    |  0 --  19 | Critical     |
    +-----------+--------------+

    Parameters
    ----------
    score : float
        A scalar water quality score in the range ``[0, 100]``.

    Returns
    -------
    str
        One of ``"Excellent"``, ``"Good"``, ``"Moderate"``, ``"Poor"``,
        or ``"Critical"``.
    """
    if score >= 80.0:
        return "Excellent"
    if score >= 60.0:
        return "Good"
    if score >= 40.0:
        return "Moderate"
    if score >= 20.0:
        return "Poor"
    return "Critical"


# ===================================================================
# 1. NDWI -- Normalized Difference Water Index
# ===================================================================

def compute_ndwi(
    green_band: np.ndarray,
    nir_band: np.ndarray,
) -> np.ndarray:
    """Compute the Normalized Difference Water Index (NDWI).

    Formula
    -------
    .. math::

        NDWI = \\frac{Green - NIR}{Green + NIR}

    NDWI highlights open water surfaces while suppressing vegetation and soil.
    Values close to **+1** indicate water; values near **-1** indicate dry
    land or dense vegetation.

    A pixel is considered *water* when ``NDWI > config.SPECTRAL["ndwi_threshold"]``
    (default **{threshold}**).

    Parameters
    ----------
    green_band : np.ndarray
        Surface reflectance in the Green channel (Sentinel-2 B3, ~560 nm).
    nir_band : np.ndarray
        Surface reflectance in the NIR channel (Sentinel-2 B8, ~842 nm).

    Returns
    -------
    np.ndarray
        NDWI image with values in ``[-1, +1]``, dtype ``float64``.

    References
    ----------
    McFeeters, S. K. (1996). "The use of the Normalized Difference Water
    Index (NDWI) in the delineation of open water features."
    *International Journal of Remote Sensing*, 17(7), 1425-1432.
    """.format(threshold=NDWI_THRESHOLD)

    green = np.asarray(green_band, dtype=np.float64)
    nir = np.asarray(nir_band, dtype=np.float64)

    numerator = green - nir
    denominator = green + nir

    return safe_divide(numerator, denominator)


# ===================================================================
# 2. Chlorophyll-a Index (Algal Bloom Detection)
# ===================================================================

def compute_chlorophyll_index(
    nir_band: np.ndarray,
    red_band: np.ndarray,
    red_edge_band: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Compute a chlorophyll-a proxy for algal bloom detection.

    Two complementary formulations are supported:

    **Band-ratio method** (always computed)::

        Chl-a proxy = NIR / Red

    High values indicate dense chlorophyll (algal blooms / eutrophication).
    A pixel is flagged when the ratio exceeds
    ``config.SPECTRAL["chlorophyll_threshold"]`` (default **{threshold}**).

    **NDCI method** (when *red_edge_band* is supplied -- Sentinel-2 only)::

        NDCI = (RedEdge - Red) / (RedEdge + Red)

    The Normalized Difference Chlorophyll Index (NDCI) exploits the sharp
    reflectance rise at the red-edge (~705 nm) caused by chlorophyll
    absorption.  When available, NDCI is returned instead of the simple band
    ratio because it offers better sensitivity to moderate concentrations.

    Parameters
    ----------
    nir_band : np.ndarray
        Surface reflectance in the NIR channel (Sentinel-2 B8, ~842 nm).
    red_band : np.ndarray
        Surface reflectance in the Red channel (Sentinel-2 B4, ~665 nm).
    red_edge_band : np.ndarray or None, optional
        Surface reflectance in the Red-Edge channel (Sentinel-2 B5, ~705 nm).
        If provided, the NDCI formulation is used.  Defaults to ``None``.

    Returns
    -------
    np.ndarray
        Chlorophyll-a index image, dtype ``float64``.
        - Band-ratio mode: values in ``[0, +inf)``
        - NDCI mode: values in ``[-1, +1]``

    References
    ----------
    Mishra, S. & Mishra, D. R. (2012). "Normalized difference chlorophyll
    index: A novel model for remote estimation of chlorophyll-a
    concentration in turbid productive waters."
    *Remote Sensing of Environment*, 117, 394-406.
    """.format(threshold=CHLOROPHYLL_THRESHOLD)

    nir = np.asarray(nir_band, dtype=np.float64)
    red = np.asarray(red_band, dtype=np.float64)

    if red_edge_band is not None:
        # --- NDCI: preferred when Sentinel-2 Red-Edge band is available ---
        red_edge = np.asarray(red_edge_band, dtype=np.float64)
        numerator = red_edge - red
        denominator = red_edge + red
        return safe_divide(numerator, denominator)

    # --- Simple band ratio: NIR / Red ---
    return safe_divide(nir, red)


# ===================================================================
# 3. Turbidity Index
# ===================================================================

def compute_turbidity(red_band: np.ndarray) -> np.ndarray:
    """Compute a turbidity proxy from the Red-band surface reflectance.

    Formula
    -------
    Turbidity is approximated directly by the Red-band reflectance.
    Suspended sediments (silt, clay, construction runoff) increase
    back-scatter in the red portion of the visible spectrum.

    A pixel is considered *turbid* when
    ``Red > config.SPECTRAL["turbidity_threshold"]``
    (default **{threshold}**).

    Parameters
    ----------
    red_band : np.ndarray
        Surface reflectance in the Red channel (Sentinel-2 B4, ~665 nm).
        Values are expected in the range ``[0, 1]`` for Level-2A SR data.

    Returns
    -------
    np.ndarray
        Turbidity index image, dtype ``float64``.  Higher values mean
        greater turbidity / more suspended material.

    Notes
    -----
    For more sophisticated turbidity models (e.g., Dogliotti et al. 2015)
    the Red and NIR bands can be combined.  This single-band proxy is
    intentionally simple and sufficient for the Aqua-Sentinel forensic
    pipeline when combined with the other spectral indices.
    """.format(threshold=TURBIDITY_THRESHOLD)

    red = np.asarray(red_band, dtype=np.float64)
    return red


# ===================================================================
# 4. Oil Slick Index
# ===================================================================

def compute_oil_index(
    swir1_band: np.ndarray,
    nir_band: np.ndarray,
) -> np.ndarray:
    """Compute the Oil Slick Index for detecting oil spills on water.

    Formula
    -------
    .. math::

        OilIndex = \\frac{SWIR1}{NIR}

    Oil films on water suppress NIR reflectance while maintaining or
    increasing SWIR1 reflectance, producing elevated ratio values.

    A pixel is flagged as a potential oil slick when
    ``OilIndex > config.SPECTRAL["oil_slick_threshold"]``
    (default **{threshold}**).

    Parameters
    ----------
    swir1_band : np.ndarray
        Surface reflectance in the SWIR-1 channel (Sentinel-2 B11,
        ~1610 nm).
    nir_band : np.ndarray
        Surface reflectance in the NIR channel (Sentinel-2 B8, ~842 nm).

    Returns
    -------
    np.ndarray
        Oil Slick Index image, dtype ``float64``.

    References
    ----------
    Hu, C. et al. (2009). "Detection of natural oil slicks in the NW Gulf
    of Mexico using MODIS imagery."
    *Geophysical Research Letters*, 36(1).
    """.format(threshold=OIL_SLICK_THRESHOLD)

    swir1 = np.asarray(swir1_band, dtype=np.float64)
    nir = np.asarray(nir_band, dtype=np.float64)

    return safe_divide(swir1, nir)


# ===================================================================
# 5. Thermal Anomaly Detection
# ===================================================================

def compute_thermal_anomaly(
    thermal_band: np.ndarray,
    baseline_temp: Optional[float] = None,
    delta_threshold: float = THERMAL_ANOMALY_DELTA_K,
) -> Tuple[np.ndarray, np.ndarray]:
    """Detect thermal anomalies (e.g., industrial discharge) in a thermal
    band image.

    The function computes the per-pixel temperature departure from a
    *baseline* and flags every pixel whose departure exceeds
    *delta_threshold*.

    Algorithm
    ---------
    1. If *baseline_temp* is not provided, the **median** of the thermal
       band is used as the scene-wide baseline.  This is a reasonable
       default for scenes that are predominantly water.
    2. ``delta_map = thermal_band - baseline_temp``
    3. ``anomaly_mask = delta_map > delta_threshold``

    The default *delta_threshold* is drawn from
    ``config.SPECTRAL["thermal_anomaly_delta_k"]`` (default **{delta}** K).

    Parameters
    ----------
    thermal_band : np.ndarray
        Surface / brightness temperature image in **Kelvin** (e.g.,
        Landsat 8/9 ST_B10 after applying scale factor and offset).
    baseline_temp : float or None, optional
        Expected background water temperature in Kelvin.  When ``None``
        the scene median is used.
    delta_threshold : float, optional
        Minimum temperature exceedance (K) to flag as anomalous.
        Defaults to ``config.SPECTRAL["thermal_anomaly_delta_k"]``.

    Returns
    -------
    anomaly_mask : np.ndarray
        Boolean array -- ``True`` where the pixel temperature exceeds the
        baseline by more than *delta_threshold*.
    delta_map : np.ndarray
        Continuous temperature-departure image (K), dtype ``float64``.
        Positive values indicate warmer-than-baseline pixels.
    """.format(delta=THERMAL_ANOMALY_DELTA_K)

    thermal = np.asarray(thermal_band, dtype=np.float64)

    if baseline_temp is None:
        # Use the scene median as the background temperature estimate.
        # np.nanmedian is used to gracefully handle any NaN / nodata pixels.
        baseline_temp = float(np.nanmedian(thermal))

    delta_map: np.ndarray = thermal - baseline_temp
    anomaly_mask: np.ndarray = delta_map > delta_threshold

    return anomaly_mask, delta_map


# ===================================================================
# 6. Composite Water Quality Score
# ===================================================================

def compute_water_quality_score(
    ndwi: np.ndarray,
    chlorophyll: np.ndarray,
    turbidity: np.ndarray,
    oil_index: np.ndarray,
    thermal_delta: np.ndarray,
) -> np.ndarray:
    """Compute a single composite Water Quality Score (WQS).

    The score maps multiple spectral indices onto a **0 -- 100** scale where
    **100 = pristine** and **0 = severely degraded**.

    Scoring Method
    --------------
    Each index is converted to a *penalty* in ``[0, 1]`` that reflects how
    far the measured value departs from the "clean water" expectation.  The
    penalties are combined with equal weighting and subtracted from 100.

    +-------------------+-------------------------------+------------------+
    | Sub-index         | Penalty rule                  | Weight           |
    +===================+===============================+==================+
    | Chlorophyll-a     | chl / chl_threshold, cap at 1 | 0.25             |
    | Turbidity         | turb / turb_threshold, cap 1  | 0.25             |
    | Oil Slick Index   | oil / oil_threshold, cap at 1 | 0.25             |
    | Thermal departure | delta / delta_thresh, cap 1   | 0.25             |
    +-------------------+-------------------------------+------------------+

    The NDWI input is used as a **water mask**: pixels where
    ``NDWI < ndwi_threshold`` are assigned a score of ``NaN`` because
    they are likely land and a water-quality metric is meaningless there.

    Parameters
    ----------
    ndwi : np.ndarray
        NDWI image (output of :func:`compute_ndwi`).
    chlorophyll : np.ndarray
        Chlorophyll-a index (output of :func:`compute_chlorophyll_index`).
    turbidity : np.ndarray
        Turbidity index (output of :func:`compute_turbidity`).
    oil_index : np.ndarray
        Oil Slick Index (output of :func:`compute_oil_index`).
    thermal_delta : np.ndarray
        Temperature departure map in Kelvin (the second element returned
        by :func:`compute_thermal_anomaly`).

    Returns
    -------
    np.ndarray
        Water Quality Score image, values in ``[0, 100]`` for water pixels
        and ``NaN`` for non-water pixels, dtype ``float64``.
    """
    ndwi = np.asarray(ndwi, dtype=np.float64)
    chlorophyll = np.asarray(chlorophyll, dtype=np.float64)
    turbidity = np.asarray(turbidity, dtype=np.float64)
    oil_index = np.asarray(oil_index, dtype=np.float64)
    thermal_delta = np.asarray(thermal_delta, dtype=np.float64)

    # --- Sub-index penalties (each in [0, 1]) ---
    penalty_chl = np.clip(chlorophyll / CHLOROPHYLL_THRESHOLD, 0.0, 1.0)
    penalty_turb = np.clip(turbidity / TURBIDITY_THRESHOLD, 0.0, 1.0)
    penalty_oil = np.clip(oil_index / OIL_SLICK_THRESHOLD, 0.0, 1.0)
    penalty_thermal = np.clip(thermal_delta / THERMAL_ANOMALY_DELTA_K, 0.0, 1.0)

    # Equal-weight aggregation
    total_penalty = 0.25 * (penalty_chl + penalty_turb + penalty_oil + penalty_thermal)

    # Convert penalty -> quality score
    score = (1.0 - total_penalty) * 100.0

    # Clamp to [0, 100] for safety (floating-point edge cases)
    score = np.clip(score, 0.0, 100.0)

    # Mask non-water pixels with NaN
    water_mask = ndwi > NDWI_THRESHOLD
    score[~water_mask] = np.nan

    return score
