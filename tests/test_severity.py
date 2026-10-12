"""
NIRMAAN AI - Unit Tests: Severity Assessment Logic
"""

import pytest
from src.ml.severity import evaluate_severity


def test_evaluate_severity_low():
    # Minor litter
    res = evaluate_severity(
        total_objects=1,
        coverage_ratio=5.0,
        detected_classes={"paper": 1},
        waste_category="paper"
    )
    assert res["severity_level"] == "Low"
    assert res["severity_score"] < 40.0


def test_evaluate_severity_medium():
    # Moderate accumulation
    res = evaluate_severity(
        total_objects=4,
        coverage_ratio=25.0,
        detected_classes={"plastic": 4},
        waste_category="plastic"
    )
    assert res["severity_level"] == "Medium"
    assert 40.0 <= res["severity_score"] <= 74.0


def test_evaluate_severity_high_due_to_volume():
    # Large accumulation
    res = evaluate_severity(
        total_objects=10,
        coverage_ratio=45.0,
        detected_classes={"mixed_trash": 10},
        waste_category="mixed_trash"
    )
    assert res["severity_level"] == "High"
    assert res["severity_score"] >= 75.0


def test_evaluate_severity_high_due_to_hazardous_class():
    # Immediate high severity for hazard even if small object count
    res = evaluate_severity(
        total_objects=1,
        coverage_ratio=3.0,
        detected_classes={"hazardous": 1},
        waste_category="hazardous"
    )
    assert res["severity_level"] == "High"
    assert res["severity_score"] >= 90.0
