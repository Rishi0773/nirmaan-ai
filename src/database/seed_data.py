"""
NIRMAAN AI - Database Seeding Script
Generates realistic Bengaluru municipal demonstration reports, hot-spots,
cleanup tasks, and verification samples clearly flagged as simulated data.
"""

import os
import random
import numpy as np
import cv2
from datetime import datetime, timedelta
from pathlib import Path
from src.config import (
    UPLOADS_DIR, REPORTS_DIR, BEFORE_DIR, AFTER_DIR, ANNOTATIONS_DIR,
    WASTE_CLASSES, DEFAULT_PRIORITY_WEIGHTS, WASTE_TYPE_WEIGHTS
)
from src.database.connection import init_db, reset_db
from src.database.repository import Repository


def create_synthetic_image(output_path: Path, title: str, object_count: int, clean_state: bool = False):
    """
    Creates a realistic synthetic demonstration image with simulated asphalt/ground texture,
    visible waste contours/boxes, and civic identification watermark.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    height, width = 480, 640

    # Base texture: asphalt pavement grey-brown
    img = np.ones((height, width, 3), dtype=np.uint8) * 110
    noise = np.random.normal(0, 15, (height, width, 3)).astype(np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Road curb / pavement line
    cv2.line(img, (0, 360), (640, 360), (70, 70, 70), 3)
    cv2.rectangle(img, (0, 360), (640, 480), (130, 130, 120), -1)

    if not clean_state:
        # Draw simulated waste litter (bottles, bags, debris)
        colors = [
            (40, 40, 180),    # Red can
            (180, 200, 40),   # Cyan plastic bag
            (30, 140, 30),    # Green bottle
            (160, 160, 160),  # Tin foil
            (30, 80, 160),    # Cardboard brown
        ]
        np.random.seed(abs(hash(str(output_path))) % 10000)

        for i in range(max(1, object_count)):
            cx = np.random.randint(80, 560)
            cy = np.random.randint(180, 420)
            radius = np.random.randint(15, 45)
            color = colors[i % len(colors)]
            # Draw irregular polygon or ellipse
            axes = (radius, int(radius * 0.7))
            angle = np.random.randint(0, 180)
            cv2.ellipse(img, (cx, cy), axes, angle, 0, 360, color, -1)
            cv2.ellipse(img, (cx, cy), axes, angle, 0, 360, (20, 20, 20), 2)
    else:
        # Draw clean swept pavement with faint water wash marks
        cv2.putText(
            img, "[SITE CLEARED - BBMP FIELD VERIFIED]",
            (80, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 180, 0), 2
        )

    # Civic Header Watermark
    cv2.rectangle(img, (0, 0), (640, 32), (30, 30, 30), -1)
    status_tag = "CLEANED" if clean_state else f"UNRESOLVED ({object_count} ITEMS)"
    cv2.putText(
        img, f"NIRMAAN DEMO - {title[:35]} | {status_tag}",
        (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1
    )

    cv2.imwrite(str(output_path), img)
    return str(output_path)


def seed_database():
    """Seeds the database with representative Bengaluru ward reports."""
    print("Resetting database schema...")
    reset_db()
    repo = Repository()

    print("Creating civic users...")
    users = [
        ("admin_blr", "Dr. Ramesh Kumar", "Administrator", "admin@nirmaan.local", "9845011111", "Central"),
        ("officer_east", "Ananya Hegde", "Ward Officer", "a.hegde@nirmaan.local", "9845022222", "Koramangala"),
        ("officer_west", "Suresh Gowda", "Ward Officer", "s.gowda@nirmaan.local", "9845033333", "Malleshwaram"),
        ("supervisor_01", "Manjunath K", "Sanitation Supervisor", "manju.k@nirmaan.local", "9845044444", "Koramangala"),
        ("supervisor_02", "Deepak Rao", "Sanitation Supervisor", "d.rao@nirmaan.local", "9845055555", "Indiranagar"),
        ("worker_01", "Basavaraj P", "Cleanup Worker", "basava@nirmaan.local", "9845066666", "Koramangala"),
        ("worker_02", "Ravi Naik", "Cleanup Worker", "ravi.n@nirmaan.local", "9845077777", "Indiranagar"),
        ("citizen_blr", "Pooja Sharma", "Citizen", "pooja.blr@example.com", "9845088888", "Indiranagar"),
    ]
    user_ids = {}
    for u in users:
        uid = repo.create_user(u[0], u[1], u[2], u[3], u[4], u[5])
        user_ids[u[0]] = uid

    # Realistic Bengaluru Locations with clustering around known hotspots
    sample_incidents = [
        # Cluster 1: Koramangala 5th Block (Chronic Hotspot - 4 reports)
        {
            "uid": "REP-BLR-001",
            "lat": 12.9352, "lon": 77.6245,
            "ward": "Koramangala", "address": "80 Feet Rd, 5th Block, near Jyoti Nivas College",
            "cat": "mixed_trash", "days_ago": 6, "status": "Pending",
            "desc": "Heavy commercial food waste and overflowing bins spilling onto pedestrian walkway.",
            "objects": 9, "coverage": 48.0, "severity": "High", "score_sev": 92.0
        },
        {
            "uid": "REP-BLR-002",
            "lat": 12.9356, "lon": 77.6249,
            "ward": "Koramangala", "address": "1st Cross, 5th Block, near bakery corner",
            "cat": "organic", "days_ago": 4, "status": "Under Cleanup",
            "desc": "Wet kitchen waste accumulated for 3 days attracting stray animals.",
            "objects": 7, "coverage": 38.0, "severity": "High", "score_sev": 85.0
        },
        {
            "uid": "REP-BLR-003",
            "lat": 12.9348, "lon": 77.6241,
            "ward": "Koramangala", "address": "Corner of 5th Block park entrance",
            "cat": "plastic", "days_ago": 2, "status": "Pending",
            "desc": "Single-use plastic cups, water pouches, and packaging discarded along curb.",
            "objects": 5, "coverage": 22.0, "severity": "Medium", "score_sev": 60.0
        },
        {
            "uid": "REP-BLR-004",
            "lat": 12.9354, "lon": 77.6244,
            "ward": "Koramangala", "address": "Near Koramangala Post Office side wall",
            "cat": "mixed_trash", "days_ago": 8, "status": "Cleared",
            "desc": "Mixed street debris and paper packaging dumped after evening market.",
            "objects": 4, "coverage": 18.0, "severity": "Medium", "score_sev": 54.0
        },

        # Cluster 2: Indiranagar 100ft Road (High-frequency commercial - 3 reports)
        {
            "uid": "REP-BLR-005",
            "lat": 12.9719, "lon": 77.6412,
            "ward": "Indiranagar", "address": "100 Feet Rd, near 12th Main junction",
            "cat": "hazardous", "days_ago": 1, "status": "Pending",
            "desc": "Discarded chemical bottles and broken compact fluorescent lamps behind electrical transformer.",
            "objects": 8, "coverage": 42.0, "severity": "High", "score_sev": 96.0
        },
        {
            "uid": "REP-BLR-006",
            "lat": 12.9714, "lon": 77.6418,
            "ward": "Indiranagar", "address": "100 Feet Rd, lane beside retail plaza",
            "cat": "mixed_trash", "days_ago": 5, "status": "Under Cleanup",
            "desc": "Overflowing black bags left overnight outside restaurant kitchen.",
            "objects": 6, "coverage": 34.0, "severity": "Medium", "score_sev": 70.0
        },
        {
            "uid": "REP-BLR-007",
            "lat": 12.9722, "lon": 77.6409,
            "ward": "Indiranagar", "address": "13th Main corner, Indiranagar",
            "cat": "paper", "days_ago": 3, "status": "Cleared",
            "desc": "Discarded cardboard cartons and packaging boxes obstructing footpath.",
            "objects": 3, "coverage": 12.0, "severity": "Low", "score_sev": 32.0
        },

        # Cluster 3: Malleshwaram 8th Cross (Traditional Market - 3 reports)
        {
            "uid": "REP-BLR-008",
            "lat": 13.0031, "lon": 77.5701,
            "ward": "Malleshwaram", "address": "8th Cross, near vegetable market gate",
            "cat": "organic", "days_ago": 7, "status": "Pending",
            "desc": "Vegetable peels, rotten fruits, and damp banana leaves piling up by drain.",
            "objects": 11, "coverage": 52.0, "severity": "High", "score_sev": 94.0
        },
        {
            "uid": "REP-BLR-009",
            "lat": 13.0028, "lon": 77.5706,
            "ward": "Malleshwaram", "address": "7th Cross Sampige Road junction",
            "cat": "plastic", "days_ago": 4, "status": "Pending",
            "desc": "Plastic carry bags and fruit foam wrappers tossed under tree.",
            "objects": 5, "coverage": 24.0, "severity": "Medium", "score_sev": 62.0
        },
        {
            "uid": "REP-BLR-010",
            "lat": 13.0034, "lon": 77.5698,
            "ward": "Malleshwaram", "address": "Margosa Rd, behind temple precinct",
            "cat": "organic", "days_ago": 10, "status": "Cleared",
            "desc": "Wilted flower garlands and coconut shells.",
            "objects": 4, "coverage": 16.0, "severity": "Medium", "score_sev": 50.0
        },

        # Isolated Sites across Bengaluru
        {
            "uid": "REP-BLR-011",
            "lat": 12.9863, "lon": 77.7289,
            "ward": "Whitefield", "address": "ITPL Main Rd, near Pattandur Agrahara gate",
            "cat": "plastic", "days_ago": 3, "status": "Pending",
            "desc": "Plastic water bottles and construction tea cups scattered on mud verge.",
            "objects": 3, "coverage": 11.0, "severity": "Low", "score_sev": 28.0
        },
        {
            "uid": "REP-BLR-012",
            "lat": 12.9299, "lon": 77.5834,
            "ward": "Jayanagar", "address": "4th Block, 11th Main, opposite complex",
            "cat": "mixed_trash", "days_ago": 5, "status": "Under Cleanup",
            "desc": "Mixed domestic garbage dumped beside public park fence.",
            "objects": 6, "coverage": 30.0, "severity": "Medium", "score_sev": 65.0
        },
        {
            "uid": "REP-BLR-013",
            "lat": 12.9830, "lon": 77.6050,
            "ward": "Shivajinagar", "address": "Russell Market exterior wall, Meenakshi Koil St",
            "cat": "organic", "days_ago": 9, "status": "Pending",
            "desc": "Rotting butchery and vegetable waste causing severe stench.",
            "objects": 12, "coverage": 58.0, "severity": "High", "score_sev": 98.0
        },
        {
            "uid": "REP-BLR-014",
            "lat": 12.9116, "lon": 77.6389,
            "ward": "HSR Layout", "address": "Sector 2, 27th Main, near canal bridge",
            "cat": "metal", "days_ago": 2, "status": "Pending",
            "desc": "Rusted metal scrap and discarded iron rods dumped on open plot.",
            "objects": 4, "coverage": 19.0, "severity": "Medium", "score_sev": 48.0
        },
        {
            "uid": "REP-BLR-015",
            "lat": 12.9611, "lon": 77.5255,
            "ward": "Vijayanagar", "address": "Near Tollgate metro pillar 142",
            "cat": "paper", "days_ago": 1, "status": "Cleared",
            "desc": "Discarded advertising pamphlets and damp newspaper bundles.",
            "objects": 2, "coverage": 7.0, "severity": "Low", "score_sev": 20.0
        },
    ]

    print("Inserting incident reports and generating synthetic test images...")
    now = datetime.now()

    for inc in sample_incidents:
        created_time = (now - timedelta(days=inc["days_ago"])).strftime("%Y-%m-%d %H:%M:%S")
        rep_id = repo.create_report(
            report_uid=inc["uid"],
            latitude=inc["lat"],
            longitude=inc["lon"],
            ward_name=inc["ward"],
            waste_category=inc["cat"],
            address=inc["address"],
            description=inc["desc"],
            reporter_name=f"Citizen {inc['uid'][-3:]}",
            is_simulated=1,
            created_at=created_time
        )

        # Generate synthetic incident photograph
        img_name = f"{inc['uid']}_incident.jpg"
        img_path = REPORTS_DIR / img_name
        create_synthetic_image(img_path, inc["address"], inc["objects"])
        repo.add_report_image(rep_id, "incident", str(img_path))

        # Save computer vision detection record
        detected_classes = {inc["cat"]: inc["objects"]}
        bounding_boxes = [
            {"box": [50 + i * 40, 100 + i * 20, 90 + i * 40, 140 + i * 20], "cls": inc["cat"], "conf": 0.88}
            for i in range(min(5, inc["objects"]))
        ]
        repo.save_detection(
            report_id=rep_id,
            model_version="YOLOv8n-Litter-v1.0 (Demo Mode)",
            total_objects=inc["objects"],
            detected_classes=detected_classes,
            bounding_boxes=bounding_boxes,
            max_confidence=0.92,
            inference_time_ms=45.2
        )

        # Save severity assessment
        factors = {
            "object_count": inc["objects"],
            "coverage_pct": inc["coverage"],
            "hazard_detected": (inc["cat"] == "hazardous"),
            "primary_waste": inc["cat"]
        }
        repo.save_severity(
            report_id=rep_id,
            severity_level=inc["severity"],
            severity_score=inc["score_sev"],
            coverage_ratio=inc["coverage"],
            factors=factors,
            assessed_by="YOLOv8 + OpenCV Saliency"
        )

        # If status is Under Cleanup or Cleared, generate tasks and verification records
        if inc["status"] in ["Under Cleanup", "Cleared"]:
            task_code = f"TASK-{inc['uid'][-3:]}"
            task_id = repo.create_task(
                task_code=task_code,
                report_id=rep_id,
                assigned_team="Ward Strike Team Alpha",
                supervisor_id=user_ids["supervisor_01"],
                priority_level="High" if inc["severity"] == "High" else "Normal",
                notes="Dispatched per NIRMAAN priority ranking."
            )
            # Maintain the intended status
            repo.update_task_status(task_id, inc["status"], f"Task moved to {inc['status']}")

            if inc["status"] == "Cleared":
                # Create before & after images
                b_path = BEFORE_DIR / f"{inc['uid']}_before.jpg"
                a_path = AFTER_DIR / f"{inc['uid']}_after.jpg"
                create_synthetic_image(b_path, f"BEFORE {inc['uid']}", inc["objects"], clean_state=False)
                create_synthetic_image(a_path, f"AFTER {inc['uid']}", 0, clean_state=True)

                repo.add_report_image(rep_id, "before_cleanup", str(b_path))
                repo.add_report_image(rep_id, "after_cleanup", str(a_path))

                repo.save_verification(
                    task_id=task_id,
                    before_image_path=str(b_path),
                    after_image_path=str(a_path),
                    waste_reduction_pct=95.4,
                    ai_verdict="Approved",
                    supervisor_decision="Verified Clean",
                    verified_by=user_ids["supervisor_01"],
                    verification_notes="Confirmed spot clearance with BBMP health inspector."
                )

    print("Generating Hotspot clusters using spatial aggregation...")
    # Seed 3 well-defined hotspots
    hotspots_seed = [
        ("HS-BLR-001", "Koramangala", 12.9352, 77.6245, 180.0, 4, 88.5, 72.8),
        ("HS-BLR-002", "Indiranagar", 12.9718, 77.6413, 150.0, 3, 76.0, 66.0),
        ("HS-BLR-003", "Malleshwaram", 13.0031, 77.5702, 200.0, 3, 82.0, 68.7),
    ]

    for hs in hotspots_seed:
        hid = repo.save_hotspot(
            hotspot_code=hs[0],
            ward_name=hs[1],
            centroid_lat=hs[2],
            centroid_lon=hs[3],
            radius_meters=hs[4],
            incident_count=hs[5],
            recurrence_score=hs[6],
            avg_severity=hs[7],
            status="Active"
        )
        # Link corresponding reports
        reports = repo.get_all_reports(ward=hs[1])
        for r in reports[:hs[5]]:
            repo.link_hotspot_report(hid, r["id"])

    print("Calculating initial baseline priority scores...")
    from src.engine.priority import calculate_and_save_all_priorities
    calculate_and_save_all_priorities(repo)

    print("Adding sample civic notifications...")
    repo.add_notification(
        title="High Severity Hotspot Flagged",
        message="Russell Market exterior wall (Shivajinagar) has accumulated severe decomposing waste.",
        category="Priority Alert",
        target_role="Sanitation Supervisor",
        link_ref="REP-BLR-013"
    )
    repo.add_notification(
        title="Verification Pending Review",
        message="Cleanup evidence submitted for Koramangala Post Office side wall (REP-BLR-004).",
        category="Verification",
        target_role="Ward Officer",
        link_ref="REP-BLR-004"
    )
    repo.add_notification(
        title="Hazardous Waste Alert",
        message="Transformer corner in Indiranagar 100ft Rd contains broken lamps and chemicals.",
        category="Priority Alert",
        target_role="Administrator",
        link_ref="REP-BLR-005"
    )

    print("Logging audit entries...")
    repo.log_audit("SYSTEM_INIT", "Database", "ALL", "System", None, "", "Seeded 15 Bengaluru demonstration reports.")
    repo.log_audit("PRIORITY_CALC", "Engine", "ALL", "AI Engine", None, "", "Computed transparent priority rankings.")

    print("Database seeding completed successfully!")


if __name__ == "__main__":
    init_db()
    seed_database()
