# NIRMAAN AI: Implementation Audit & Architecture Review

**Date:** October 2026  
**Auditor:** Senior Software Engineer & System Architect  
**Project:** NIRMAAN AI — Garbage Hotspot Prioritization (Civic Decision-Support Platform)

---

## 1. Executive Summary

An exhaustive technical audit of the **NIRMAAN AI** codebase was conducted to evaluate existing capabilities, identify visual and functional defects, assess relational database integrity, and plan the complete UI redesign based on the reference civic portal design.

The core computational logic (YOLOv8 inference, OpenCV saliency/contour coverage, DBSCAN spatial clustering, composite priority formula $0.35S + 0.25R + 0.20W + 0.20T$, and FCFS simulation evaluation) is structurally sound with **16 passing unit tests**. However, the presentation layer suffered from raw HTML tag leakage, missing top-level navigation, rigid sidebar-only routing, lack of hero landing components, and absence of an interactive civic assistant.

---

## 2. Inventory of Existing Modules & Health Check

| Module / Layer | Path | Existing Health | Findings & Required Actions |
|:---|:---|:---|:---|
| **Entry Point** | `app.py` | Working | Relies on sidebar radio navigation; needs full integration with top translucent navbar, hero view, and floating assistant while retaining all 15 operational views. |
| **Relational Database** | `src/database/schema.sql`, `connection.py`, `repository.py` | Good | 12 tables with foreign keys and WAL mode. Needs explicit index optimization, transaction safety verification, and a comprehensive Mermaid ER diagram in `docs/database-architecture.md`. |
| **Computer Vision** | `src/ml/detector.py`, `severity.py`, `verification.py` | Working | Fallback mode supported; verified on synthetic images. Ensure model versioning and clear reporting of inference status. |
| **Spatial Clustering** | `src/ml/clustering.py`, `recurrence.py` | Working | Scikit-learn DBSCAN with Haversine distance. Ensure cluster IDs are dynamic and do not collide with permanent hotspot tracking codes. |
| **Priority Engine** | `src/engine/priority.py`, `evaluation.py` | Working | Formula $Score = 0.35S + 0.25R + 0.20W + 0.20T$ matches PPT Slide 7. Explanations need clear breakdown pills. |
| **UI Views** | `src/ui/views/` (15 views) | Mixed | **Defect found:** Markdown parser treats 4+ space indented HTML strings as `<pre><code>` raw text, displaying literal `<tr><td>` tags on the dashboard and queue tables. Unclosed container tags also cause layout glitches. |
| **Styling** | `src/ui/styles.py` | Outdated | Light grey neumorphic theme lacks the rich dark navy glassmorphism and emerald/teal accents of the civic reference design. |
| **Test Suite** | `tests/` (8 test files) | 16/16 Passed | Passes cleanly. Needs regression tests covering HTML rendering, new search service, civic assistant query resolution, and KPI calculations. |

---

## 3. Detailed Defect Analysis & Root Causes

### Defect 1: Raw HTML Table Tags Displayed as Text on Dashboard & Priority Queue
- **Root Cause:** In `src/ui/views/dashboard.py` and `src/ui/views/priority_queue.py`, multi-line HTML strings were written with 8 to 16 spaces of indentation inside Python function blocks. In CommonMark (the Markdown standard used by Streamlit), any line indented by 4 or more spaces is parsed as an indented code block (`<pre><code>`). Consequently, the browser received escaped HTML strings instead of table DOM elements.
- **Remedy:** Format HTML strings with `textwrap.dedent` or zero leading markdown indentation, and utilize Streamlit 1.30+ `st.html()` or clean, sanitized HTML containers.

### Defect 2: Broken / Missing Top Navigation
- **Root Cause:** Streamlit sidebar was the sole navigation mechanism. The user reference screenshot requires a top-level translucent dark navy navbar (`NIRMAAN AI`, Home, Report Garbage, Live Map, Track Report, Hotspots, Analytics, About, User Profile/Login).
- **Remedy:** Create `components/navbar.py` with responsive navigation state synchronization via `st.session_state["active_page"]`, bridging top navbar actions with existing sidebar workflows.

### Defect 3: Missing Reference Hero & Civic Assistant
- **Root Cause:** The landing view was previously a simple presentation summary without the Vidhana Soudha / Bengaluru hero backdrop, headline typography, search bar, and interactive floating assistant.
- **Remedy:** Build `components/hero.py` (with configurable `assets/images/bengaluru_hero.jpg` and dark navy gradient fallback), `components/civic_assistant.py` (with rule-based database query integration, FAQs, and ticket tracking), and `components/kpi_cards.py`.

### Defect 4: Search Input Disconnected from Backend
- **Root Cause:** The search field in the reference design was not implemented in code.
- **Remedy:** Implement `services/search_service.py` supporting search across report UIDs (`REP-BLR-...`), ward names (`Koramangala`, `Indiranagar`), addresses, and categories with automatic redirection to the Incident Dossier or Map.

---

## 4. Planned Architecture & Upgrades

```
NIRMAAN/
├── app.py                      # Main entry point with Navbar & Page Router
├── .streamlit/
│   └── config.toml             # Theme settings (Navy & Emerald palette)
├── assets/
│   ├── README.md               # Asset placement guidelines
│   ├── images/
│   │   └── README.md           # Instructions for hero & logo assets
│   └── styles/
│       ├── README.md           # CSS documentation
│       └── custom.css          # Glassmorphic, dark navy, and emerald CSS
├── components/
│   ├── __init__.py
│   ├── navbar.py               # Dark navy translucent navbar with navigation state
│   ├── hero.py                 # Hero section with headline, search, and CTA
│   ├── civic_assistant.py      # Floating civic chatbot with real SQLite queries
│   ├── kpi_cards.py            # Live database KPI metrics strip
│   └── shared_ui.py            # Clean badges, cards, and modal helpers
├── services/
│   ├── __init__.py
│   ├── report_service.py       # Incident validation & reporting pipeline
│   ├── search_service.py       # UID, ward, and keyword search service
│   └── assistant_service.py    # Query answering & database intent resolution
├── src/                        # Preserved core modules (database, ml, engine, auth, ui)
├── tests/                      # Pytest suite (existing 16 + new regression tests)
└── docs/                       # Implementation audit, architecture, roadmap
```

---

## 5. Non-Regressive Commitments
1. **Zero Data Loss:** `data/nirmaan.db` and all 15 simulated seed records are preserved.
2. **All 15 Views Retained:** Every existing view remains fully functional and accessible.
3. **No React Migration:** Pure Python & Streamlit implementation ensuring high performance and simple deployment.
4. **Graceful Asset Fallback:** If `assets/images/bengaluru_hero.jpg` is not present, a dark navy gradient is rendered without broken image artifacts.
