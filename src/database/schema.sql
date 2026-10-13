-- NIRMAAN AI Relational SQLite Schema
-- Civic Decision-Support Platform for Garbage Hotspot Prioritization

PRAGMA foreign_keys = ON;

-- 1. Users & Civic Officers
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Administrator', 'Ward Officer', 'Sanitation Supervisor', 'Cleanup Worker', 'Citizen')),
    email TEXT,
    phone TEXT,
    ward_assigned TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Incident Reports
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_uid TEXT UNIQUE NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    address TEXT,
    ward_name TEXT NOT NULL,
    landmark TEXT,
    description TEXT,
    waste_category TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN (
        'Pending', 'Submitted', 'Under Review', 'Prioritized', 'Assigned',
        'In Progress', 'Under Cleanup', 'Awaiting Verification', 'Cleared',
        'Verified Closed', 'Blocked', 'Rejected', 'Duplicate', 'Reopened'
    )),
    reporter_name TEXT DEFAULT 'Anonymous Citizen',
    reporter_contact TEXT,
    citizen_id INTEGER,
    duplicate_of_id INTEGER,
    rejection_reason TEXT,
    blocked_reason TEXT,
    escalated INTEGER DEFAULT 0,
    escalation_notes TEXT,
    is_simulated INTEGER DEFAULT 0,
    is_flagged INTEGER DEFAULT 0,
    flag_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(citizen_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY(duplicate_of_id) REFERENCES reports(id) ON DELETE SET NULL
);

-- 3. Report Image Records
CREATE TABLE IF NOT EXISTS report_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    image_type TEXT NOT NULL CHECK(image_type IN ('incident', 'before_cleanup', 'after_cleanup')),
    file_path TEXT NOT NULL,
    annotated_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
);

-- 4. Computer Vision Detections (YOLOv8)
CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL UNIQUE,
    model_version TEXT NOT NULL,
    total_objects INTEGER NOT NULL DEFAULT 0,
    detected_classes_json TEXT NOT NULL DEFAULT '{}',
    bounding_boxes_json TEXT NOT NULL DEFAULT '[]',
    max_confidence REAL DEFAULT 0.0,
    inference_time_ms REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
);

-- 5. Severity Assessments (YOLOv8 + OpenCV Coverage)
CREATE TABLE IF NOT EXISTS severity_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL UNIQUE,
    severity_level TEXT NOT NULL CHECK(severity_level IN ('Low', 'Medium', 'High')),
    severity_score REAL NOT NULL CHECK(severity_score >= 0 AND severity_score <= 100),
    coverage_ratio REAL NOT NULL DEFAULT 0.0,
    factors_json TEXT NOT NULL DEFAULT '{}',
    assessed_by TEXT DEFAULT 'AI Engine',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
);

-- 6. Spatial Hotspot Clusters
CREATE TABLE IF NOT EXISTS hotspots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotspot_code TEXT UNIQUE NOT NULL,
    ward_name TEXT NOT NULL,
    centroid_lat REAL NOT NULL,
    centroid_lon REAL NOT NULL,
    radius_meters REAL NOT NULL DEFAULT 200.0,
    incident_count INTEGER NOT NULL DEFAULT 1,
    recurrence_score REAL NOT NULL DEFAULT 0.0,
    avg_severity REAL NOT NULL DEFAULT 0.0,
    status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Monitoring', 'Resolved')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Hotspot to Reports Association (Many-to-Many)
CREATE TABLE IF NOT EXISTS hotspot_reports (
    hotspot_id INTEGER NOT NULL,
    report_id INTEGER NOT NULL,
    PRIMARY KEY(hotspot_id, report_id),
    FOREIGN KEY(hotspot_id) REFERENCES hotspots(id) ON DELETE CASCADE,
    FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
);

-- 8. Transparent Priority Scores
CREATE TABLE IF NOT EXISTS priority_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL UNIQUE,
    score REAL NOT NULL CHECK(score >= 0 AND score <= 100),
    severity_component REAL NOT NULL,
    recurrence_component REAL NOT NULL,
    waste_type_component REAL NOT NULL,
    waiting_time_component REAL NOT NULL,
    rank INTEGER DEFAULT 0,
    manual_override_score REAL,
    override_reason TEXT,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
);

-- 9. Operations Cleanup Tasks
CREATE TABLE IF NOT EXISTS cleanup_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_code TEXT UNIQUE NOT NULL,
    report_id INTEGER NOT NULL UNIQUE,
    assigned_team TEXT NOT NULL,
    supervisor_id INTEGER,
    worker_id INTEGER,
    status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN (
        'Pending', 'Assigned', 'In Progress', 'Under Cleanup', 'Blocked',
        'Awaiting Verification', 'Cleared', 'Verified Closed', 'Reopened'
    )),
    priority_level TEXT DEFAULT 'Normal',
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    notes TEXT,
    worker_notes TEXT,
    blocked_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE,
    FOREIGN KEY(supervisor_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY(worker_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 10. Cleanup Verification Evidence
CREATE TABLE IF NOT EXISTS cleanup_verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL UNIQUE,
    before_image_path TEXT NOT NULL,
    after_image_path TEXT NOT NULL,
    waste_reduction_pct REAL NOT NULL DEFAULT 0.0,
    ai_verdict TEXT NOT NULL CHECK(ai_verdict IN ('Approved', 'Uncertain', 'Rejected')),
    supervisor_decision TEXT NOT NULL CHECK(supervisor_decision IN ('Verified Clean', 'Needs Re-cleaning', 'Pending Review')),
    verified_by INTEGER,
    verification_notes TEXT,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES cleanup_tasks(id) ON DELETE CASCADE,
    FOREIGN KEY(verified_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 11. In-App Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_role TEXT,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('Priority Alert', 'Task Assignment', 'Verification', 'System')),
    is_read INTEGER DEFAULT 0,
    link_ref TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. Immutable Civic Audit Log
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    user_name TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    ip_address TEXT DEFAULT '127.0.0.1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. Report Status Change History (Audit & Timeline Tracking)
CREATE TABLE IF NOT EXISTS report_status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    old_status TEXT,
    new_status TEXT NOT NULL,
    changed_by_user_id INTEGER,
    changed_by_name TEXT,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE,
    FOREIGN KEY(changed_by_user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 14. Citizen Follow-up Notes (Add info without duplicate reports)
CREATE TABLE IF NOT EXISTS report_followups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    user_id INTEGER,
    user_name TEXT,
    notes TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes for performance & query speed
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_ward ON reports(ward_name);
CREATE INDEX IF NOT EXISTS idx_reports_uid ON reports(report_uid);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON cleanup_tasks(status);
CREATE INDEX IF NOT EXISTS idx_status_history_report ON report_status_history(report_id);
