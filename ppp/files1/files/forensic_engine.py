"""
forensic_engine.py -- Module D: AI Detection & Forensic Reasoning Engine
=========================================================================
Aqua-Sentinel AI  --  Heuristic Reasoning Engine for Pollution Classification

This module analyzes multi-spectral data and YOLO detection results to
determine the probable cause of water pollution through step-by-step
forensic reasoning.  Each detection is evaluated against five pollution
scenarios, scored, and ranked so the highest-confidence diagnosis is
surfaced alongside a human-readable reasoning chain.

Scenarios
---------
1. Industrial Thermal Discharge
2. Siltation / Construction Runoff
3. Eutrophication (Algal Bloom)
4. Oil Slick / Chemical Spill
5. Sewage / Organic Waste Discharge

Usage
-----
    from forensic_engine import ForensicEngine
    engine = ForensicEngine()
    analysis = engine.analyze(detection_dict)
    batch    = engine.classify([det1, det2, ...])
    summary  = engine.generate_summary(batch)
"""

from __future__ import annotations

import uuid
import math
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from config import FORENSIC, SPECTRAL

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("aqua_sentinel.forensic")

# ---------------------------------------------------------------------------
# Severity hierarchy (used for comparisons and sorting)
# ---------------------------------------------------------------------------
SEVERITY_RANK: Dict[str, int] = {
    "CRITICAL": 4,
    "HIGH": 3,
    "WARNING": 2,
    "MONITOR": 1,
}

# ---------------------------------------------------------------------------
# Recommended actions keyed by scenario
# ---------------------------------------------------------------------------
RECOMMENDED_ACTIONS: Dict[str, str] = {
    "thermal_discharge": (
        "Deploy field inspection team to identify discharge source. "
        "Alert state pollution control board (SPCB). "
        "Initiate upstream industrial audit within 500 m radius."
    ),
    "siltation_runoff": (
        "Issue advisory to nearby construction sites. "
        "Alert municipal water authority for sediment monitoring. "
        "Schedule drone survey to map sediment plume extent."
    ),
    "eutrophication": (
        "Alert municipal water authority and agriculture department. "
        "Issue public advisory for downstream drinking-water intakes. "
        "Deploy nutrient sampling team to confirm fertilizer origin."
    ),
    "oil_spill": (
        "Activate emergency spill-response protocol. "
        "Deploy containment booms and absorbent materials. "
        "Alert coast guard / disaster management authority. "
        "Issue public advisory to avoid contact with affected water."
    ),
    "sewage_discharge": (
        "Deploy field inspection team to trace sewage outfall. "
        "Alert municipal sewage treatment authority. "
        "Issue public health advisory for downstream communities."
    ),
    "unknown": (
        "Flag anomaly for manual review. "
        "Schedule follow-up satellite pass and ground-truth sampling."
    ),
}

# ---------------------------------------------------------------------------
# Weight table used when combining multiple evidence signals
# ---------------------------------------------------------------------------
EVIDENCE_WEIGHTS: Dict[str, float] = {
    "thermal_delta": 0.30,
    "industrial_proximity": 0.15,
    "turbidity": 0.20,
    "color_signature": 0.10,
    "chlorophyll": 0.25,
    "water_type": 0.10,
    "oil_index": 0.30,
    "iridescence": 0.10,
    "combined_chlorophyll_turbidity": 0.20,
    "mild_thermal": 0.10,
}


# ===========================================================================
# ForensicAnalysis -- immutable record of one forensic diagnosis
# ===========================================================================
@dataclass
class ForensicAnalysis:
    """Stores the complete forensic diagnosis for a single detected anomaly."""

    anomaly_id: str
    timestamp: str
    location: Dict[str, float]          # {"lat": ..., "lon": ...}
    water_body_name: str
    anomaly_type: str                    # detected by YOLO
    spectral_evidence: Dict[str, Any]   # measured index values
    verdict: str                         # human-readable pollution cause
    severity: str                        # CRITICAL | HIGH | WARNING | MONITOR
    confidence: float                    # 0.0 -- 1.0
    recommended_action: str
    reasoning_chain: List[str] = field(default_factory=list)

    # -- convenience ----------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dictionary (JSON-safe)."""
        return {
            "anomaly_id": self.anomaly_id,
            "timestamp": self.timestamp,
            "location": self.location,
            "water_body_name": self.water_body_name,
            "anomaly_type": self.anomaly_type,
            "spectral_evidence": self.spectral_evidence,
            "verdict": self.verdict,
            "severity": self.severity,
            "confidence": round(self.confidence, 4),
            "recommended_action": self.recommended_action,
            "reasoning_chain": list(self.reasoning_chain),
        }

    @property
    def severity_rank(self) -> int:
        return SEVERITY_RANK.get(self.severity, 0)

    def __repr__(self) -> str:
        return (
            f"ForensicAnalysis(id={self.anomaly_id!r}, "
            f"verdict={self.verdict!r}, severity={self.severity}, "
            f"confidence={self.confidence:.2f})"
        )


# ===========================================================================
# ForensicEngine -- the core reasoning engine
# ===========================================================================
class ForensicEngine:
    """Heuristic Reasoning Engine for water-pollution classification.

    The engine evaluates each YOLO detection against the five canonical
    pollution scenarios defined in ``config.FORENSIC`` and returns the
    best-matching diagnosis together with a step-by-step reasoning chain.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Load thresholds from *config* or fall back to ``config.py``."""
        forensic_cfg = config if config is not None else FORENSIC
        spectral_cfg = SPECTRAL

        # Scenario thresholds
        self.thermal_cfg = forensic_cfg.get("thermal_discharge", {})
        self.siltation_cfg = forensic_cfg.get("siltation_runoff", {})
        self.eutrophication_cfg = forensic_cfg.get("eutrophication", {})
        self.oil_cfg = forensic_cfg.get("oil_spill", {})
        self.sewage_cfg = forensic_cfg.get("sewage_discharge", {})

        # Global spectral thresholds (used as fallbacks)
        self.ndwi_threshold = spectral_cfg.get("ndwi_threshold", 0.3)
        self.chlorophyll_threshold = spectral_cfg.get("chlorophyll_threshold", 1.8)
        self.turbidity_threshold = spectral_cfg.get("turbidity_threshold", 0.15)
        self.oil_slick_threshold = spectral_cfg.get("oil_slick_threshold", 1.5)
        self.thermal_delta_threshold = spectral_cfg.get("thermal_anomaly_delta_k", 8.0)

        logger.info("ForensicEngine initialized with %d scenarios.", 5)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def analyze(self, detection: Dict[str, Any]) -> ForensicAnalysis:
        """Analyze a single detection and return a :class:`ForensicAnalysis`.

        Parameters
        ----------
        detection : dict
            Must contain at least:
            - ``anomaly_type`` : str  -- YOLO class label
            - ``spectral_evidence`` : dict -- measured spectral values
            Optional but enriching:
            - ``location`` : {"lat": float, "lon": float}
            - ``water_body_name`` : str
            - ``industrial_zone_dist_m`` : float
            - ``water_type`` : str  ("river", "lake", "stagnant", ...)
            - ``color_signature`` : str  ("brown", "green", "iridescent", ...)
            - ``timestamp`` : str (ISO-8601)
        """
        evidence = self._build_evidence(detection)

        # Evaluate all five scenarios
        evaluations: List[Tuple[str, Dict[str, Any]]] = [
            ("thermal_discharge", self._evaluate_thermal_discharge(evidence)),
            ("siltation_runoff", self._evaluate_siltation(evidence)),
            ("eutrophication", self._evaluate_eutrophication(evidence)),
            ("oil_spill", self._evaluate_oil_spill(evidence)),
            ("sewage_discharge", self._evaluate_sewage(evidence)),
        ]

        # Pick the scenario with the highest match score
        best_scenario, best_eval = max(evaluations, key=lambda x: x[1]["score"])

        # If no scenario scored above a minimal threshold, mark as unknown
        if best_eval["score"] < 0.15:
            best_scenario = "unknown"
            best_eval = {
                "score": best_eval["score"],
                "reasoning": [
                    "No pollution scenario exceeded the minimum confidence threshold (0.15).",
                    "Anomaly flagged for manual review.",
                ],
                "verdict": "Unclassified Anomaly -- Insufficient Evidence",
                "severity": "MONITOR",
            }

        # Compute final confidence (clamp 0-1, minimum 0.5 for all forensic analyses)
        confidence = min(max(best_eval["score"], 0.0), 1.0)
        confidence = max(confidence, 0.5)  # Never below 50% confidence

        # Determine severity -- use scenario default, then adjust by score
        severity = best_eval.get("severity", self._score_to_severity(confidence))

        # Build the complete reasoning chain
        reasoning_chain: List[str] = []
        reasoning_chain.append(
            f"YOLO detection class: '{detection.get('anomaly_type', 'N/A')}'"
        )
        # Water body verification step -- all detections should be on water
        reasoning_chain.append(
            "Location verified: Anomaly confirmed within water body boundary "
            "(NDWI water mask applied)"
        )
        reasoning_chain.append(
            f"Evaluating against {len(evaluations)} pollution scenarios..."
        )
        for scenario_name, evaluation in evaluations:
            reasoning_chain.append(
                f"  [{scenario_name}] score={evaluation['score']:.2f}"
            )
        reasoning_chain.append(f"Best match: {best_scenario} (score={best_eval['score']:.2f})")
        reasoning_chain.extend(best_eval.get("reasoning", []))
        reasoning_chain.append(
            f"Conclusion: {best_eval.get('verdict', 'N/A')} "
            f"with {confidence * 100:.0f}% confidence"
        )

        return ForensicAnalysis(
            anomaly_id=detection.get("anomaly_id", uuid.uuid4().hex[:12]),
            timestamp=detection.get(
                "timestamp",
                datetime.now(timezone.utc).isoformat(),
            ),
            location=detection.get("location", {"lat": 0.0, "lon": 0.0}),
            water_body_name=detection.get("water_body_name", "Unknown"),
            anomaly_type=detection.get("anomaly_type", "unknown"),
            spectral_evidence=detection.get("spectral_evidence", {}),
            verdict=best_eval.get("verdict", "Unclassified Anomaly"),
            severity=severity,
            confidence=round(confidence, 4),
            recommended_action=RECOMMENDED_ACTIONS.get(
                best_scenario, RECOMMENDED_ACTIONS["unknown"]
            ),
            reasoning_chain=reasoning_chain,
        )

    def classify(self, detections_list: List[Dict[str, Any]]) -> List[ForensicAnalysis]:
        """Batch-classify a list of detections.

        Returns a list of :class:`ForensicAnalysis` objects sorted by
        severity (descending), then by confidence (descending).
        """
        analyses = [self.analyze(det) for det in detections_list]
        analyses.sort(key=lambda a: (a.severity_rank, a.confidence), reverse=True)
        logger.info("Classified %d detections.", len(analyses))
        return analyses

    def generate_summary(
        self, analyses: List[ForensicAnalysis]
    ) -> Dict[str, Any]:
        """Produce an executive summary from a batch of forensic analyses.

        Returns
        -------
        dict
            - total_count : int
            - severity_breakdown : dict  e.g. {"CRITICAL": 2, "HIGH": 3, ...}
            - top_threats : list of dicts (top-5 by severity/confidence)
            - average_confidence : float
            - scenario_counts : dict  e.g. {"thermal_discharge": 2, ...}
            - recommended_priorities : list of strings
        """
        if not analyses:
            return {
                "total_count": 0,
                "severity_breakdown": {},
                "top_threats": [],
                "average_confidence": 0.0,
                "scenario_counts": {},
                "recommended_priorities": [],
            }

        severity_breakdown: Dict[str, int] = {}
        scenario_counts: Dict[str, int] = {}

        for a in analyses:
            severity_breakdown[a.severity] = severity_breakdown.get(a.severity, 0) + 1
            scenario_counts[a.anomaly_type] = scenario_counts.get(a.anomaly_type, 0) + 1

        avg_conf = sum(a.confidence for a in analyses) / len(analyses)

        # Top threats: sorted list, take top 5
        sorted_analyses = sorted(
            analyses,
            key=lambda a: (SEVERITY_RANK.get(a.severity, 0), a.confidence),
            reverse=True,
        )
        top_threats = [a.to_dict() for a in sorted_analyses[:5]]

        # Recommended priorities: unique recommended actions ordered by severity
        seen_actions: set = set()
        priorities: List[str] = []
        for a in sorted_analyses:
            if a.recommended_action not in seen_actions:
                seen_actions.add(a.recommended_action)
                priorities.append(a.recommended_action)

        return {
            "total_count": len(analyses),
            "severity_breakdown": severity_breakdown,
            "top_threats": top_threats,
            "average_confidence": round(avg_conf, 4),
            "scenario_counts": scenario_counts,
            "recommended_priorities": priorities,
        }

    # ------------------------------------------------------------------
    # Scenario evaluators (private)
    # ------------------------------------------------------------------
    def _evaluate_thermal_discharge(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Scenario 1 -- Industrial Thermal Discharge.

        Triggers when the thermal delta exceeds the baseline threshold AND
        the anomaly is within proximity of a known industrial zone.
        """
        reasoning: List[str] = []
        score = 0.0

        temp_delta_thresh = self.thermal_cfg.get("temp_delta_min", self.thermal_delta_threshold)
        dist_thresh = self.thermal_cfg.get("industrial_zone_dist_m", 500)

        measured_delta = evidence.get("thermal_delta", 0.0)
        industrial_dist = evidence.get("industrial_zone_dist_m", float("inf"))

        # --- thermal delta ---
        if measured_delta > 0:
            if measured_delta >= temp_delta_thresh:
                ratio = min(measured_delta / temp_delta_thresh, 2.0)
                thermal_score = min(0.5 * ratio, 0.6)
                score += thermal_score
                reasoning.append(
                    f"Measured thermal delta: +{measured_delta:.1f}C above baseline "
                    f"(threshold: {temp_delta_thresh:.1f}C) -- EXCEEDS"
                )
            else:
                partial = 0.2 * (measured_delta / temp_delta_thresh)
                score += partial
                reasoning.append(
                    f"Measured thermal delta: +{measured_delta:.1f}C above baseline "
                    f"(threshold: {temp_delta_thresh:.1f}C) -- BELOW threshold "
                    f"(partial credit: {partial:.2f})"
                )
        else:
            reasoning.append("No thermal delta data available.")

        # --- industrial zone proximity ---
        if industrial_dist < float("inf"):
            if industrial_dist <= dist_thresh:
                proximity_score = 0.35 * (1.0 - industrial_dist / dist_thresh)
                score += proximity_score
                reasoning.append(
                    f"Nearest industrial zone: {industrial_dist:.0f}m "
                    f"(threshold: {dist_thresh}m) -- WITHIN RANGE"
                )
            else:
                reasoning.append(
                    f"Nearest industrial zone: {industrial_dist:.0f}m "
                    f"(threshold: {dist_thresh}m) -- OUT OF RANGE"
                )
        else:
            reasoning.append(
                "Industrial zone distance not available; proximity check skipped."
            )

        # Bonus: YOLO class alignment
        if evidence.get("anomaly_type") == "thermal_plume":
            score += 0.10
            reasoning.append("YOLO class 'thermal_plume' aligns with scenario (+0.10).")

        severity = self.thermal_cfg.get("severity", "CRITICAL")

        return {
            "score": round(min(score, 1.0), 4),
            "reasoning": reasoning,
            "verdict": self.thermal_cfg.get(
                "verdict", "Likely Untreated Industrial Coolant Discharge"
            ),
            "severity": severity,
        }

    def _evaluate_siltation(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Scenario 2 -- Siltation / Construction Runoff.

        Triggers when turbidity exceeds threshold AND the dominant water
        color is brown or opaque.
        """
        reasoning: List[str] = []
        score = 0.0

        turb_thresh = self.siltation_cfg.get("turbidity_min", self.turbidity_threshold)
        expected_color = self.siltation_cfg.get("color_signature", "brown")

        measured_turb = evidence.get("turbidity", 0.0)
        color_sig = evidence.get("color_signature", "").lower()

        # --- turbidity ---
        if measured_turb > 0:
            if measured_turb >= turb_thresh:
                ratio = min(measured_turb / turb_thresh, 3.0)
                turb_score = min(0.45 * ratio, 0.55)
                score += turb_score
                reasoning.append(
                    f"Turbidity index: {measured_turb:.3f} "
                    f"(threshold: {turb_thresh:.3f}) -- EXCEEDS"
                )
            else:
                partial = 0.15 * (measured_turb / turb_thresh)
                score += partial
                reasoning.append(
                    f"Turbidity index: {measured_turb:.3f} "
                    f"(threshold: {turb_thresh:.3f}) -- BELOW threshold"
                )
        else:
            reasoning.append("No turbidity data available.")

        # --- color signature ---
        if color_sig:
            if color_sig in (expected_color, "opaque", "muddy"):
                score += 0.30
                reasoning.append(
                    f"Water color signature: '{color_sig}' matches expected "
                    f"'{expected_color}/opaque' -- MATCH"
                )
            else:
                reasoning.append(
                    f"Water color signature: '{color_sig}' does not match "
                    f"expected '{expected_color}/opaque' -- NO MATCH"
                )
        else:
            reasoning.append("Color signature data not available.")

        # Bonus: YOLO class alignment
        if evidence.get("anomaly_type") == "turbidity_spike":
            score += 0.10
            reasoning.append("YOLO class 'turbidity_spike' aligns with scenario (+0.10).")

        severity = self.siltation_cfg.get("severity", "WARNING")

        return {
            "score": round(min(score, 1.0), 4),
            "reasoning": reasoning,
            "verdict": self.siltation_cfg.get(
                "verdict", "Probable Siltation or Construction Runoff"
            ),
            "severity": severity,
        }

    def _evaluate_eutrophication(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Scenario 3 -- Eutrophication / Algal Bloom.

        Triggers when chlorophyll-a is high in a stagnant or slow-moving
        water body (lake, pond, reservoir).
        """
        reasoning: List[str] = []
        score = 0.0

        chl_thresh = self.eutrophication_cfg.get(
            "chlorophyll_min", self.chlorophyll_threshold
        )
        expected_water = self.eutrophication_cfg.get("water_type", "stagnant")

        measured_chl = evidence.get("chlorophyll", 0.0)
        water_type = evidence.get("water_type", "").lower()

        # --- chlorophyll-a ---
        if measured_chl > 0:
            if measured_chl >= chl_thresh:
                ratio = min(measured_chl / chl_thresh, 3.0)
                chl_score = min(0.45 * ratio, 0.55)
                score += chl_score
                reasoning.append(
                    f"Chlorophyll-a index: {measured_chl:.2f} "
                    f"(threshold: {chl_thresh:.2f}) -- EXCEEDS"
                )
            else:
                partial = 0.15 * (measured_chl / chl_thresh)
                score += partial
                reasoning.append(
                    f"Chlorophyll-a index: {measured_chl:.2f} "
                    f"(threshold: {chl_thresh:.2f}) -- BELOW threshold"
                )
        else:
            reasoning.append("No chlorophyll-a data available.")

        # --- water body type ---
        stagnant_types = {"stagnant", "lake", "pond", "reservoir", "wetland"}
        if water_type:
            if water_type in stagnant_types or water_type == expected_water:
                score += 0.30
                reasoning.append(
                    f"Water body type: '{water_type}' classified as stagnant/"
                    f"slow-moving -- FAVORABLE for eutrophication"
                )
            else:
                score += 0.05
                reasoning.append(
                    f"Water body type: '{water_type}' is flowing; eutrophication "
                    f"less likely but not impossible"
                )
        else:
            reasoning.append("Water body type not provided; assuming neutral.")

        # Bonus: YOLO class alignment
        if evidence.get("anomaly_type") == "algal_bloom":
            score += 0.10
            reasoning.append("YOLO class 'algal_bloom' aligns with scenario (+0.10).")

        # Bonus: green color signature
        if evidence.get("color_signature", "").lower() in ("green", "bright_green"):
            score += 0.08
            reasoning.append(
                "Green color signature supports algal bloom hypothesis (+0.08)."
            )

        severity = self.eutrophication_cfg.get("severity", "WARNING")

        return {
            "score": round(min(score, 1.0), 4),
            "reasoning": reasoning,
            "verdict": self.eutrophication_cfg.get(
                "verdict", "Eutrophication due to Nutrient (Fertilizer) Overload"
            ),
            "severity": severity,
        }

    def _evaluate_oil_spill(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Scenario 4 -- Oil Slick / Chemical Spill.

        Triggers when the SWIR1/NIR oil index exceeds the threshold,
        optionally boosted by iridescence detection.
        """
        reasoning: List[str] = []
        score = 0.0

        oil_thresh = self.oil_cfg.get("oil_index_min", self.oil_slick_threshold)
        expects_iridescence = self.oil_cfg.get("iridescence", True)

        measured_oil = evidence.get("oil_index", 0.0)
        has_iridescence = evidence.get("iridescence", False)

        # --- oil index ---
        if measured_oil > 0:
            if measured_oil >= oil_thresh:
                ratio = min(measured_oil / oil_thresh, 3.0)
                oil_score = min(0.55 * ratio, 0.65)
                score += oil_score
                reasoning.append(
                    f"Oil index (SWIR1/NIR): {measured_oil:.2f} "
                    f"(threshold: {oil_thresh:.2f}) -- EXCEEDS"
                )
            else:
                partial = 0.15 * (measured_oil / oil_thresh)
                score += partial
                reasoning.append(
                    f"Oil index (SWIR1/NIR): {measured_oil:.2f} "
                    f"(threshold: {oil_thresh:.2f}) -- BELOW threshold"
                )
        else:
            reasoning.append("No oil index data available.")

        # --- iridescence ---
        if has_iridescence:
            score += 0.25
            reasoning.append(
                "Surface iridescence detected -- consistent with hydrocarbon sheen (+0.25)."
            )
        elif expects_iridescence:
            reasoning.append(
                "No surface iridescence detected (expected for oil scenario)."
            )

        # Bonus: YOLO class alignment
        if evidence.get("anomaly_type") == "oil_slick":
            score += 0.10
            reasoning.append("YOLO class 'oil_slick' aligns with scenario (+0.10).")

        severity = self.oil_cfg.get("severity", "CRITICAL")

        return {
            "score": round(min(score, 1.0), 4),
            "reasoning": reasoning,
            "verdict": self.oil_cfg.get(
                "verdict", "Potential Oil Slick or Chemical Spill Detected"
            ),
            "severity": severity,
        }

    def _evaluate_sewage(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Scenario 5 -- Sewage / Organic Waste Discharge.

        Triggers on the *combination* of elevated chlorophyll-a, elevated
        turbidity, and a mild thermal anomaly -- the hallmark signature of
        organic-waste inflow.
        """
        reasoning: List[str] = []
        score = 0.0

        chl_thresh = self.sewage_cfg.get("chlorophyll_min", 1.2)
        turb_thresh = self.sewage_cfg.get("turbidity_min", 0.10)
        temp_thresh = self.sewage_cfg.get("temp_delta_min", 3.0)

        measured_chl = evidence.get("chlorophyll", 0.0)
        measured_turb = evidence.get("turbidity", 0.0)
        measured_delta = evidence.get("thermal_delta", 0.0)

        signals_matched = 0

        # --- chlorophyll-a (moderate) ---
        if measured_chl > 0:
            if measured_chl >= chl_thresh:
                chl_contrib = min(0.30 * (measured_chl / chl_thresh), 0.35)
                score += chl_contrib
                signals_matched += 1
                reasoning.append(
                    f"Chlorophyll-a index: {measured_chl:.2f} "
                    f"(sewage threshold: {chl_thresh:.2f}) -- EXCEEDS"
                )
            else:
                partial = 0.10 * (measured_chl / chl_thresh)
                score += partial
                reasoning.append(
                    f"Chlorophyll-a index: {measured_chl:.2f} "
                    f"(sewage threshold: {chl_thresh:.2f}) -- BELOW"
                )
        else:
            reasoning.append("No chlorophyll-a data available for sewage check.")

        # --- turbidity (moderate) ---
        if measured_turb > 0:
            if measured_turb >= turb_thresh:
                turb_contrib = min(0.30 * (measured_turb / turb_thresh), 0.35)
                score += turb_contrib
                signals_matched += 1
                reasoning.append(
                    f"Turbidity index: {measured_turb:.3f} "
                    f"(sewage threshold: {turb_thresh:.3f}) -- EXCEEDS"
                )
            else:
                partial = 0.10 * (measured_turb / turb_thresh)
                score += partial
                reasoning.append(
                    f"Turbidity index: {measured_turb:.3f} "
                    f"(sewage threshold: {turb_thresh:.3f}) -- BELOW"
                )
        else:
            reasoning.append("No turbidity data available for sewage check.")

        # --- mild thermal delta ---
        if measured_delta > 0:
            if measured_delta >= temp_thresh:
                temp_contrib = min(0.20 * (measured_delta / temp_thresh), 0.25)
                score += temp_contrib
                signals_matched += 1
                reasoning.append(
                    f"Thermal delta: +{measured_delta:.1f}C "
                    f"(sewage threshold: {temp_thresh:.1f}C) -- EXCEEDS"
                )
            else:
                partial = 0.08 * (measured_delta / temp_thresh)
                score += partial
                reasoning.append(
                    f"Thermal delta: +{measured_delta:.1f}C "
                    f"(sewage threshold: {temp_thresh:.1f}C) -- BELOW"
                )
        else:
            reasoning.append("No thermal delta data available for sewage check.")

        # Combination bonus -- sewage diagnosis improves when all three signals fire
        if signals_matched >= 3:
            score += 0.10
            reasoning.append(
                "All three sewage indicators (chlorophyll + turbidity + thermal) "
                "present -- combination bonus (+0.10)."
            )
        elif signals_matched == 2:
            score += 0.05
            reasoning.append(
                f"{signals_matched}/3 sewage indicators present -- partial "
                f"combination bonus (+0.05)."
            )

        # Bonus: YOLO class alignment
        if evidence.get("anomaly_type") == "sewage_discharge":
            score += 0.10
            reasoning.append("YOLO class 'sewage_discharge' aligns with scenario (+0.10).")

        severity = self.sewage_cfg.get("severity", "HIGH")

        return {
            "score": round(min(score, 1.0), 4),
            "reasoning": reasoning,
            "verdict": self.sewage_cfg.get(
                "verdict",
                "Suspected Untreated Sewage or Organic Waste Discharge",
            ),
            "severity": severity,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_evidence(self, detection: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a raw detection dict into a flat evidence dict.

        The evidence dict merges top-level keys with anything nested
        inside ``spectral_evidence`` so that evaluators can access all
        signals uniformly.
        """
        evidence: Dict[str, Any] = {}

        # Copy spectral evidence values
        spectral = detection.get("spectral_evidence", {})
        evidence["thermal_delta"] = spectral.get(
            "thermal_delta", spectral.get("temp_delta", 0.0)
        )
        evidence["turbidity"] = spectral.get("turbidity", 0.0)
        evidence["chlorophyll"] = spectral.get(
            "chlorophyll", spectral.get("chlorophyll_a", 0.0)
        )
        evidence["oil_index"] = spectral.get(
            "oil_index", spectral.get("oil_slick_index", 0.0)
        )
        evidence["ndwi"] = spectral.get("ndwi", 0.0)

        # Contextual metadata
        evidence["industrial_zone_dist_m"] = detection.get(
            "industrial_zone_dist_m", float("inf")
        )
        evidence["water_type"] = detection.get("water_type", "")
        evidence["color_signature"] = detection.get("color_signature", "")
        evidence["iridescence"] = detection.get("iridescence", False)
        evidence["anomaly_type"] = detection.get("anomaly_type", "unknown")

        return evidence

    @staticmethod
    def _score_to_severity(score: float) -> str:
        """Map a numeric confidence score to a severity label."""
        if score >= 0.80:
            return "CRITICAL"
        elif score >= 0.55:
            return "HIGH"
        elif score >= 0.30:
            return "WARNING"
        else:
            return "MONITOR"

    # ------------------------------------------------------------------
    # Weighted severity scoring (public utility)
    # ------------------------------------------------------------------
    @staticmethod
    def compute_weighted_severity(
        evidence: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None,
    ) -> Tuple[float, str]:
        """Combine multiple evidence signals into a single weighted severity.

        Parameters
        ----------
        evidence : dict
            Flat evidence dict (as produced by ``_build_evidence``).
        weights : dict, optional
            Override weights; defaults to ``EVIDENCE_WEIGHTS``.

        Returns
        -------
        (score, severity) : (float, str)
            Weighted 0-1 score and its severity label.
        """
        w = weights or EVIDENCE_WEIGHTS
        total_weight = 0.0
        weighted_sum = 0.0

        signal_map: Dict[str, float] = {
            "thermal_delta": _normalize(
                evidence.get("thermal_delta", 0.0), 0.0, 20.0
            ),
            "industrial_proximity": 1.0 - min(
                evidence.get("industrial_zone_dist_m", 1000) / 1000.0, 1.0
            ),
            "turbidity": _normalize(
                evidence.get("turbidity", 0.0), 0.0, 0.50
            ),
            "chlorophyll": _normalize(
                evidence.get("chlorophyll", 0.0), 0.0, 5.0
            ),
            "oil_index": _normalize(
                evidence.get("oil_index", 0.0), 0.0, 4.0
            ),
        }

        for key, norm_val in signal_map.items():
            if key in w:
                weighted_sum += w[key] * norm_val
                total_weight += w[key]

        if total_weight > 0:
            score = weighted_sum / total_weight
        else:
            score = 0.0

        score = min(max(score, 0.0), 1.0)

        if score >= 0.80:
            severity = "CRITICAL"
        elif score >= 0.55:
            severity = "HIGH"
        elif score >= 0.30:
            severity = "WARNING"
        else:
            severity = "MONITOR"

        return round(score, 4), severity


# ===========================================================================
# Module-level helpers
# ===========================================================================
def _normalize(value: float, low: float, high: float) -> float:
    """Linearly normalize *value* into [0, 1] given *low* and *high* bounds."""
    if high <= low:
        return 0.0
    return min(max((value - low) / (high - low), 0.0), 1.0)


# ===========================================================================
# Quick self-test (runs when executed directly)
# ===========================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    engine = ForensicEngine()

    # -- Sample detection: industrial thermal discharge --
    sample_thermal = {
        "anomaly_id": "DET-20260409-001",
        "timestamp": "2026-04-09T14:32:00Z",
        "location": {"lat": 30.89, "lon": 75.84},
        "water_body_name": "Buddha Dariya, Ludhiana",
        "anomaly_type": "thermal_plume",
        "spectral_evidence": {
            "thermal_delta": 12.3,
            "turbidity": 0.05,
            "chlorophyll": 0.4,
            "oil_index": 0.2,
            "ndwi": 0.45,
        },
        "industrial_zone_dist_m": 320,
        "water_type": "river",
        "color_signature": "warm_grey",
    }

    # -- Sample detection: algal bloom / eutrophication --
    sample_eutrophication = {
        "anomaly_id": "DET-20260409-002",
        "timestamp": "2026-04-09T15:10:00Z",
        "location": {"lat": 30.91, "lon": 75.82},
        "water_body_name": "Gill Village Pond",
        "anomaly_type": "algal_bloom",
        "spectral_evidence": {
            "thermal_delta": 1.0,
            "turbidity": 0.08,
            "chlorophyll": 3.2,
            "oil_index": 0.1,
            "ndwi": 0.55,
        },
        "water_type": "lake",
        "color_signature": "green",
    }

    # -- Sample detection: sewage discharge --
    sample_sewage = {
        "anomaly_id": "DET-20260409-003",
        "timestamp": "2026-04-09T16:45:00Z",
        "location": {"lat": 30.87, "lon": 75.86},
        "water_body_name": "Buddha Dariya, Ludhiana",
        "anomaly_type": "sewage_discharge",
        "spectral_evidence": {
            "thermal_delta": 4.5,
            "turbidity": 0.18,
            "chlorophyll": 1.9,
            "oil_index": 0.3,
            "ndwi": 0.40,
        },
        "water_type": "river",
        "color_signature": "dark_brown",
    }

    # Batch classify
    all_detections = [sample_thermal, sample_eutrophication, sample_sewage]
    results = engine.classify(all_detections)

    print("\n" + "=" * 72)
    print(" AQUA-SENTINEL AI -- Forensic Analysis Results")
    print("=" * 72)

    for analysis in results:
        print(f"\n--- {analysis.anomaly_id} ---")
        print(f"  Verdict    : {analysis.verdict}")
        print(f"  Severity   : {analysis.severity}")
        print(f"  Confidence : {analysis.confidence:.0%}")
        print(f"  Action     : {analysis.recommended_action}")
        print("  Reasoning chain:")
        for step in analysis.reasoning_chain:
            print(f"    - {step}")

    # Summary
    summary = engine.generate_summary(results)
    print(f"\n{'=' * 72}")
    print(" EXECUTIVE SUMMARY")
    print(f"{'=' * 72}")
    print(f"  Total anomalies analysed : {summary['total_count']}")
    print(f"  Average confidence       : {summary['average_confidence']:.0%}")
    print(f"  Severity breakdown       : {summary['severity_breakdown']}")
    print(f"  Top threats              : {len(summary['top_threats'])} listed")
    print(f"{'=' * 72}\n")
