# NIRMAAN AI: Civic Pilot Proposal Guide & Evaluation Framework

This document outlines the operational roadmap, data prerequisites, privacy safeguards, and evaluation protocols required to transition NIRMAAN AI from an academic prototype into a controlled municipal pilot proposal for civic sanitation authorities (such as Bruhat Bengaluru Mahanagara Palike - BBMP).

---

## 1. Executive Summary & Independence Disclaimer

> **Important Regulatory Notice:**  
> NIRMAAN AI is an independent academic research prototype developed for garbage hotspot prioritization and civic workflow optimization. This software is not currently an official application of BBMP or the Government of Karnataka, nor does it claim active government endorsement. All civic references, ward names, and demonstration data are used solely for localized validation and civic demonstration purposes.

---

## 2. Municipal Problem Context

Urban local bodies face severe operational constraints in managing solid waste complaints:
1. **Inefficient First-Come-First-Served (FCFS) Dispatching**: High-density overflowing blackspots often sit pending while isolated minor litter reports are addressed first.
2. **Chronic Recurrence**: Over 40% of cleaned blackspots experience re-dumping within 72 hours due to lack of spatiotemporal hotspot tracking.
3. **Verification Bottlenecks**: Supervisors manually inspect cleanups with high travel overhead or rely on unverified phone calls, leading to premature closure of complaints.

NIRMAAN AI resolves these gaps through:
- **Vision-Driven Triage**: Automated severity grading using YOLOv8 and OpenCV contour analysis.
- **Dynamic Prioritization**: An explainable formula ranking cleanup sites by Severity, Recurrence, Waste Type, and Elapsed Waiting Time.
- **Before-and-After Verification**: Computer vision verification measuring residual waste reduction before supervisory closure.

---

## 3. Pilot Scope & Prerequisites

To execute an authorized 6-week municipal pilot within a single zone (e.g., East Zone, 2 wards):

### 3.1 Data Requirements from Civic Authority
- **Ward Boundary GeoJSON**: Official digital ward boundary polygons for geographic containment and ward-level routing.
- **Sanitation Beat Maps**: Micro-level route maps of pourakarmikas (sanitation workers) and auto-tippers.
- **Historical Grievance Dump (Anonymized)**: 6–12 months of anonymized citizen complaints from Sahaya / 1912 for historical recurrence baseline calibration.
- **Commercial & Market Zones**: Geospatial points of interest (vegetable markets, mutton stalls, construction corridors) representing high waste vulnerability.

### 3.2 Field Hardware Requirements
- **Sanitation Supervisors**: Low-cost Android smartphones with GPS and camera capabilities for before/after evidence capture.
- **Ward Command Desk**: Desktop browser access to the NIRMAAN AI dashboard for the Junior Health Inspector (JHI) or Assistant Executive Engineer (AEE).

---

## 4. Privacy Safeguards & Data Ethics

1. **Citizen Anonymization**: Citizen names, phone numbers, and exact IP addresses are stripped upon ingest. Reports only expose a pseudonymized ticket identifier.
2. **Automated Facial & License Plate Redaction**: Images captured in public streets undergo automated blurring for human faces and vehicle license plates to protect citizen privacy.
3. **Location Precision**: Citizen coordinates are snapped to road centerlines rather than pinpointing private residential doorways.
4. **Transparent Audit Logging**: Every manual status modification or priority score adjustment is logged immutably with supervisor ID and timestamp to prevent corruption.

---

## 5. Technical Migration from Prototype to Municipal Scale

| Component | College MVP (Current) | Production Municipal Pilot |
|:---|:---|:---|
| **Database** | SQLite 3 | PostgreSQL 16 + PostGIS extension |
| **Spatial Indexing** | Scikit-learn DBSCAN (Memory) | PostGIS `ST_DWithin` and R-Tree GiST indices |
| **API Layer** | Streamlit Python Application | FastAPI async microservices + Streamlit Admin Desk |
| **Object Storage** | Local File System (`data/uploads`) | AWS S3 / MinIO / S3-compatible MeitY cloud |
| **Authentication** | Session-based Role RBAC | OAuth2 / Keycloak with Aadhaar/Gov SSO |
| **Mobile Access** | Mobile Browser (Responsive Streamlit) | Offline-capable Flutter / PWA Field App |

---

## 6. Pilot Key Performance Indicators (KPIs)

The municipal pilot will measure success against three empirical benchmarks:

1. **Reduction in High-Severity Blackspot Dwell Time**:
   - *Target*: 35% reduction in average hours taken to clear High-severity waste sites compared to historical FCFS baseline.
2. **Chronic Recurrence Prevention**:
   - *Target*: Identification of top 15 chronic dumping blackspots within 14 days, enabling targeted civic intervention (CCTV installation, rangoli painting, community composting).
3. **Verification Accuracy**:
   - *Target*: 90%+ agreement between NIRMAAN AI Before-and-After reduction confidence and senior health inspector physical audit.
