"""
NIRMAAN AI - System Configuration
Centralized settings, constants, mathematical defaults, and directory paths.
"""

from pathlib import Path
import os

# Root Directory Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
REPORTS_DIR = UPLOADS_DIR / "reports"
BEFORE_DIR = UPLOADS_DIR / "before"
AFTER_DIR = UPLOADS_DIR / "after"
ANNOTATIONS_DIR = UPLOADS_DIR / "annotated"
MODELS_DIR = DATA_DIR / "models"
EXPORTS_DIR = DATA_DIR / "exports"

ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
STYLES_DIR = ASSETS_DIR / "styles"

# Standard Assets
HERO_IMAGE_PATH = IMAGES_DIR / "bengaluru_hero.jpg"
LOGO_IMAGE_PATH = IMAGES_DIR / "nirmaan_logo.png"
AVATAR_IMAGE_PATH = IMAGES_DIR / "nirmaan_avatar.png"
EMPTY_STATE_IMAGE_PATH = IMAGES_DIR / "empty_state.png"

# Create directories if they do not exist
for folder in [DATA_DIR, UPLOADS_DIR, REPORTS_DIR, BEFORE_DIR, AFTER_DIR, ANNOTATIONS_DIR, MODELS_DIR, EXPORTS_DIR, ASSETS_DIR, IMAGES_DIR, STYLES_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Database
DB_PATH = DATA_DIR / "nirmaan.db"

# Model Paths
CUSTOM_YOLO_WEIGHTS = MODELS_DIR / "yolov8_waste_best.pt"
BASE_YOLO_WEIGHTS = "yolov8n.pt"

# Bengaluru Geographic Bounds (Validation Safeguards)
BENGALURU_BOUNDS = {
    "lat_min": 12.7500,
    "lat_max": 13.2500,
    "lon_min": 77.4000,
    "lon_max": 77.8500,
    "center_lat": 12.9716,
    "center_lon": 77.5946,
}

# Standard Supported Waste Classes
WASTE_CLASSES = [
    "plastic",
    "paper",
    "organic",
    "metal",
    "glass",
    "hazardous",
    "mixed_trash",
]

# Waste Type Urgency / Hazard Weights (0 to 100)
WASTE_TYPE_WEIGHTS = {
    "hazardous": 95.0,     # Biomedical, chemical, battery waste
    "organic": 80.0,       # Wet food, decaying matter attracting disease vectors
    "mixed_trash": 75.0,   # Unsegregated open blackspots
    "plastic": 60.0,       # Clogged drains, plastic accumulation
    "glass": 55.0,         # Sharp broken glass risks
    "metal": 45.0,         # Scrap metal
    "paper": 35.0,         # Dry paper/cardboard
}

# Core Prioritization Weights (PPT Baseline: Severity, Recurrence, Waste Type, Waiting Time)
# Sum = 1.0 (Normalized)
DEFAULT_PRIORITY_WEIGHTS = {
    "severity": 0.35,      # Computer vision severity (0-100)
    "recurrence": 0.25,    # Repeat hotspot frequency index (0-100)
    "waste_type": 0.20,    # Hazard/decay urgency (0-100)
    "waiting_time": 0.20,  # Elapsed days normalized (0-100)
}

# Severity Classification Thresholds (PPT: Low, Medium, High)
SEVERITY_THRESHOLDS = {
    "low_max_objects": 2,
    "low_max_coverage": 15.0,      # percentage
    "med_max_objects": 6,
    "med_max_coverage": 40.0,      # percentage
}

# Geospatial Clustering (DBSCAN Parameters)
HOTSPOT_CLUSTER_RADIUS_METERS = 200.0  # Proximity buffer for repeat incidents
MIN_SAMPLES_CLUSTER = 2                # Minimum reports to constitute a recurrence cluster

# User Roles
ROLES = [
    "Administrator",
    "Ward Officer",
    "Sanitation Supervisor",
    "Cleanup Worker",
    "Citizen",
]

# Default Civic Disclaimer
CIVIC_DISCLAIMER = (
    "NIRMAAN AI is an independent academic research prototype. Demonstration "
    "records are marked as simulated and are not official BBMP records."
)
