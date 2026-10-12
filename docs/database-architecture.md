# NIRMAAN AI: Relational Database Architecture

This document specifies the SQLite relational database schema, integrity constraints, indexing strategies, and entity relationships for **NIRMAAN AI: Garbage Hotspot Prioritization**.

---

## 1. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    users ||--o{ reports : "reports filed"
    users ||--o{ cleanup_tasks : "supervises"
    users ||--o{ cleanup_verifications : "verifies"
    users ||--o{ audit_logs : "triggers"

    reports ||--o{ report_images : "contains"
    reports ||--|| detections : "evaluated by YOLOv8"
    reports ||--|| severity_assessments : "graded by CV"
    reports ||--|| priority_scores : "scored by engine"
    reports ||--o{ cleanup_tasks : "dispatched for"
    reports ||--o{ hotspot_reports : "clustered into"

    hotspots ||--o{ hotspot_reports : "groups"

    cleanup_tasks ||--o{ cleanup_verifications : "validated by"

    users {
        int id PK
        string username UK
        string full_name
        string role
        string email
        string phone
        string ward_assigned
        timestamp created_at
    }

    reports {
        int id PK
        string report_uid UK
        float latitude
        float longitude
        string address
        string ward_name
        string landmark
        string description
        string waste_category
        string status
        string reporter_name
        string reporter_contact
        int is_simulated
        int is_flagged
        string flag_reason
        timestamp created_at
        timestamp updated_at
    }

    report_images {
        int id PK
        int report_id FK
        string image_type
        string file_path
        string annotated_path
        timestamp created_at
    }

    detections {
        int id PK
        int report_id FK,UK
        string model_version
        int total_objects
        text detected_classes_json
        text bounding_boxes_json
        float max_confidence
        float inference_time_ms
        timestamp created_at
    }

    severity_assessments {
        int id PK
        int report_id FK,UK
        string severity_level
        float severity_score
        float coverage_ratio
        text factors_json
        string assessed_by
        timestamp created_at
    }

    hotspots {
        int id PK
        string hotspot_code UK
        string ward_name
        float centroid_lat
        float centroid_lon
        float radius_meters
        int incident_count
        float recurrence_score
        float avg_severity
        string status
        timestamp created_at
        timestamp updated_at
    }

    hotspot_reports {
        int hotspot_id PK,FK
        int report_id PK,FK
    }

    priority_scores {
        int id PK
        int report_id FK,UK
        float score
        float severity_component
        float recurrence_component
        float waste_type_component
        float waiting_time_component
        int rank
        float manual_override_score
        text override_reason
        timestamp calculated_at
    }

    cleanup_tasks {
        int id PK
        string task_code UK
        int report_id FK,UK
        string assigned_team
        int supervisor_id FK
        string status
        string priority_level
        timestamp scheduled_at
        timestamp started_at
        timestamp completed_at
        text notes
        timestamp created_at
        timestamp updated_at
    }

    cleanup_verifications {
        int id PK
        int task_id FK,UK
        string before_image_path
        string after_image_path
        float waste_reduction_pct
        string ai_verdict
        string supervisor_decision
        int verified_by FK
        text verification_notes
        timestamp verified_at
    }

    notifications {
        int id PK
        string target_role
        string title
        string message
        string category
        int is_read
        string link_ref
        timestamp created_at
    }

    audit_logs {
        int id PK
        int user_id FK
        string user_name
        string action
        string entity_type
        string entity_id
        text old_value
        text new_value
        string ip_address
        timestamp created_at
    }
```

---

## 2. Integrity & Relational Architecture Rules

1. **Foreign Key Enforcement**:  
   Every database connection is initialized with:
   ```sql
   PRAGMA foreign_keys = ON;
   PRAGMA journal_mode = WAL;
   ```
2. **Cluster vs. Hotspot Independence**:  
   DBSCAN clusters generated during spatial analysis are mapped to persistent `hotspots` using `hotspot_code` (e.g. `HS-KOR-001`), ensuring that re-clustering on incoming reports updates associations via `hotspot_reports` without destabilizing historical keys.
3. **Cascading Deletions**:  
   When an incident `reports` row is deleted, related child records (`report_images`, `detections`, `severity_assessments`, `priority_scores`, `cleanup_tasks`) are safely removed via `ON DELETE CASCADE`.
4. **Immutable Audit Trail**:  
   Every status change, task reassignment, and supervisory score override generates an append-only row in `audit_logs` capturing timestamp, actor username, old value, and new value.
5. **Future PostgreSQL / PostGIS Path**:  
   Coordinate fields `latitude` and `longitude` are standardized as decimal degrees ($WGS84$, $EPSG:4326$), facilitating frictionless migration to PostgreSQL `geometry(Point, 4326)` and PostGIS spatial indexing (`ST_DWithin`).
