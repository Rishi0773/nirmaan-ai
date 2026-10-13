"""
NIRMAAN AI - Data Repository
Encapsulates all database queries, transactions, status state transitions,
and civic role operations for reports, hotspots, tasks, and audit logs.
"""

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from src.database.connection import get_connection
from src.config import DB_PATH, CUSTOM_YOLO_WEIGHTS, BASE_YOLO_WEIGHTS


class Repository:
    def __init__(self, db_path=None):
        self.db_path = db_path

    def _conn(self):
        if self.db_path:
            return get_connection(self.db_path)
        return get_connection()

    # ==========================
    # USERS
    # ==========================
    def get_users(self) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM users ORDER BY id ASC").fetchall()
            return [dict(r) for r in rows]

    get_all_users = get_users

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return dict(row) if row else None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            return dict(row) if row else None

    def get_users_by_role(self, role: str) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM users WHERE role = ? ORDER BY full_name ASC", (role,)).fetchall()
            return [dict(r) for r in rows]

    def create_user(self, username: str, full_name: str, role: str, email: str = "", phone: str = "", ward: str = "") -> int:
        with self._conn() as conn:
            cursor = conn.execute(
                "INSERT INTO users (username, full_name, role, email, phone, ward_assigned) VALUES (?, ?, ?, ?, ?, ?)",
                (username, full_name, role, email, phone, ward)
            )
            return cursor.lastrowid

    def update_user_role(self, user_id: int, new_role: str, ward: str = ""):
        with self._conn() as conn:
            if ward:
                conn.execute("UPDATE users SET role = ?, ward_assigned = ? WHERE id = ?", (new_role, ward, user_id))
            else:
                conn.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))

    # ==========================
    # REPORTS & CITIZEN SUBMISSION
    # ==========================
    def create_report(
        self,
        report_uid: str,
        latitude: float,
        longitude: float,
        ward_name: str,
        waste_category: str,
        address: str = "",
        landmark: str = "",
        description: str = "",
        reporter_name: str = "Anonymous Citizen",
        reporter_contact: str = "",
        is_simulated: int = 0,
        citizen_id: Optional[int] = None,
        created_at: Optional[str] = None
    ) -> int:
        with self._conn() as conn:
            if created_at:
                cursor = conn.execute(
                    """
                    INSERT INTO reports (
                        report_uid, latitude, longitude, address, ward_name, landmark,
                        description, waste_category, reporter_name, reporter_contact,
                        is_simulated, citizen_id, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (report_uid, latitude, longitude, address, ward_name, landmark,
                     description, waste_category, reporter_name, reporter_contact,
                     is_simulated, citizen_id, created_at, created_at)
                )
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO reports (
                        report_uid, latitude, longitude, address, ward_name, landmark,
                        description, waste_category, reporter_name, reporter_contact,
                        is_simulated, citizen_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (report_uid, latitude, longitude, address, ward_name, landmark,
                     description, waste_category, reporter_name, reporter_contact, is_simulated, citizen_id)
                )
            rep_id = cursor.lastrowid

            # Initialize first history record
            conn.execute(
                """
                INSERT INTO report_status_history (report_id, old_status, new_status, changed_by_name, reason)
                VALUES (?, NULL, 'Submitted', ?, 'Citizen complaint filed')
                """,
                (rep_id, reporter_name)
            )
            return rep_id

    def get_report_by_id(self, report_id: int) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            query = """
                SELECT r.*,
                       s.severity_level, s.severity_score, s.coverage_ratio,
                       d.total_objects, d.model_version,
                       p.score as priority_score, p.rank as priority_rank,
                       p.severity_component, p.recurrence_component,
                       p.waste_type_component, p.waiting_time_component,
                       img.file_path as image_path, img.annotated_path
                FROM reports r
                LEFT JOIN severity_assessments s ON r.id = s.report_id
                LEFT JOIN detections d ON r.id = d.report_id
                LEFT JOIN priority_scores p ON r.id = p.report_id
                LEFT JOIN report_images img ON r.id = img.report_id AND img.image_type = 'incident'
                WHERE r.id = ?
            """
            row = conn.execute(query, (report_id,)).fetchone()
            return dict(row) if row else None

    def get_report_by_uid(self, report_uid: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            query = """
                SELECT r.*,
                       s.severity_level, s.severity_score, s.coverage_ratio,
                       d.total_objects, d.model_version,
                       p.score as priority_score, p.rank as priority_rank,
                       p.severity_component, p.recurrence_component,
                       p.waste_type_component, p.waiting_time_component,
                       img.file_path as image_path, img.annotated_path
                FROM reports r
                LEFT JOIN severity_assessments s ON r.id = s.report_id
                LEFT JOIN detections d ON r.id = d.report_id
                LEFT JOIN priority_scores p ON r.id = p.report_id
                LEFT JOIN report_images img ON r.id = img.report_id AND img.image_type = 'incident'
                WHERE r.report_uid = ?
            """
            row = conn.execute(query, (report_uid,)).fetchone()
            return dict(row) if row else None

    def get_all_reports(self, status: Optional[str] = None, ward: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT r.*,
                   s.severity_level, s.severity_score, s.coverage_ratio,
                   d.total_objects, d.model_version,
                   p.score as priority_score, p.rank as priority_rank,
                   p.severity_component, p.recurrence_component,
                   p.waste_type_component, p.waiting_time_component,
                   img.file_path as image_path, img.annotated_path
            FROM reports r
            LEFT JOIN severity_assessments s ON r.id = s.report_id
            LEFT JOIN detections d ON r.id = d.report_id
            LEFT JOIN priority_scores p ON r.id = p.report_id
            LEFT JOIN report_images img ON r.id = img.report_id AND img.image_type = 'incident'
            WHERE 1=1
        """
        params = []
        if status and status != "All":
            query += " AND r.status = ?"
            params.append(status)
        if ward and ward != "All":
            query += " AND r.ward_name = ?"
            params.append(ward)

        query += " ORDER BY COALESCE(p.score, 0) DESC, r.created_at ASC"

        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_reports_for_citizen(self, citizen_id: Optional[int] = None, reporter_name: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            query = """
                SELECT r.*,
                       s.severity_level, s.severity_score,
                       p.score as priority_score, p.rank as priority_rank,
                       img.file_path as image_path, img.annotated_path
                FROM reports r
                LEFT JOIN severity_assessments s ON r.id = s.report_id
                LEFT JOIN priority_scores p ON r.id = p.report_id
                LEFT JOIN report_images img ON r.id = img.report_id AND img.image_type = 'incident'
                WHERE 1=1
            """
            params = []
            if citizen_id:
                query += " AND (r.citizen_id = ? OR r.reporter_name = ?)"
                params.extend([citizen_id, reporter_name or ""])
            elif reporter_name:
                query += " AND r.reporter_name = ?"
                params.append(reporter_name)
            query += " ORDER BY r.created_at DESC"
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def update_report_status(self, report_id: int, new_status: str):
        """Basic status update preserved for backward-compatibility with tests."""
        with self._conn() as conn:
            conn.execute(
                "UPDATE reports SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_status, report_id)
            )

    def transition_report_status(
        self,
        report_id: int,
        new_status: str,
        user_id: Optional[int] = None,
        user_name: str = "System",
        reason: str = ""
    ):
        """
        Controlled state-machine transition recording old and new statuses,
        timestamp, user identity, and justification into report_status_history.
        """
        with self._conn() as conn:
            curr = conn.execute("SELECT status, report_uid FROM reports WHERE id = ?", (report_id,)).fetchone()
            if not curr:
                return
            old_st = curr["status"]
            uid = curr["report_uid"]

            conn.execute(
                "UPDATE reports SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_status, report_id)
            )
            conn.execute(
                """
                INSERT INTO report_status_history (report_id, old_status, new_status, changed_by_user_id, changed_by_name, reason)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (report_id, old_st, new_status, user_id, user_name, reason)
            )
            conn.execute(
                """
                INSERT INTO audit_logs (user_id, user_name, action, entity_type, entity_id, old_value, new_value)
                VALUES (?, ?, 'STATUS_TRANSITION', 'Report', ?, ?, ?)
                """,
                (user_id, user_name, uid, old_st, f"{new_status} ({reason})")
            )

    def get_report_status_history(self, report_id: int) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM report_status_history WHERE report_id = ? ORDER BY created_at ASC, id ASC",
                (report_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    def add_report_followup(self, report_id: int, user_id: Optional[int], user_name: str, notes: str):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO report_followups (report_id, user_id, user_name, notes) VALUES (?, ?, ?, ?)",
                (report_id, user_id, user_name, notes)
            )

    def get_report_followups(self, report_id: int) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM report_followups WHERE report_id = ? ORDER BY created_at ASC",
                (report_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    def find_duplicate_reports(self, lat: float, lon: float, waste_category: Optional[str] = None, max_meters: float = 60.0) -> List[Dict[str, Any]]:
        """
        Checks for nearby pending reports within max_meters using the Haversine formula
        to alert citizens and prevent duplicate clutter.
        """
        all_reps = self.get_all_reports()
        duplicates = []
        for r in all_reps:
            if r["status"] == "Cleared":
                continue
            r_lat = r["latitude"]
            r_lon = r["longitude"]

            # Haversine distance in meters
            dlat = math.radians(r_lat - lat)
            dlon = math.radians(r_lon - lon)
            a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(r_lat)) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            dist_m = 6371000 * c

            if dist_m <= max_meters:
                duplicates.append({**r, "distance_meters": round(dist_m, 1)})
        return duplicates

    # ==========================
    # IMAGES & DETECTIONS
    # ==========================
    def add_report_image(self, report_id: int, image_type: str, file_path: str, annotated_path: str = "") -> int:
        with self._conn() as conn:
            cursor = conn.execute(
                "INSERT INTO report_images (report_id, image_type, file_path, annotated_path) VALUES (?, ?, ?, ?)",
                (report_id, image_type, file_path, annotated_path)
            )
            return cursor.lastrowid

    def get_report_images(self, report_id: int) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM report_images WHERE report_id = ?", (report_id,)).fetchall()
            return [dict(r) for r in rows]

    def save_detection(
        self,
        report_id: int,
        model_version: str,
        total_objects: int,
        detected_classes: Dict[str, int],
        bounding_boxes: List[Any],
        max_confidence: float = 0.0,
        inference_time_ms: float = 0.0
    ):
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO detections (
                    report_id, model_version, total_objects, detected_classes_json,
                    bounding_boxes_json, max_confidence, inference_time_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    model_version,
                    total_objects,
                    json.dumps(detected_classes),
                    json.dumps(bounding_boxes),
                    max_confidence,
                    inference_time_ms
                )
            )

    def save_severity(
        self,
        report_id: int,
        severity_level: str,
        severity_score: float,
        coverage_ratio: float,
        factors: Dict[str, Any],
        assessed_by: str = "AI Engine"
    ):
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO severity_assessments (
                    report_id, severity_level, severity_score, coverage_ratio, factors_json, assessed_by
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    severity_level,
                    severity_score,
                    coverage_ratio,
                    json.dumps(factors),
                    assessed_by
                )
            )

    # ==========================
    # HOTSPOTS & SPATIAL CLUSTERING
    # ==========================
    def clear_hotspots(self):
        with self._conn() as conn:
            conn.execute("DELETE FROM hotspot_reports")
            conn.execute("DELETE FROM hotspots")

    def save_hotspot(
        self,
        hotspot_code: str,
        ward_name: str,
        centroid_lat: float,
        centroid_lon: float,
        radius_meters: float,
        incident_count: int,
        recurrence_score: float,
        avg_severity: float,
        status: str = "Active"
    ) -> int:
        with self._conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO hotspots (
                    hotspot_code, ward_name, centroid_lat, centroid_lon, radius_meters,
                    incident_count, recurrence_score, avg_severity, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(hotspot_code) DO UPDATE SET
                    centroid_lat = excluded.centroid_lat,
                    centroid_lon = excluded.centroid_lon,
                    radius_meters = excluded.radius_meters,
                    incident_count = excluded.incident_count,
                    recurrence_score = excluded.recurrence_score,
                    avg_severity = excluded.avg_severity,
                    status = excluded.status
                """,
                (
                    hotspot_code, ward_name, centroid_lat, centroid_lon, radius_meters,
                    incident_count, recurrence_score, avg_severity, status
                )
            )
            row = conn.execute("SELECT id FROM hotspots WHERE hotspot_code = ?", (hotspot_code,)).fetchone()
            return row[0] if row else cursor.lastrowid

    def link_hotspot_report(self, hotspot_id: int, report_id: int):
        with self._conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO hotspot_reports (hotspot_id, report_id) VALUES (?, ?)",
                (hotspot_id, report_id)
            )

    def get_all_hotspots(self) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM hotspots ORDER BY recurrence_score DESC, incident_count DESC").fetchall()
            return [dict(r) for r in rows]

    def get_hotspot_reports(self, hotspot_id: int) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT r.*, s.severity_level, s.severity_score
                FROM reports r
                JOIN hotspot_reports hr ON r.id = hr.report_id
                LEFT JOIN severity_assessments s ON r.id = s.report_id
                WHERE hr.hotspot_id = ?
                ORDER BY r.created_at DESC
                """,
                (hotspot_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    # ==========================
    # PRIORITY SCORES
    # ==========================
    def save_priority_score(
        self,
        report_id: int,
        score: float,
        severity_comp: float,
        recurrence_comp: float,
        waste_type_comp: float,
        waiting_time_comp: float,
        rank: int = 0
    ):
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO priority_scores (
                    report_id, score, severity_component, recurrence_component,
                    waste_type_component, waiting_time_component, rank
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report_id, score, severity_comp, recurrence_comp,
                    waste_type_comp, waiting_time_comp, rank
                )
            )

    def set_priority_override(self, report_id: int, manual_score: float, reason: str):
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE priority_scores
                SET manual_override_score = ?, override_reason = ?, score = ?
                WHERE report_id = ?
                """,
                (manual_score, reason, manual_score, report_id)
            )

    # ==========================
    # CLEANUP TASKS & OPERATIONS
    # ==========================
    def create_task(
        self,
        task_code: str,
        report_id: int,
        assigned_team: str,
        supervisor_id: Optional[int] = None,
        worker_id: Optional[int] = None,
        priority_level: str = "Normal",
        notes: str = ""
    ) -> int:
        with self._conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO cleanup_tasks (
                    task_code, report_id, assigned_team, supervisor_id, worker_id, priority_level, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (task_code, report_id, assigned_team, supervisor_id, worker_id, priority_level, notes)
            )
            # Synchronize report status to Under Cleanup
            conn.execute("UPDATE reports SET status = 'Under Cleanup' WHERE id = ?", (report_id,))
            conn.execute(
                """
                INSERT INTO report_status_history (report_id, old_status, new_status, changed_by_user_id, reason)
                VALUES (?, 'Pending', 'Under Cleanup', ?, ?)
                """,
                (report_id, supervisor_id, f"Dispatched task {task_code} to {assigned_team}")
            )
            return cursor.lastrowid

    def get_all_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT t.*, r.report_uid, r.ward_name, r.address, r.waste_category,
                   r.latitude, r.longitude,
                   s.severity_level, p.score as priority_score,
                   u.full_name as supervisor_name_full,
                   w.full_name as worker_name_full
            FROM cleanup_tasks t
            JOIN reports r ON t.report_id = r.id
            LEFT JOIN severity_assessments s ON r.id = s.report_id
            LEFT JOIN priority_scores p ON r.id = p.report_id
            LEFT JOIN users u ON t.supervisor_id = u.id
            LEFT JOIN users w ON t.worker_id = w.id
            WHERE 1=1
        """
        params = []
        if status and status != "All":
            query += " AND t.status = ?"
            params.append(status)
        query += " ORDER BY t.created_at DESC"

        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_tasks_for_worker(self, worker_id: int) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            user = conn.execute("SELECT ward_assigned, full_name FROM users WHERE id = ?", (worker_id,)).fetchone()
            worker_ward = user["ward_assigned"] if user else ""

            query = """
                SELECT t.*, r.report_uid, r.ward_name, r.address, r.landmark, r.description,
                       r.waste_category, r.latitude, r.longitude,
                       s.severity_level, s.severity_score,
                       p.score as priority_score, p.severity_component, p.recurrence_component,
                       p.waste_type_component, p.waiting_time_component,
                       img.file_path as incident_image_path
                FROM cleanup_tasks t
                JOIN reports r ON t.report_id = r.id
                LEFT JOIN severity_assessments s ON r.id = s.report_id
                LEFT JOIN priority_scores p ON r.id = p.report_id
                LEFT JOIN report_images img ON r.id = img.report_id AND img.image_type = 'incident'
                WHERE t.worker_id = ? OR (t.worker_id IS NULL AND r.ward_name = ?)
                ORDER BY CASE WHEN t.status IN ('Pending', 'Assigned', 'In Progress', 'Under Cleanup') THEN 1 ELSE 2 END,
                         COALESCE(p.score, 0) DESC
            """
            rows = conn.execute(query, (worker_id, worker_ward)).fetchall()
            return [dict(r) for r in rows]

    def assign_task_to_worker(self, task_id: int, worker_id: int, supervisor_id: Optional[int] = None, notes: str = ""):
        with self._conn() as conn:
            worker = conn.execute("SELECT full_name FROM users WHERE id = ?", (worker_id,)).fetchone()
            w_name = worker["full_name"] if worker else "Field Worker"

            conn.execute(
                """
                UPDATE cleanup_tasks
                SET worker_id = ?,
                    notes = CASE WHEN ? != '' THEN ? ELSE notes END,
                    status = 'Assigned',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (worker_id, notes, notes, task_id)
            )
            task = conn.execute("SELECT report_id, task_code FROM cleanup_tasks WHERE id = ?", (task_id,)).fetchone()
            if task:
                conn.execute(
                    """
                    INSERT INTO report_status_history (report_id, old_status, new_status, changed_by_user_id, reason)
                    VALUES (?, 'Under Cleanup', 'Assigned', ?, ?)
                    """,
                    (task["report_id"], supervisor_id, f"Assigned to worker {w_name}")
                )

    def worker_accept_task(self, task_id: int, worker_id: int, worker_name: str = "Worker"):
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE cleanup_tasks
                SET status = 'In Progress',
                    started_at = COALESCE(started_at, CURRENT_TIMESTAMP),
                    worker_id = COALESCE(worker_id, ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (worker_id, task_id)
            )
            task = conn.execute("SELECT report_id, task_code FROM cleanup_tasks WHERE id = ?", (task_id,)).fetchone()
            if task:
                conn.execute("UPDATE reports SET status = 'Under Cleanup', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (task["report_id"],))
                conn.execute(
                    """
                    INSERT INTO report_status_history (report_id, old_status, new_status, changed_by_user_id, changed_by_name, reason)
                    VALUES (?, 'Assigned', 'In Progress', ?, ?, 'Worker accepted task and commenced site clearance')
                    """,
                    (task["report_id"], worker_id, worker_name)
                )

    def worker_report_blocked(self, task_id: int, worker_id: int, worker_name: str, reason: str):
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE cleanup_tasks
                SET status = 'Blocked',
                    blocked_reason = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (reason, task_id)
            )
            task = conn.execute("SELECT report_id, task_code FROM cleanup_tasks WHERE id = ?", (task_id,)).fetchone()
            if task:
                conn.execute("UPDATE reports SET status = 'Blocked', blocked_reason = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (reason, task["report_id"]))
                conn.execute(
                    """
                    INSERT INTO report_status_history (report_id, old_status, new_status, changed_by_user_id, changed_by_name, reason)
                    VALUES (?, 'In Progress', 'Blocked', ?, ?, ?)
                    """,
                    (task["report_id"], worker_id, worker_name, f"Field Blocked: {reason}")
                )

    def worker_submit_completion(self, task_id: int, worker_id: int, worker_name: str, before_img: str, after_img: str, notes: str):
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE cleanup_tasks
                SET status = 'Awaiting Verification',
                    worker_notes = ?,
                    completed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (notes, task_id)
            )
            task = conn.execute("SELECT report_id, task_code FROM cleanup_tasks WHERE id = ?", (task_id,)).fetchone()
            if task:
                conn.execute("UPDATE reports SET status = 'Awaiting Verification', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (task["report_id"],))
                conn.execute(
                    """
                    INSERT INTO report_status_history (report_id, old_status, new_status, changed_by_user_id, changed_by_name, reason)
                    VALUES (?, 'In Progress', 'Awaiting Verification', ?, ?, 'Field cleanup completed; awaiting supervisory verification')
                    """,
                    (task["report_id"], worker_id, worker_name)
                )

        if before_img and after_img and Path(before_img).exists() and Path(after_img).exists():
            from src.ml.verification import verify_cleanup_images
            try:
                ver_res = verify_cleanup_images(before_img, after_img)
                reduction = ver_res.get("waste_reduction_pct", 0.0)
                verdict = ver_res.get("ai_verdict", "Uncertain")
            except Exception:
                reduction = 0.0
                verdict = "Uncertain"

            with self._conn() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO cleanup_verifications (
                        task_id, before_image_path, after_image_path, waste_reduction_pct,
                        ai_verdict, supervisor_decision, verification_notes
                    ) VALUES (?, ?, ?, ?, ?, 'Pending Review', ?)
                    """,
                    (task_id, before_img, after_img, reduction, verdict, notes)
                )

    def update_task_status(self, task_id: int, new_status: str, notes: str = ""):
        with self._conn() as conn:
            task = conn.execute("SELECT report_id FROM cleanup_tasks WHERE id = ?", (task_id,)).fetchone()
            if not task:
                return

            report_id = task["report_id"]
            completed_at = "CURRENT_TIMESTAMP" if new_status in ["Cleared", "Verified Closed"] else "NULL"
            started_at = "CURRENT_TIMESTAMP" if new_status in ["Under Cleanup", "In Progress"] else "NULL"

            conn.execute(
                f"""
                UPDATE cleanup_tasks
                SET status = ?,
                    notes = COALESCE(?, notes),
                    started_at = CASE WHEN ? IN ('Under Cleanup', 'In Progress') AND started_at IS NULL THEN CURRENT_TIMESTAMP ELSE started_at END,
                    completed_at = CASE WHEN ? IN ('Cleared', 'Verified Closed') THEN CURRENT_TIMESTAMP ELSE completed_at END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (new_status, notes if notes else None, new_status, new_status, task_id)
            )

            # Sync report status
            rep_sync_status = "Cleared" if new_status in ["Cleared", "Verified Closed"] else ("Under Cleanup" if new_status in ["In Progress", "Under Cleanup", "Awaiting Verification"] else new_status)
            conn.execute("UPDATE reports SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (rep_sync_status, report_id))

    def save_verification(
        self,
        task_id: int,
        before_image_path: str,
        after_image_path: str,
        waste_reduction_pct: float,
        ai_verdict: str,
        supervisor_decision: str,
        verified_by: Optional[int] = None,
        verification_notes: str = ""
    ) -> int:
        with self._conn() as conn:
            cursor = conn.execute(
                """
                INSERT OR REPLACE INTO cleanup_verifications (
                    task_id, before_image_path, after_image_path, waste_reduction_pct,
                    ai_verdict, supervisor_decision, verified_by, verification_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id, before_image_path, after_image_path, waste_reduction_pct,
                    ai_verdict, supervisor_decision, verified_by, verification_notes
                )
            )
            last_id = cursor.lastrowid

            task = conn.execute("SELECT report_id, task_code FROM cleanup_tasks WHERE id = ?", (task_id,)).fetchone()
            if task:
                report_id = task["report_id"]
                user = conn.execute("SELECT full_name FROM users WHERE id = ?", (verified_by,)).fetchone() if verified_by else None
                v_name = user["full_name"] if user else "Supervisor"

                if supervisor_decision == "Verified Clean":
                    conn.execute(
                        "UPDATE cleanup_tasks SET status = 'Cleared', notes = 'Cleanup verified by supervisory officer.', completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (task_id,)
                    )
                    conn.execute("UPDATE reports SET status = 'Cleared', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (report_id,))
                    conn.execute(
                        """
                        INSERT INTO report_status_history (report_id, old_status, new_status, changed_by_user_id, changed_by_name, reason)
                        VALUES (?, 'Awaiting Verification', 'Verified Closed', ?, ?, ?)
                        """,
                        (report_id, verified_by, v_name, f"Verified Clean ({waste_reduction_pct:.1f}% reduction): {verification_notes}")
                    )
                elif supervisor_decision == "Needs Re-cleaning":
                    conn.execute(
                        "UPDATE cleanup_tasks SET status = 'Reopened', notes = 'Verification failed. Reopened for re-cleaning.', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (task_id,)
                    )
                    conn.execute("UPDATE reports SET status = 'Reopened', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (report_id,))
                    conn.execute(
                        """
                        INSERT INTO report_status_history (report_id, old_status, new_status, changed_by_user_id, changed_by_name, reason)
                        VALUES (?, 'Awaiting Verification', 'Reopened', ?, ?, ?)
                        """,
                        (report_id, verified_by, v_name, f"Needs Re-cleaning: {verification_notes}")
                    )

            return last_id

    def get_verification_by_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM cleanup_verifications WHERE task_id = ?", (task_id,)).fetchone()
            return dict(row) if row else None

    # ==========================
    # NOTIFICATIONS & AUDIT
    # ==========================
    def add_notification(self, title: str, message: str, category: str, target_role: str = "All", link_ref: str = ""):
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO notifications (title, message, category, target_role, link_ref)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, message, category, target_role, link_ref)
            )

    def get_notifications(self, role: str = "All", unread_only: bool = False) -> List[Dict[str, Any]]:
        query = "SELECT * FROM notifications WHERE 1=1"
        params = []
        if role != "All" and role != "Administrator":
            query += " AND (target_role = ? OR target_role = 'All')"
            params.append(role)
        if unread_only:
            query += " AND is_read = 0"
        query += " ORDER BY created_at DESC LIMIT 50"

        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def mark_all_notifications_read(self):
        with self._conn() as conn:
            conn.execute("UPDATE notifications SET is_read = 1 WHERE is_read = 0")

    def log_audit(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        user_name: str = "System",
        user_id: Optional[int] = None,
        old_val: str = "",
        new_val: str = ""
    ):
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO audit_logs (
                    user_id, user_name, action, entity_type, entity_id, old_value, new_value
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, user_name, action, entity_type, entity_id, old_val, new_val)
            )

    def get_audit_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    # ==========================
    # DASHBOARD AGGREGATES & HEALTH
    # ==========================
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        with self._conn() as conn:
            total_reports = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
            pending_reports = conn.execute("SELECT COUNT(*) FROM reports WHERE status IN ('Pending', 'Submitted', 'Under Review', 'Prioritized')").fetchone()[0]
            under_cleanup = conn.execute("SELECT COUNT(*) FROM reports WHERE status IN ('Under Cleanup', 'In Progress', 'Assigned', 'Awaiting Verification')").fetchone()[0]
            cleared_reports = conn.execute("SELECT COUNT(*) FROM reports WHERE status IN ('Cleared', 'Verified Closed')").fetchone()[0]
            high_severity = conn.execute(
                """
                SELECT COUNT(*) FROM reports r
                JOIN severity_assessments s ON r.id = s.report_id
                WHERE s.severity_level = 'High' AND r.status NOT IN ('Cleared', 'Verified Closed')
                """
            ).fetchone()[0]
            total_hotspots = conn.execute("SELECT COUNT(*) FROM hotspots WHERE status = 'Active'").fetchone()[0]
            avg_priority = conn.execute("SELECT AVG(score) FROM priority_scores").fetchone()[0] or 0.0

            return {
                "total_reports": total_reports,
                "pending_reports": pending_reports,
                "under_cleanup": under_cleanup,
                "cleared_reports": cleared_reports,
                "high_severity_pending": high_severity,
                "active_hotspots": total_hotspots,
                "avg_priority_score": round(avg_priority, 1),
            }

    def get_system_health(self) -> Dict[str, Any]:
        """Returns database size, model backend status, and operational health metrics."""
        db_size_kb = 0
        if Path(DB_PATH).exists():
            db_size_kb = round(Path(DB_PATH).stat().st_size / 1024, 1)

        custom_model_exists = CUSTOM_YOLO_WEIGHTS.exists()
        base_model_exists = Path(BASE_YOLO_WEIGHTS).exists()

        with self._conn() as conn:
            user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            task_count = conn.execute("SELECT COUNT(*) FROM cleanup_tasks").fetchone()[0]
            audit_count = conn.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0]

        return {
            "db_size_kb": db_size_kb,
            "custom_yolo_weights": custom_model_exists,
            "base_yolo_weights": base_model_exists,
            "detector_backend": "YOLOv8 Nano (Pretrained COCO)" if base_model_exists else "OpenCV Saliency Fallback",
            "user_count": user_count,
            "task_count": task_count,
            "audit_count": audit_count,
            "db_status": "Healthy (WAL Mode)"
        }
