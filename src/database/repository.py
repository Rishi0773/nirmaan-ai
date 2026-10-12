"""
NIRMAAN AI - Data Repository
Encapsulates all database queries, transactions, and transformations.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from src.database.connection import get_connection


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

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            return dict(row) if row else None

    def create_user(self, username: str, full_name: str, role: str, email: str = "", phone: str = "", ward: str = "") -> int:
        with self._conn() as conn:
            cursor = conn.execute(
                "INSERT INTO users (username, full_name, role, email, phone, ward_assigned) VALUES (?, ?, ?, ?, ?, ?)",
                (username, full_name, role, email, phone, ward)
            )
            return cursor.lastrowid

    # ==========================
    # REPORTS
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
        created_at: Optional[str] = None
    ) -> int:
        with self._conn() as conn:
            if created_at:
                cursor = conn.execute(
                    """
                    INSERT INTO reports (
                        report_uid, latitude, longitude, address, ward_name, landmark,
                        description, waste_category, reporter_name, reporter_contact,
                        is_simulated, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (report_uid, latitude, longitude, address, ward_name, landmark,
                     description, waste_category, reporter_name, reporter_contact,
                     is_simulated, created_at, created_at)
                )
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO reports (
                        report_uid, latitude, longitude, address, ward_name, landmark,
                        description, waste_category, reporter_name, reporter_contact,
                        is_simulated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (report_uid, latitude, longitude, address, ward_name, landmark,
                     description, waste_category, reporter_name, reporter_contact, is_simulated)
                )
            return cursor.lastrowid

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

    def update_report_status(self, report_id: int, new_status: str):
        with self._conn() as conn:
            conn.execute(
                "UPDATE reports SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_status, report_id)
            )

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
    # CLEANUP TASKS & VERIFICATION
    # ==========================
    def create_task(
        self,
        task_code: str,
        report_id: int,
        assigned_team: str,
        supervisor_id: Optional[int] = None,
        priority_level: str = "Normal",
        notes: str = ""
    ) -> int:
        with self._conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO cleanup_tasks (
                    task_code, report_id, assigned_team, supervisor_id, priority_level, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (task_code, report_id, assigned_team, supervisor_id, priority_level, notes)
            )
            # Synchronize report status to Under Cleanup
            conn.execute("UPDATE reports SET status = 'Under Cleanup' WHERE id = ?", (report_id,))
            return cursor.lastrowid

    def get_all_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT t.*, r.report_uid, r.ward_name, r.address, r.waste_category,
                   s.severity_level, p.score as priority_score,
                   u.full_name as supervisor_name_full
            FROM cleanup_tasks t
            JOIN reports r ON t.report_id = r.id
            LEFT JOIN severity_assessments s ON r.id = s.report_id
            LEFT JOIN priority_scores p ON r.id = p.report_id
            LEFT JOIN users u ON t.supervisor_id = u.id
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

    def update_task_status(self, task_id: int, new_status: str, notes: str = ""):
        with self._conn() as conn:
            task = conn.execute("SELECT report_id FROM cleanup_tasks WHERE id = ?", (task_id,)).fetchone()
            if not task:
                return

            report_id = task["report_id"]
            completed_at = "CURRENT_TIMESTAMP" if new_status == "Cleared" else "NULL"
            started_at = "CURRENT_TIMESTAMP" if new_status == "Under Cleanup" else "NULL"

            conn.execute(
                f"""
                UPDATE cleanup_tasks
                SET status = ?,
                    notes = COALESCE(?, notes),
                    started_at = CASE WHEN ? = 'Under Cleanup' AND started_at IS NULL THEN CURRENT_TIMESTAMP ELSE started_at END,
                    completed_at = CASE WHEN ? = 'Cleared' THEN CURRENT_TIMESTAMP ELSE completed_at END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (new_status, notes if notes else None, new_status, new_status, task_id)
            )

            # Sync report status
            conn.execute("UPDATE reports SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_status, report_id))

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

            # Directly update task and report status within this transaction
            task = conn.execute("SELECT report_id FROM cleanup_tasks WHERE id = ?", (task_id,)).fetchone()
            if task:
                report_id = task["report_id"]
                if supervisor_decision == "Verified Clean":
                    conn.execute(
                        "UPDATE cleanup_tasks SET status = 'Cleared', notes = 'Cleanup verified by supervisor.', completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (task_id,)
                    )
                    conn.execute("UPDATE reports SET status = 'Cleared', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (report_id,))
                elif supervisor_decision == "Needs Re-cleaning":
                    conn.execute(
                        "UPDATE cleanup_tasks SET status = 'Reopened', notes = 'Verification failed. Reopened for re-cleaning.', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (task_id,)
                    )
                    conn.execute("UPDATE reports SET status = 'Reopened', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (report_id,))

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
    # DASHBOARD AGGREGATES
    # ==========================
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        with self._conn() as conn:
            total_reports = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
            pending_reports = conn.execute("SELECT COUNT(*) FROM reports WHERE status = 'Pending'").fetchone()[0]
            under_cleanup = conn.execute("SELECT COUNT(*) FROM reports WHERE status = 'Under Cleanup'").fetchone()[0]
            cleared_reports = conn.execute("SELECT COUNT(*) FROM reports WHERE status = 'Cleared'").fetchone()[0]
            high_severity = conn.execute(
                """
                SELECT COUNT(*) FROM reports r
                JOIN severity_assessments s ON r.id = s.report_id
                WHERE s.severity_level = 'High' AND r.status != 'Cleared'
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
