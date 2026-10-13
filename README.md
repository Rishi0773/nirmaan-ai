# NIRMAAN AI: Garbage Hotspot Prioritization

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit 1.56](https://img.shields.io/badge/Streamlit-1.56-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF.svg)](https://github.com/ultralytics/ultralytics)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.13-5C3EE8.svg?logo=opencv&logoColor=white)](https://opencv.org/)
[![Tests](https://img.shields.io/badge/Tests-27%20Passed%20(100%25)-10B981.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **Intelligent Municipal Decision-Support Platform & Academic Defense Prototype**  
> *A Computer Vision and Geospatial Platform for Prioritizing Urban Solid Waste Clearance in Greater Bengaluru.*

---

## 1. Executive Summary & Problem Statement

Traditional urban grievance redressal portals (such as municipal helpdesks) process waste accumulation complaints in a naive **First-Come-First-Served (FCFS)** sequence. Under FCFS:
- An overflowing, hazardous garbage blackspot adjacent to a hospital or school can languish for days simply because it was logged recently.
- Minor complaints involving scattered dry litter often absorb dispatch bandwidth ahead of critical public-health hazards.
- Repeat chronic accumulation points are treated as disconnected isolated events rather than chronic systemic hotspots.

**NIRMAAN AI (निर्माण)** eliminates FCFS dispatch bottlenecks by replacing chronological queues with an **explainable, multi-criteria mathematical prioritization engine**. Integrating **YOLOv8 computer vision**, **OpenCV contour coverage estimation**, and **DBSCAN spatiotemporal clustering**, NIRMAAN AI enables municipal authorities (e.g., BBMP) to deploy sanitation crews where urgency, severity, and health impact are greatest.

---

## 2. End-to-End System Pipeline

```
  [ Citizen Report & Incident Photograph ]
                     │
                     ▼
  [ YOLOv8 Multi-Class Object Detection ] ──▶ [ OpenCV Color & Contour Coverage Ratio % ]
                     │
                     ▼
  [ Severity Assessment (Low / Medium / High) ]
                     │
                     ▼
  [ SQLite Relational Storage (WAL Mode) ]
                     │
                     ▼
  [ Unsupervised DBSCAN Geospatial Clustering ] ──▶ [ Spatiotemporal Recurrence Score ]
                     │
                     ▼
  [ Multi-Criteria Mathematical Prioritization Engine ]
       Score = 0.35·Severity + 0.25·Recurrence + 0.20·Hazard + 0.20·WaitingUrgency
                     │
                     ▼
  [ Dynamic Ranked Priority Queue & Interactive Folium Map ]
                     │
                     ▼
  [ Field Crew Task Assignment & Route Optimization ]
                     │
                     ▼
  [ Before-and-After Verification (OpenCV Feature Matching) ]
                     │
                     ▼
  [ Ward Officer Review, Audit Trail Logging & Ticket Closure ]
```

---

## 3. Mathematical Prioritization Scoring Model

For every active report $i$, the composite Priority Score $P_i \in [0, 100]$ is computed as:

$$\mathbf{P_i = w_s \cdot S_i + w_r \cdot R_i + w_w \cdot W_i + w_t \cdot T_i}$$

Subject to normalized weights: $\sum w = 1.0$ (Default: $w_s=0.35, w_r=0.25, w_w=0.20, w_t=0.20$).

| Factor | Notation | Range | Description & Calculation Methodology |
|:---|:---:|:---:|:---|
| **Severity Score** | $S_i$ | $[0, 100]$ | Evaluated via YOLOv8 object count $N$ and OpenCV contour ground coverage $C\%$. Classified into Low ($\le 2$ items, $\le 15\%$), Medium, or High ($>6$ items, $>40\%$ coverage, or hazardous waste). |
| **Recurrence Score** | $R_i$ | $[0, 100]$ | Unsupervised DBSCAN density ($Eps=200\text{m}$, $MinPts=2$). Quantifies persistent blackspots where waste repeatedly accumulates within a 30-day window. |
| **Waste Type Hazard** | $W_i$ | $[0, 100]$ | Public health risk weight: `hazardous` ($95$), `organic` ($80$), `mixed_trash` ($75$), `plastic` ($60$), `glass` ($55$), `metal` ($45$), `paper` ($35$). |
| **Waiting Urgency** | $T_i$ | $[0, 100]$ | Linear aging escalation preventing starvation of older low-severity reports: $\min(100, \text{days\_pending} \times 12.5)$. |

---

## 4. Key Capabilities & Feature Set

- **Vidhana Soudha Cinematic Landing Experience**: High-contrast, responsive civic portal featuring the Bengaluru Vidhana Soudha backdrop, universal report search, primary action CTAs, and live database KPI cards.
- **Embedded NIRMAAN Civic Assistant**: Context-aware assistant providing rule-based reporting guidance, priority formula explanations, and real-time ticket tracking from the database.
- **Universal Civic Search**: Instantly query reports by alphanumeric UID (e.g., `REP-BLR-001`), municipal ward name, or locality.
- **Interactive Geospatial Hotspot Map**: Dynamic Folium mapping with MarkerCluster pins color-coded by severity, DBSCAN cluster radius buffers, and ward boundary filters.
- **Before-and-After Image Verification**: Visual verification engine using OpenCV ORB feature alignment and color-histogram differencing to authenticate cleanup claims before closing tickets.
- **Quantitative Simulation & Evaluation**: Comparative benchmark demonstrating dwell-time reduction and critical backlog clearance rates against standard FCFS scheduling.
- **Municipal Exports**: Automated generation of official BBMP-compliant PDF dispatch manifests and structured CSV dumps.
- **Simulated Role-Based Access Control (RBAC)**: Dedicated interfaces and permissions for Citizens, Field Workers, Supervisors, Ward Officers, and System Administrators.
- **Immutable Audit Trail**: Cryptographically traceable event logging for every ticket status transition, role elevation, and parameter calibration.

---

## 5. Technology Stack & Architecture

| Layer | Technologies |
|:---|:---|
| **Frontend & UI** | Streamlit 1.56, Vanilla CSS (Glassmorphic Neumorphic Design System), Google Fonts (`Space Grotesk`, `Plus Jakarta Sans`) |
| **Computer Vision** | Ultralytics YOLOv8 (`yolov8n.pt` / fine-tuned `yolov8_waste_best.pt`), OpenCV 4.13 (`cv2`), Pillow |
| **Spatial & Analytics** | Scikit-Learn (DBSCAN), NumPy (Vectorized Haversine Distance), Pandas |
| **Mapping & GIS** | Folium, `streamlit-folium`, OpenStreetMap Tiles |
| **Database & Storage** | SQLite 3 with Write-Ahead Logging (WAL) and Foreign Key Constraints |
| **Reporting & Export** | ReportLab 3.6+ (PDF generation), Pandas CSV |
| **Testing & QA** | Pytest 9.1+, AnyIO |

---

## 6. Repository Structure

```
nirmaan-ai/
├── app.py                      # Streamlit application entry point & router
├── components/                 # Reusable UI components
│   ├── navbar.py               # Professional top navigation bar
│   ├── hero.py                 # Full-viewport Vidhana Soudha hero & search
│   ├── civic_assistant.py      # Translucent NIRMAAN Civic Assistant panel
│   ├── kpi_cards.py            # Live SQLite metric summary cards
│   └── shared_ui.py            # Clean HTML tables and status badges
├── src/                        # Core system modules
│   ├── auth/rbac.py            # Role-based access control & session identities
│   ├── config.py               # Central settings, constants & directory paths
│   ├── database/               # Relational persistence layer
│   │   ├── connection.py       # SQLite connection manager with WAL mode
│   │   ├── repository.py       # Data Access Object (DAO) for all civic entities
│   │   ├── schema.sql          # Relational DDL definitions & indexes
│   │   └── seed_data.py        # Realistic Bengaluru demonstration seed script
│   ├── ml/                     # Machine learning & algorithmic pipelines
│   │   ├── detector.py         # YOLOv8 object detection & OpenCV saliency fallback
│   │   ├── clustering.py       # DBSCAN geospatial hotspot discovery
│   │   ├── priority_engine.py  # Composite multi-criteria scoring calculator
│   │   ├── verification.py     # Before-and-after image difference matching
│   │   └── evaluation.py       # NIRMAAN vs FCFS dwell-time simulator
│   └── ui/                     # Operational dashboard views
│       ├── components.py       # View headers and metric blocks
│       ├── styles.py           # Design tokens and theme injector
│       └── views/              # 12+ specialized civic operations screens
├── services/                   # Application service layer
│   ├── search_service.py       # Universal report & ward search
│   ├── assistant_service.py    # Civic assistant conversational query dispatcher
│   └── report_service.py       # Incident validation & geometry checks
├── assets/                     # Static media & styles
│   ├── images/                 # Photographs & logo assets (bengaluru_hero.jpg)
│   └── styles/custom.css       # Platform stylesheet
├── data/                       # Local SQLite database & uploaded evidence images
├── docs/                       # Project documentation & pilot proposals
│   ├── implementation-audit.md # Complete architecture audit & code review
│   ├── database-architecture.md# Schema diagrams, relations & indexes
│   ├── feature-roadmap.md      # Future capabilities & pilot roadmap
│   ├── bbmp-pilot-proposal-guide.md # Municipal deployment guidelines
│   └── model-setup-and-datasets.md  # YOLOv8 training instructions
├── tests/                      # Automated test suite (21 passing tests)
├── requirements.txt            # Python dependencies
└── README.md                   # Project overview & quickstart
```

---

## 7. Quick Start Guide

### Prerequisites
- **Python 3.10+** (Tested on Python 3.12.4 on Windows, macOS, and Linux)
- **Pip** package manager

### Step 1: Clone the Repository
```bash
git clone https://github.com/Rishi0773/nirmaan-ai.git
cd nirmaan-ai
```

### Step 2: Set Up Virtual Environment & Dependencies
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Linux/macOS:
source venv/bin/activate

# Install dependencies:
pip install -r requirements.txt
```

### Step 3: Initialize & Seed Demonstration Data
Seeds 15 realistic Bengaluru reports across Koramangala, Indiranagar, Malleshwaram, Whitefield, and Jayanagar with simulated evidence imagery and active DBSCAN hotspot clusters:
```bash
python -m src.database.seed_data
```

### Step 4: Launch the Streamlit Portal
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

### Step 5: Run Automated Test Suite
```bash
python -m pytest tests/ -v
```
*Expected result: 21 tests passed (100% pass rate).*

---

## 8. Demonstration Personas & RBAC Credentials

The system provides built-in simulation profiles. You can switch personas instantly in the **Login / Civic Operations Console**:

| Username | Full Name | Role | Assigned Ward | Capabilities & Scope |
|:---|:---|:---|:---|:---|
| `admin_blr` | Dr. Ramesh Kumar | Administrator | Central | Full platform control, priority formula weight calibration, audit trail review |
| `officer_east` | Ananya Hegde | Ward Officer | Koramangala | Incident dispatching, before/after verification approval, executive exports |
| `supervisor_01` | Manjunath K | Sanitation Supervisor | Koramangala | Crew task dispatch, fieldwork coordination, evidence submission |
| `worker_01` | Basavaraj P | Cleanup Worker | Koramangala | Field cleanup progression, after-photo upload |
| `citizen_blr` | Pooja Sharma | Citizen | Indiranagar | Public incident reporting, interactive live map exploration, report tracking |

---

## 9. Computer Vision Configuration

- **Fine-Tuned YOLOv8 Weights**: Place custom weights at `data/models/yolov8_waste_best.pt`.
- **Pretrained Fallback Mode**: If custom weights are not found, the system automatically downloads and loads standard `yolov8n.pt`.
- **Heuristic Saliency Mode**: If PyTorch/CUDA cannot run, the system uses an OpenCV color-saliency detector with connected contour bounding boxes.
- **Simulated Data Demarcation**: All synthetic database records carry `is_simulated = 1` and display a prominent verification badge in the interface.

For model training guidelines and Roboflow dataset integration, refer to [`docs/model-setup-and-datasets.md`](docs/model-setup-and-datasets.md).

---

## 10. Research Disclaimer & Academic Attribution

> **Academic Research Prototype Notice:**  
> **NIRMAAN AI** is an independent academic decision-support prototype developed for urban garbage hotspot prioritization and civic workflow optimization. This software is not an official portal of the Bruhat Bengaluru Mahanagara Palike (BBMP) or the Government of Karnataka, nor does it claim active government endorsement.

---

## 11. License

This project is licensed under the [MIT License](LICENSE). Contributions, municipal feedback, and research citations are welcome.