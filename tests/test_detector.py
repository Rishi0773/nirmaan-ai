"""
NIRMAAN AI - Unit Tests: Computer Vision Detector & Saliency Fallback
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
from src.ml.detector import detect_waste, run_opencv_saliency_detection


def test_opencv_saliency_detection():
    # Create synthetic test image with 3 distinct solid contours
    img = np.ones((480, 640, 3), dtype=np.uint8) * 120
    cv2.circle(img, (200, 200), 30, (0, 0, 255), -1)
    cv2.circle(img, (400, 250), 25, (255, 0, 0), -1)
    cv2.rectangle(img, (300, 320), (360, 370), (0, 255, 0), -1)

    boxes, classes_count, max_conf = run_opencv_saliency_detection(img)
    assert len(boxes) >= 1
    assert max_conf > 0.0


def test_detect_waste_missing_file_handling():
    with pytest.raises(FileNotFoundError):
        detect_waste("non_existent_image_file_123.jpg", "TEST-UID")
