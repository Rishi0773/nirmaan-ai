"""
NIRMAAN AI - Cleanup Verification Engine
Compares Before-and-After cleanup photographs using computer vision contour reduction,
computes waste removal percentages, evaluates viewpoint uncertainty, and yields
AI recommendations for supervisory sign-off (PPT Slide 8).
"""

from pathlib import Path
from typing import Dict, Any
import numpy as np
import cv2

from src.ml.severity import compute_waste_coverage


def verify_cleanup_images(before_image_path: str, after_image_path: str) -> Dict[str, Any]:
    """
    Compares before and after cleanup photos.
    Calculates percentage reduction in waste coverage, visual viewpoint similarity,
    and returns an AI recommendation with uncertainty flags.
    """
    b_path = Path(before_image_path)
    a_path = Path(after_image_path)

    if not b_path.exists() or not a_path.exists():
        raise FileNotFoundError("Both before and after image files must exist on disk.")

    before_bgr = cv2.imread(str(b_path))
    after_bgr = cv2.imread(str(a_path))

    if before_bgr is None or after_bgr is None:
        raise ValueError("Failed to load before or after image files into OpenCV.")

    # 1. Compute Waste Coverage on both images
    cov_before = compute_waste_coverage(str(b_path))
    cov_after = compute_waste_coverage(str(a_path))

    # Waste reduction percentage
    if cov_before > 0:
        reduction_pct = max(0.0, min(100.0, ((cov_before - cov_after) / cov_before) * 100.0))
    else:
        reduction_pct = 100.0 if cov_after <= 2.0 else 0.0

    # 2. Viewpoint & Background Consistency Check (ORB feature matching)
    # Check if the before and after images likely show the same geographic perspective
    orb = cv2.ORB_create(nfeatures=500)
    kp1, des1 = orb.detectAndCompute(cv2.cvtColor(before_bgr, cv2.COLOR_BGR2GRAY), None)
    kp2, des2 = orb.detectAndCompute(cv2.cvtColor(after_bgr, cv2.COLOR_BGR2GRAY), None)

    viewpoint_confidence = 70.0
    match_count = 0
    if des1 is not None and des2 is not None and len(des1) > 10 and len(des2) > 10:
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        match_count = len(matches)
        # More matches = higher confidence that both photos represent the same location/viewpoint
        viewpoint_confidence = float(np.clip(40.0 + (match_count * 0.8), 40.0, 95.0))

    # 3. AI Verdict & Recommendation
    if reduction_pct >= 80.0:
        ai_verdict = "Approved"
        recommendation = "AI confirms significant waste clearance (>80% reduction). Recommended for supervisor approval."
    elif reduction_pct >= 50.0:
        ai_verdict = "Uncertain"
        recommendation = "Moderate waste reduction detected (50%-80%). Residual litter visible; manual field audit advised."
    else:
        ai_verdict = "Rejected"
        recommendation = "Substantial waste remains (<50% reduction). Re-cleaning required before clearance."

    uncertainty_notes = []
    if viewpoint_confidence < 60.0:
        uncertainty_notes.append("Low viewpoint match: Images may have been captured from differing angles or lighting.")
    if cov_after > 10.0:
        uncertainty_notes.append(f"Residual waste coverage remains at {cov_after:.1f}%.")

    return {
        "coverage_before_pct": round(cov_before, 1),
        "coverage_after_pct": round(cov_after, 1),
        "waste_reduction_pct": round(reduction_pct, 1),
        "viewpoint_match_features": match_count,
        "viewpoint_confidence": round(viewpoint_confidence, 1),
        "ai_verdict": ai_verdict,
        "ai_recommendation": recommendation,
        "uncertainty_notes": uncertainty_notes,
        "human_verification_required": True
    }
