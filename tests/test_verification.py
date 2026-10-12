"""
NIRMAAN AI - Unit Tests: Cleanup Verification Engine
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
from src.ml.verification import verify_cleanup_images


def test_verification_on_synthetic_pair(tmp_path):
    b_path = tmp_path / "before.jpg"
    a_path = tmp_path / "after.jpg"

    # Before image with simulated waste spots
    b_img = np.ones((480, 640, 3), dtype=np.uint8) * 110
    cv2.circle(b_img, (300, 300), 40, (0, 0, 255), -1)
    cv2.circle(b_img, (200, 250), 35, (255, 0, 0), -1)
    cv2.imwrite(str(b_path), b_img)

    # After image with clean pavement
    a_img = np.ones((480, 640, 3), dtype=np.uint8) * 110
    cv2.imwrite(str(a_path), a_img)

    res = verify_cleanup_images(str(b_path), str(a_path))
    assert res["waste_reduction_pct"] >= 70.0
    assert res["ai_verdict"] in ["Approved", "Uncertain"]
