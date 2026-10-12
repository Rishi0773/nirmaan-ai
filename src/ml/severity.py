"""
NIRMAAN AI - Severity Assessment Engine
Calculates waste image coverage ratio via OpenCV and merges with YOLO object count
to derive an explainable Low, Medium, or High severity grade (PPT standard).
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
import cv2

from src.config import SEVERITY_THRESHOLDS


def compute_waste_coverage(image_path: str) -> float:
    """
    Analyzes pixel coverage of waste using OpenCV color space segmentation
    and morphological contour extraction. Returns percentage [0.0, 100.0].
    """
    img_bgr = cv2.imread(str(image_path))
    if img_bgr is None:
        return 0.0

    height, width = img_bgr.shape[:2]
    total_pixels = height * width

    # Convert to HSV to separate pavement luminance from vibrant litter/debris
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    # Waste is characterized by either high saturation (plastics/packaging)
    # or extreme dark/light patches compared to asphalt median
    sat_mask = cv2.threshold(s, 55, 255, cv2.THRESH_BINARY)[1]
    val_diff = cv2.absdiff(v, cv2.medianBlur(v, 21))
    val_mask = cv2.threshold(val_diff, 40, 255, cv2.THRESH_BINARY)[1]

    # Combine cues
    combined = cv2.bitwise_or(sat_mask, val_mask)

    # Morphological closing to fill small gaps in waste objects
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    closed = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=2)

    waste_pixels = cv2.countNonZero(closed)
    if waste_pixels == 0:
        return 0.0

    coverage_pct = (waste_pixels / total_pixels) * 100.0
    return float(np.clip(coverage_pct, 0.0, 85.0))


def evaluate_severity(
    total_objects: int,
    coverage_ratio: float,
    detected_classes: Dict[str, int],
    waste_category: str
) -> Dict[str, Any]:
    """
    Maps detected visual parameters into PPT core categories: Low, Medium, High.
    Returns normalized severity score [0.0, 100.0] and factor explanation.
    """
    has_hazard = ("hazardous" in detected_classes) or (waste_category == "hazardous")
    has_organic = ("organic" in detected_classes) or (waste_category == "organic")

    low_obj_max = SEVERITY_THRESHOLDS["low_max_objects"]
    low_cov_max = SEVERITY_THRESHOLDS["low_max_coverage"]
    med_obj_max = SEVERITY_THRESHOLDS["med_max_objects"]
    med_cov_max = SEVERITY_THRESHOLDS["med_max_coverage"]

    # PPT Core Severity Grading Logic
    if has_hazard:
        # Hazardous waste immediately triggers High severity regardless of volume
        severity_level = "High"
        base_score = 95.0
        reason = "Immediate High severity triggered by presence of hazardous/chemical waste."
    elif total_objects > med_obj_max or coverage_ratio >= med_cov_max:
        severity_level = "High"
        base_score = min(100.0, 75.0 + (coverage_ratio * 0.5) + (total_objects * 1.5))
        reason = f"High severity: {total_objects} detected objects with {coverage_ratio:.1f}% visual ground coverage."
    elif total_objects <= low_obj_max and coverage_ratio < low_cov_max:
        severity_level = "Low"
        base_score = max(10.0, 15.0 + (coverage_ratio * 1.2) + (total_objects * 3.0))
        reason = f"Low severity: Minor littering ({total_objects} items, {coverage_ratio:.1f}% ground coverage)."
    else:
        severity_level = "Medium"
        base_score = min(74.0, max(40.0, 40.0 + (coverage_ratio * 0.6) + (total_objects * 2.5)))
        reason = f"Medium severity: Moderate waste accumulation ({total_objects} items, {coverage_ratio:.1f}% coverage)."

    # Slight amplification for wet decomposing organic waste (health vector)
    if has_organic and severity_level != "High":
        base_score = min(74.0, base_score + 8.0)
        reason += " Elevated due to decomposing organic matter."

    final_score = round(float(np.clip(base_score, 0.0, 100.0)), 1)

    factors = {
        "object_count": total_objects,
        "coverage_ratio_pct": round(coverage_ratio, 1),
        "hazard_flag": has_hazard,
        "organic_flag": has_organic,
        "primary_category": waste_category,
        "grading_rationale": reason
    }

    return {
        "severity_level": severity_level,
        "severity_score": final_score,
        "coverage_ratio": round(coverage_ratio, 1),
        "factors": factors
    }
