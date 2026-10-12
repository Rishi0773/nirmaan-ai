"""
NIRMAAN AI - Incident Reporting & Validation Service
Validates coordinates within Greater Bengaluru, verifies image formats,
and orchestrates the detection and persistence pipeline.
"""

from typing import Tuple, Dict, Any, Optional
from src.config import BENGALURU_BOUNDS, WASTE_CLASSES
from src.database.repository import Repository
from src.ml.detector import detect_waste
from src.ml.severity import evaluate_severity
from src.engine.priority import compute_priority_score


def validate_report_submission(
    latitude: float,
    longitude: float,
    ward_name: str,
    waste_category: str,
    has_image: bool
) -> Tuple[bool, Optional[str]]:
    """Validates submitted report inputs against civic standards."""
    if not has_image:
        return False, "An incident photograph is required for AI severity grading."

    if not ward_name or not ward_name.strip():
        return False, "Please select an assigned Bengaluru municipal ward."

    if waste_category not in WASTE_CLASSES:
        return False, f"Waste category '{waste_category}' is not recognized."

    b = BENGALURU_BOUNDS
    if not (b["lat_min"] <= latitude <= b["lat_max"] and b["lon_min"] <= longitude <= b["lon_max"]):
        return False, (
            f"Coordinates ({latitude:.4f}, {longitude:.4f}) fall outside Greater Bengaluru bounds "
            f"[{b['lat_min']}-{b['lat_max']}, {b['lon_min']}-{b['lon_max']}]."
        )

    return True, None
