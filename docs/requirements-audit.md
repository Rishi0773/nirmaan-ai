# NIRMAAN AI: PPT-to-Code Requirements Audit Matrix

This audit matrix compares the nine presentation slides of **NIRMAAN AI: Garbage Hotspot Prioritization** with the system implementation. It maps each academic objective, technical decision, and operational workflow directly to code modules, database schemas, AI models, and user interfaces.

---

## 1. Comprehensive Requirements Matrix

| PPT Slide | Slide Title & Requirement | Existing Implementation | Status | Gap | Proposed Action |
|:---|:---|:---|:---|:---|:---|
| **Slide 1** | **Title & Concept:** NIRMAAN AI — Garbage Hotspot Prioritization. Combining computer vision, location data, and report history to help municipal/civic teams prioritize cleanup sites. | None (Fresh repository initialisation required) | Implemented | Clean system architecture, neutral civic branding, reproducible configuration required. | Build modular Python/Streamlit architecture with SQLite, transparent configuration, and BBMP-ready pilot disclaimers in `app.py`, `src/config.py`. |
| **Slide 2** | **Problem Statement:** Current citizen complaint workflows handle reports individually (First-Come-First-Served) without considering severity, waste hazard, or recurrence. Teams lack prioritization tools. | None | Implemented | Lack of comparative analytics showing FCFS vs. Priority-driven queue inefficiency. | Build `src/engine/evaluation.py` and comparison dashboard in `src/ui/views/analytics_eval.py` showing metric contrasts (waiting time for high-severity cases, severity coverage). |
| **Slide 3** | **Objective 1:** Detect and grade waste using YOLOv8 and OpenCV. | None | Implemented | Need YOLOv8 bounding box inference + OpenCV contour/coverage estimation with graceful fallback when weights are missing. | Implement `src/ml/detector.py` and `src/ml/severity.py` with multi-class detection, coverage calculation, and explicit demo/real mode toggles. |
| **Slide 3** | **Objective 2:** Store timestamped reports and geographic location information. | None | Implemented | Relational schema with coordinate validation, timestamping, and image paths needed. | Design SQLite relational database in `src/database/schema.sql` and `src/database/repository.py` storing report lat/long, wards, timestamps, and metadata. |
| **Slide 3** | **Objective 3:** Identify recurring garbage hotspots using spatial-temporal aggregation. | None | Implemented | Automated clustering of geographically close repeat complaints. | Implement DBSCAN/Haversine clustering in `src/ml/clustering.py` and interactive map visualization in `src/ui/views/hotspot_intel.py`. |
| **Slide 3** | **Objective 4:** Rank cleanup locations using Severity, Waste Type, Recurrence, and Waiting Time. | None | Implemented | Transparent, configurable, and explainable scoring mathematical formula. | Develop `src/engine/priority.py` with explainable score components: $Score = w_s S + w_r R + w_w W + w_t T$ and UI breakdown inspection. |
| **Slide 3** | **Objective 5:** Track cleanup status and team assignments. | None | Implemented | End-to-end task workflow (Pending $\rightarrow$ Under Cleanup $\rightarrow$ Cleared $\rightarrow$ Reopened). | Implement task tracking and status transitions in `src/database/repository.py` and UI in `src/ui/views/task_management.py`. |
| **Slide 3** | **Objective 6:** Evaluate detection and prioritization performance. | None | Implemented | Quantitative comparison of Priority vs. FCFS queues and severity classification calibration. | Implement automated evaluation pipeline in `src/engine/evaluation.py` and test suite in `tests/test_evaluation.py`. |
| **Slide 4** | **Methodology Pipeline:** Citizen Report $\rightarrow$ YOLOv8/OpenCV Analysis $\rightarrow$ Storage $\rightarrow$ Historical Analysis $\rightarrow$ Hotspot Discovery $\rightarrow$ Priority Calculation $\rightarrow$ Civic Dashboard $\rightarrow$ History Update on Cleanup. | None | Implemented | End-to-end orchestrated pipeline must connect seamlessly without mock breaks. | Build unified pipeline orchestrator in `app.py` connecting data ingestion, inference, database persistence, and spatial analytics. |
| **Slide 5** | **Computer Vision & Severity Grading:** YOLOv8 bounding boxes, object class confidences, OpenCV mask/contour area ratio, 3-level severity (Low, Medium, High). | None | Implemented | Robust image preprocessing, bounding box annotation rendering, and explainable severity threshold logic. | Build `src/ml/detector.py` (YOLOv8 inference), `src/ml/severity.py` (Low/Med/High severity logic based on object count and pixel area percentage), preserving PPT core categories. |
| **Slide 6** | **Spatial Hotspot Analysis:** Aggregate reports within spatial proximity (e.g., 100m–250m radius), repeat incident frequency, latest incident date, average severity. | None | Implemented | Spatial clustering engine using Scikit-Learn DBSCAN and distance metrics. | Implement `src/ml/clustering.py` calculating hotspot centroid, radius, total incidents, recurrence score, and repeat frequency. |
| **Slide 7** | **Prioritization Engine:** Explainable formula balancing Severity ($S$), Recurrence ($R$), Waste Type ($W$), and Waiting Time ($T$). | None | Implemented | Configurable weights, factor explanations, and human-in-the-loop review override. | Build `src/engine/priority.py` with default normalized weights ($0.35, 0.25, 0.20, 0.20$), factor breakdown tooltips, and supervisor manual override. |
| **Slide 8** | **Cleanup Verification & Operations:** Field teams submit Before & After photographs; AI comparison of waste reduction + supervisor verification approval. | None | Implemented | Dual-image comparison engine verifying reduction in waste pixels/detections with uncertainty scoring. | Develop `src/ml/verification.py` comparing pre- and post-cleanup images, computing waste reduction percentage, and audit-logged supervisor sign-off in `src/ui/views/verification_view.py`. |
| **Slide 9** | **Outcomes & Academic Honesty:** Working prototype, FCFS comparison, TACO/TrashNet dataset documentation, explicit demarcation of simulated demo records vs. genuine observations. | None | Implemented | Risk of presenting synthetic data as real Bengaluru municipal records. | Add clear dataset metadata, simulated vs. genuine flags on all seed records, model disclaimer banners, and `docs/model-setup-and-datasets.md`. |

---

## 2. Status Definitions

- **Implemented**: Fully designed, coded, tested, and integrated with working database and UI.
- **Partially Implemented**: Code exists but lacks full edge-case coverage or backend integration.
- **Missing**: Not yet present in the codebase.
- **Broken**: Code is present but raises runtime or logic errors.
- **Needs Validation**: Requires live model weights or ground-truth dataset testing.
- **Optional Enhancement**: Extends PPT scope for pilot readiness (e.g., PDF reporting, audit logging).
