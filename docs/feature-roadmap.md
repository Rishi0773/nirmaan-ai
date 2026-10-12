# NIRMAAN AI: Feature Roadmap & Upgrade Specifications

This document outlines the phased development roadmap for **NIRMAAN AI: Garbage Hotspot Prioritization**, detailing current capabilities, the UI redesign upgrade, and municipal BBMP pilot scaling milestones.

---

## 1. P0 — Academic MVP & Reference UI Redesign (Current Release)

1. **Reference Landing Page & Layout (Completed)**
   - Dark navy translucent top navigation bar with full-width glassmorphism.
   - Hero banner with headline, eyebrow tag, sub-headline, search bar, and primary/secondary CTA buttons.
   - Configurable `assets/images/bengaluru_hero.jpg` background with fallback dark navy gradient.
   - Floating interactive **NIRMAAN Civic Assistant** panel with live report tracking, priority formula guidance, and map navigation.
   - Bottom live KPI strip displaying 5 translucent cards connected to real database counts.

2. **Core Pipeline & Computer Vision (Preserved & Verified)**
   - YOLOv8 multi-class waste detection (plastic, organic, paper, metal, glass, hazardous, mixed trash).
   - OpenCV contour segmentation and ground coverage ratio calculation.
   - Three-tier severity grading: Low, Medium, High.
   - Seamless fallback when weights are absent (`yolov8n.pt` / OpenCV color saliency).

3. **Geospatial Hotspot Analysis & DBSCAN (Preserved)**
   - Unsupervised DBSCAN spatial clustering with 200m buffer and Haversine distance metric.
   - Interactive Folium map with clustering, heatmaps, and ward boundaries.
   - Hotspot metrics: incident count, recurrence score, average severity, latest incident date.

4. **Transparent Mathematical Prioritization Engine (Preserved)**
   - Scoring formula: $\text{Priority} = 0.35S + 0.25R + 0.20W + 0.20T$.
   - Explainable breakdown displaying individual component contributions.
   - Ranked cleanup queue with supervisory manual score override and civic audit logging.

5. **Operational Task Workflow & Verification (Preserved)**
   - Ticket lifecycle: `Pending` $\rightarrow$ `Under Cleanup` $\rightarrow$ `Cleared` $\rightarrow$ `Reopened`.
   - Dual-image Before-and-After submission.
   - Automated AI reduction percentage calculation and supervisor sign-off.

6. **FCFS vs. Priority Evaluation (Preserved)**
   - Discrete-event simulation comparing NIRMAAN Priority Queue against standard First-Come-First-Served dispatching.
   - Metrics: high-severity wait latency, critical waste containment time, severity-weighted coverage.

7. **Defect Repairs & Hygiene**
   - Fixed raw HTML table rendering defect across Dashboard and Priority Queue by eliminating 4-space markdown indentations.
   - Repaired broken chart card containers.
   - Connected universal search bar to SQLite backend.

---

## 2. P1 — Operational Enhancements (College Demonstration & Presentation)

1. **Role-Based Access Control (RBAC)**
   - Roles: `Administrator`, `Ward Officer`, `Sanitation Supervisor`, `Cleanup Worker`, and `Citizen`.
   - Role switcher widget in top navigation bar and settings view.

2. **Municipal Exports & Dossier Generation**
   - Dynamic PDF generation via ReportLab with civic branding.
   - Filter-based CSV report downloads.

3. **In-App Notification Center & Audit Trail**
   - Unread alerts counter badge in navigation header.
   - Immutable audit trail capturing all supervisory overrides and task status updates.

---

## 3. P2 — Municipal BBMP Pilot Scale (Future Horizon)

1. **PostgreSQL + PostGIS Migration**
   - Transition SQLite relational storage to PostgreSQL with spatial indexing (`ST_DWithin`, spatial queries across millions of rows).
2. **Citizen WhatsApp & Mobile Ingestion**
   - Webhook endpoint for geo-tagged image uploads via citizen chatbots.
3. **Automated Route Optimization (VRP)**
   - Multi-vehicle capacitated routing using Google OR-Tools for municipal compactor truck fleets.
